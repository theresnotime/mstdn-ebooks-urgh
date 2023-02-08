FROM python:3-alpine

ADD requirements.txt /ebooks/

WORKDIR /ebooks/
VOLUME /ebooks/data/

RUN apk add --virtual .build-deps gcc musl-dev libffi-dev openssl-dev \
     && pip install -r requirements.txt \
     && apk del --purge .build-deps \
     && ln -s data/config.json . \
     && ln -s data/toots.db .

ADD entrypoint.sh ./
ADD *.py ./

ENV EBOOKS_SITE=https://botsin.space
ENV POST_TIMINGS="*/30 * * * *"
ENV FETCH_TIMINGS="5 */2 * * *"

ENTRYPOINT [ "/ebooks/entrypoint.sh" ]
