#!/bin/bash

set -xe

(echo "${POST_TIMINGS} cd /ebooks/ && python gen.py"; \
 echo "${FETCH_TIMINGS} cd /ebooks/ && python main.py"; \
 echo "@reboot cd /ebooks/ && python reply.py") | crontab -

test -f data/config.json || echo "{\"site\":\"${EBOOKS_SITE}\"}" > data/config.json

test -f data/toots.db || (python main.py && exit)

exec crond -f -L /dev/stdout
