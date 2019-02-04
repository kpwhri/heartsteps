FROM python:3.6.8
ENV PYTHONUNBUFFERED 1

RUN apt-get update && \
    apt-get install -y r-base

# Create and add files to Docker
WORKDIR /pooling-service
ADD . /pooling-service

RUN conda create -n py36 python=3.6

RUN conda install --name py36 jupyter