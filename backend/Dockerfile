# FROM python:3.11

# WORKDIR /usr/src/app

# ENV PYTHONUNBUFFERED 1
# ENV PYTHONDONTWRITEBYTECODE 1

# COPY ./requirements.txt .
# RUN pip install --upgrade pip
# RUN pip install -r requirements.txt
# pull official base image
FROM python:3.11.0-alpine

# set work directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# copy requirements file
COPY ./requirements.txt /usr/src/app/requirements.txt

# install dependencies
RUN set -eux \
    && apk add --no-cache --virtual .build-deps build-base \
    openssl-dev libffi-dev gcc musl-dev python3-dev \
    postgresql-dev bash \
    && pip install --upgrade pip setuptools wheel \
    && pip install -r /usr/src/app/requirements.txt \
    && rm -rf /root/.cache/pip

# copy project
COPY . /usr/src/app/