FROM python:3.6
ENV PYTHONUNBUFFERED 1

RUN apt-get update && \
    apt-get install -y r-base

# Create and add files to Docker
WORKDIR /pooling-service
ADD . /pooling-service


RUN apt-get install -y vim

# Anaconda installing
RUN wget https://repo.continuum.io/archive/Anaconda3-5.0.1-Linux-x86_64.sh
RUN bash Anaconda3-5.0.1-Linux-x86_64.sh -b
RUN rm Anaconda3-5.0.1-Linux-x86_64.sh

# Set path to conda
#ENV PATH /root/anaconda3/bin:$PATH
ENV PATH /root/anaconda3/bin:$PATH



RUN conda create -n py36 python=3.6

ENV PATH /root/anaconda3/envs/py36/bin:$PATH

RUN conda update conda

RUN conda update jupyter

RUN conda install -c conda-forge gpflow


