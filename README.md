# mstdn-ebooks
**Lynnear Edition**

This version makes quite a few changes from [the original](https://github.com/Jess3Jane/mastodon-ebooks), such as:
- Unicode support
- Non-Markov stuff
- Stores toots in a sqlite database rather than a text file
  - Doesn't unnecessarily redownload all toots every time

## FediBooks
Before you use mstdn-ebooks to create your own ebooks bot, I recommend checking out [FediBooks](https://fedibooks.com). Compared to mstdn-ebooks, FediBooks offers a few advantages:
- Hosted and maintained by someone else - you don't have to worry about updating, keeping the computer on, etc
- No installation required
- A nice UI for managing your bot(s)
- Easy configuration

However, there are still a few reasons you might want to use mstdn-ebooks instead:
- Your data stays local to your machine
- More customisation potential - you can edit mstdn-ebooks to add functionality
- Replying more (in)frequently than FediBooks allows

Like mstdn-ebooks, FediBooks is free, both as in free of charge and free to modify, self-host, and more.

## Secure Fetch
Secure fetch (aka authorised fetches, authenticated fetches, secure mode...) is *not* supported by mstdn-ebooks, and will fail to download any posts from users on instances with secure fetch enabled. For more information, see [this wiki page](https://github.com/Lynnesbian/mstdn-ebooks/wiki/Secure-fetch).

## Install/usage Guide
An installation and usage guide is available [here](https://cloud.lynnesbian.space/s/jozbRi69t4TpD95). It's primarily targeted at Linux, but it should be possible on BSD, macOS, etc. I've also put some effort into providing steps for Windows, but I can't make any guarantees as to its effectiveness.

### Docker
While there is a Docker version provided, it is **not guaranteed to work**. I personally don't use Docker and don't know how the Dockerfile works; it was create over a year ago by someone else and hasn't been updated since. It might work for you, it might not. If you'd like to help update the Dockerfile, please get in touch with me on the Fediverse.

## Compatibility
| Software  | Downloading statuses                                              | Posting | Replying                                                    |
|-----------|-------------------------------------------------------------------|---------|-------------------------------------------------------------|
| Mastodon  | Yes                                                               | Yes     | Yes                                                         |
| Pleroma   | [Somewhat](https://git.pleroma.social/pleroma/pleroma/issues/866) | Yes     | [No](https://git.pleroma.social/pleroma/pleroma/issues/416) |
| Misskey   | Yes                                                               | No      | No                                                          |
| diaspora* | [No](https://github.com/diaspora/diaspora/issues/7422)            | No      | No                                                          |
| Others    | Maybe                                                             | No      | No                                                          |

*Note: Bots are only supported on Mastodon and Pleroma instances. Bots can learn from users on other instances, but the bot itself must run on either a Mastodon or Pleroma instance.*

mstdn-ebooks uses ActivityPub to download posts. This means that it is not dependant on any particular server software, and should work with anything that (properly) implements ActivityPub. Any software that does not support ActivityPub (e.g. diaspora*) is not supported, and won't work.

I recommend that you create your bot's account on a Mastodon instance. Creating a bot on a Pleroma instance means that your bot will be unable to reply, although posting will work just fine. However, even if your bot is on a Mastodon instance, it will be able to learn from any Pleroma or Misskey users just fine.

## Configuration
Configuring mstdn-ebooks is accomplished by editing `config.json`. If you want to use a different file for configuration, specify it with the `--cfg` argument. For example, if you want to use `/home/lynne/c.json` instead, you would run `python3 main.py --cfg /home/lynne/c.json` instead of just `python3 main.py`

| Setting                  | Default                                 | Meaning                                                                                                                                                                                                                                                                                 |
|--------------------------|-----------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| site                     | https://botsin.space                    | The instance your bot will log in to and post from. This must start with `https://` or `http://` (preferably the latter)                                                                                                                                                                |
| cw                       | null                                    | The content warning (aka subject) mstdn-ebooks will apply to non-error posts.                                                                                                                                                                                                           |
| cw_reply                 | false                                   | If true, replies will be CW'd                                                                                                                                                                                                                                                           |
| instance_blacklist       | ["bofa.lol", "witches.town", "knzk.me"] | If your bot is following someone from a blacklisted instance, it will skip over them and not download their posts. This is useful for ensuring that mstdn-ebooks doesn't waste time trying to download posts from dead instances, without you having to unfollow the user(s) from them. |
| learn_from_cw            | false                                   | If true, mstdn-ebooks will learn from CW'd posts.                                                                                                                                                                                                                                       |
| mention_handling         | 1                                       | 0: Never use mentions. 1: Only generate fake mentions in the middle of posts, never at the start. 2: Use mentions as normal (old behaviour).                                                                                                                                            |
| max_thread_length        | 15                                      | The maximum number of bot posts in a thread before it stops replying. A thread can be 10 or 10000 posts long, but the bot will stop after it has posted `max_thread_length` times.                                                                                                      |
| strip_paired_punctuation | false                                   | If true, mstdn-ebooks will remove punctuation that commonly appears in pairs, like " and (). This avoids the issue of posts that open a bracket (or quote) without closing it.                                                                                                          |
| limit_length             | false                                   | If true, the sentence length will be random between `length_lower_limit` and `length_upper_limit`                                                                                                                                                                                       |
| length_lower_limit       | 5                                       | The lower bound in the random number range above. Only matters if `limit_length` is true.                                                                                                                                                                                               |
| length_upper_limit       | 50                                      | The upper bound in the random number range above. Can be the same as `length_lower_limit` to disable randomness. Only matters if `limit_length` is true.                                                                                                                                |
| overlap_ratio_enabled    | false                                   | If true, checks the output's similarity to the original posts.                                                                                                                                                                                                                          |
| overlap_ratio            | 0.7                                     | The ratio that determins if the output is too similar to original or not. With decreasing ratio, both the interestingness of the output and the likelihood of failing to create output increases. Only matters if `overlap_ratio_enabled` is true.                                      |

## Donating
Please don't feel obligated to donate at all.

- [Ko-Fi](https://ko-fi.com/lynnesbian) allows you to make one-off payments in increments of AU$3. These payments are not taxed.
- [PayPal](https://paypal.me/lynnesbian) allows you to make one-off payments of any amount in a range of currencies. These payments may be taxed.
