#!/usr/bin/env python3
# toot downloader version two!!
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import argparse
import functions
import json
import re
import requests
import signal
import sqlite3
import sys
from mastodon import Mastodon, MastodonUnauthorizedError

parser = argparse.ArgumentParser(description="Log in and download posts.")
parser.add_argument(
    "-c",
    "--cfg",
    dest="cfg",
    default="config.json",
    nargs="?",
    help="Specify a custom location for config.json.",
)

args = parser.parse_args()

scopes = [
    "read:statuses",
    "read:accounts",
    "read:follows",
    "write:statuses",
    "read:notifications",
    "write:accounts",
]
# cfg defaults

cfg = {
    "site": "https://iscurrently.live",
    "cw": None,
    "cw_reply": False,
    "instance_blacklist": ["bofa.lol", "witches.town", "knzk.me"],  # rest in piece
    "learn_from_cw": False,
    "mention_handling": 1,
    "max_thread_length": 15,
    "strip_paired_punctuation": False,
    "limit_length": False,
    "length_lower_limit": 5,
    "length_upper_limit": 50,
    "overlap_ratio_enabled": False,
    "overlap_ratio": 0.7,
}

try:
    cfg.update(json.load(open(args.cfg, "r")))
except FileNotFoundError:
    open(args.cfg, "w").write("{}")

print("Using {} as configuration file".format(args.cfg))

if not cfg["site"].startswith("https://") and not cfg["site"].startswith("http://"):
    print(
        "Site must begin with 'https://' or 'http://'. Value '{}' is invalid - try 'https://{}' instead.".format(
            cfg["site"]
        )
    )
    sys.exit(1)

if "client" not in cfg:
    print("No application info -- registering application with {}".format(cfg["site"]))
    client_id, client_secret = Mastodon.create_app(
        "mstdn-ebooks",
        api_base_url=cfg["site"],
        scopes=scopes,
        website="https://github.com/Lynnesbian/mstdn-ebooks",
    )

    cfg["client"] = {"id": client_id, "secret": client_secret}

if "secret" not in cfg:
    print("No user credentials -- logging in to {}".format(cfg["site"]))
    client = Mastodon(
        client_id=cfg["client"]["id"],
        client_secret=cfg["client"]["secret"],
        api_base_url=cfg["site"],
    )

    print(
        "Open this URL and authenticate to give mstdn-ebooks access to your bot's account: {}".format(
            client.auth_request_url(scopes=scopes)
        )
    )
    cfg["secret"] = client.log_in(code=input("Secret: "), scopes=scopes)

json.dump(cfg, open(args.cfg, "w+"))


def extract_toot(toot):
    toot = functions.extract_toot(toot)
    toot = toot.replace(
        "@", "@\u200B"
    )  # put a zws between @ and username to avoid mentioning
    return toot


client = Mastodon(
    client_id=cfg["client"]["id"],
    client_secret=cfg["client"]["secret"],
    access_token=cfg["secret"],
    api_base_url=cfg["site"],
)

try:
    me = client.account_verify_credentials()
except MastodonUnauthorizedError:
    print(
        "The provided access token in {} is invalid. Please delete {} and run main.py again.".format(
            args.cfg, args.cfg
        )
    )
    sys.exit(1)

# following = client.account_following(me.id)
following = [{"id": "109314173860767899", "acct": "theresnotime"}]

db = sqlite3.connect("toots.db")
db.text_factory = str
c = db.cursor()
c.execute(
    "CREATE TABLE IF NOT EXISTS `toots` (sortid INTEGER UNIQUE PRIMARY KEY AUTOINCREMENT, id VARCHAR NOT NULL, cw INT NOT NULL DEFAULT 0, userid VARCHAR NOT NULL, uri VARCHAR NOT NULL, content VARCHAR NOT NULL)"
)
c.execute(
    "CREATE TRIGGER IF NOT EXISTS `dedup` AFTER INSERT ON toots FOR EACH ROW BEGIN DELETE FROM toots WHERE rowid NOT IN (SELECT MIN(sortid) FROM toots GROUP BY uri ); END; "
)
db.commit()

tableinfo = c.execute("PRAGMA table_info(`toots`)").fetchall()
found = False
columns = []
for entry in tableinfo:
    if entry[1] == "sortid":
        found = True
        break
    columns.append(entry[1])

if not found:
    print("Migrating to new database format. Please wait...")
    print(
        "WARNING: If any of the accounts your bot is following are Pleroma users, please delete toots.db and run main.py again to create it anew."
    )
    try:
        c.execute("DROP TABLE `toots_temp`")
    except:
        pass

    c.execute(
        "CREATE TABLE `toots_temp` (sortid INTEGER UNIQUE PRIMARY KEY AUTOINCREMENT, id VARCHAR NOT NULL, cw INT NOT NULL DEFAULT 0, userid VARCHAR NOT NULL, uri VARCHAR NOT NULL, content VARCHAR NOT NULL)"
    )
    for f in following:
        user_toots = c.execute(
            "SELECT * FROM `toots` WHERE userid LIKE ? ORDER BY id", (f["id"],)
        ).fetchall()
        if user_toots is None:
            continue

        if columns[-1] == "cw":
            for toot in user_toots:
                c.execute(
                    "INSERT INTO `toots_temp` (id, userid, uri, content, cw) VALUES (?, ?, ?, ?, ?)",
                    toot,
                )
        else:
            for toot in user_toots:
                c.execute(
                    "INSERT INTO `toots_temp` (id, cw, userid, uri, content) VALUES (?, ?, ?, ?, ?)",
                    toot,
                )

    c.execute("DROP TABLE `toots`")
    c.execute("ALTER TABLE `toots_temp` RENAME TO `toots`")
    c.execute(
        "CREATE TRIGGER IF NOT EXISTS `dedup` AFTER INSERT ON toots FOR EACH ROW BEGIN DELETE FROM toots WHERE rowid NOT IN (SELECT MIN(sortid) FROM toots GROUP BY uri ); END; "
    )

db.commit()


def handleCtrlC(signal, frame):
    print("\nPREMATURE EVACUATION - Saving chunks")
    db.commit()
    sys.exit(1)


signal.signal(signal.SIGINT, handleCtrlC)

patterns = {
    "handle": re.compile(r"^.*@(.+)"),
    "url": re.compile(r"https?:\/\/(.*)"),
    "uri": re.compile(r'template="([^"]+)"'),
    "pid": re.compile(r"[^\/]+$"),
}


def insert_toot(post, acc, content, cursor):  # extracted to prevent duplication
    cursor.execute(
        "REPLACE INTO toots (id, cw, userid, uri, content) VALUES (?, ?, ?, ?, ?)",
        (
            post["id"],
            1
            if (post["spoiler_text"] is not None and post["spoiler_text"] != "")
            else 0,
            acc["id"],
            post["uri"],
            content,
        ),
    )


for f in following:
    last_toot = c.execute(
        "SELECT id FROM `toots` WHERE userid LIKE ? ORDER BY sortid DESC LIMIT 1",
        (f["id"],),
    ).fetchone()
    if last_toot is not None:
        last_toot = last_toot[0]
    else:
        last_toot = 0
    print(
        "Downloading posts for user @{}, starting from {}".format(f["acct"], last_toot)
    )

    # find the user's activitypub outbox
    print("WebFingering...")
    instance = patterns["handle"].search(f["acct"])
    if instance is None:
        instance = patterns["url"].search(cfg["site"]).group(1)
    else:
        instance = instance.group(1)

    if instance in cfg["instance_blacklist"]:
        print("skipping blacklisted instance: {}".format(instance))
        continue

    try:
        # download first 20 toots since last toot
        posts = client.account_statuses(f["id"], min_id=last_toot)
    except:
        print(
            "oopsy woopsy!! we made a fucky wucky!!!\n(we're probably rate limited, please hang up and try again)"
        )
        sys.exit(1)

    print("Downloading and saving posts", end="", flush=True)
    done = False
    try:
        while not done and len(posts) > 0:
            for post in posts:
                if post["reblog"] is not None:
                    continue  # this isn't a toot/post/status/whatever, it's a boost or a follow or some other activitypub thing. ignore

                # its a toost baby
                content = post["content"]
                toot = extract_toot(content)
                # print(toot)
                try:
                    if (
                        c.execute(
                            "SELECT COUNT(*) FROM toots WHERE uri LIKE ?", (post["id"],)
                        ).fetchone()[0]
                        > 0
                    ):
                        # we've caught up to the notices we've already downloaded, so we can stop now
                        # you might be wondering, "lynne, what if the instance ratelimits you after 40 posts, and they've made 60 since main.py was last run? wouldn't the bot miss 20 posts and never be able to see them?" to which i reply, "i know but i don't know how to fix it"
                        done = True
                    if "lang" in cfg:
                        try:
                            if post["language"] == cfg["lang"]:  # filter for language
                                insert_toot(post, f, toot, c)
                        except KeyError:
                            # JSON doesn't have language, just insert the toot irregardlessly
                            insert_toot(post, f, toot, c)
                    else:
                        insert_toot(post, f, toot, c)

                    pass
                except:
                    pass  # ignore any toots that don't successfully go into the DB

            # get the next <20 posts
            try:
                posts = client.account_statuses(f["id"], min_id=posts[0]["id"])
            except requests.Timeout:
                print("HTTP timeout, site did not respond within 15 seconds")
            except KeyError:
                print("Couldn't get next page - we've probably got all the posts")
            except:
                print("An error occurred while trying to obtain more posts.")

            print(".", end="", flush=True)
        print(" Done!")
        db.commit()
    except requests.HTTPError as e:
        if e.response.status_code == 429:
            print(
                "Rate limit exceeded. This means we're downloading too many posts in quick succession. Saving toots to database and moving to next followed account."
            )
            db.commit()
        else:
            # TODO: remove duplicate code
            print(
                "Encountered an error! Saving posts to database and moving to next followed account."
            )
            db.commit()
    except:
        print(
            "Encountered an error! Saving posts to database and moving to next followed account."
        )
        db.commit()

print("Done!")

db.commit()
db.execute("VACUUM")  # compact db
db.commit()
db.close()
