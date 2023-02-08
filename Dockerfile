FROM python:3-alpine

ADD requirements.txt /ebooks/

WORKDIR /ebooks/
VOLUME /ebooks/data/

RUN apk add --virtual .build-deps gcc musl-dev libffi-dev openssl-dev \
 && pip install -r requirements.txt \
 && apk del --purge .build-deps \
 && ln -s data/config.json . \
 && ln -s data/toots.db .

ADD *.py /ebooks/

ENV EBOOKS_SITE=https://botsin.space
ENV POST_TIMINGS="*/30 * * * *"
ENV FETCH_TIMINGS="5 */2 * * *"

RUN (echo "${POST_TIMINGS} cd /ebooks/ && python gen.py"; \
     echo "${FETCH_TIMINGS} cd /ebooks/ && python main.py"; \
     echo "@reboot cd /ebooks/ && python reply.py") | crontab -

CMD (test -f data/config.json || echo "{\"site\":\"${EBOOKS_SITE}\"}" > data/config.json) \
 && (test -f data/toots.db || (python main.py && exit)) \
 && exec crond -f -L /dev/stdout
