FROM python:3.7-alpine

ENV PYTHONBUFFERED 1
ENV DJANGO_ENV dev
ENV DOCKER_CONTAINER 1
ENV PYTHONDONTWRITEBYTECODE 1

RUN apk update \
    && apk add --virtual build-deps \
    && apk add gcc python3-dev musl-dev \
    && apk add postgresql-dev \
    && pip install psycopg2 \
    && apk del build-deps

COPY ./requirements.txt /code/requirements.txt
RUN pip install -r /code/requirements.txt

COPY . /code/
WORKDIR /code/

EXPOSE 8080