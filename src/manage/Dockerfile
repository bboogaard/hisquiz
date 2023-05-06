# syntax=docker/dockerfile:1
FROM python:3.9
ENV PYTHONUNBUFFERED=1
COPY ./src/manage/requirements.txt /code/
WORKDIR /code
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
COPY ./src/manage /code