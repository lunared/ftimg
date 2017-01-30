FROM python:3.5-alpine

RUN apk update
RUN apk add build-base python-dev py-pip jpeg-dev zlib-dev

ADD requirements.txt requirements.txt
RUN pip install -r requirements.txt

EXPOSE 5000

WORKDIR /var/www
