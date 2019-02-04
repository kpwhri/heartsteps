FROM python:3.6
ENV PYTHONUNBUFFERED 1

RUN apt-get update && \
    apt-get install -y r-base

ADD credentials /credentials

ENV GOOGLE_APPLICATION_CREDENTIALS /credentials/gae-storage-service.json
ENV GCSFUSE_REPO gcsfuse-jessie

RUN echo "deb http://packages.cloud.google.com/apt $GCSFUSE_REPO main" | tee /etc/apt/sources.list.d/gcsfuse.list
RUN curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key add -
RUN apt-get update && apt-get install -y gcsfuse
