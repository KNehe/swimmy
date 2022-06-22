# syntax=docker/dockerfile:1

FROM python:3

ENV PYTHONUNBUFFERED=1

WORKDIR /usr/src/pools

COPY requirements.txt ./

RUN pip install -r requirements.txt

# pull official base image
# FROM python:3

# set environment variables
# ENV PYTHONDONTWRITEBYTECODE 1
# ENV PYTHONUNBUFFERED 1

# set work directory
# WORKDIR /code

# install dependencies
# RUN pip install --upgrade pip
# COPY requirements.txt /code/
# RUN pip install -r requirements.txt
# COPY . /code/