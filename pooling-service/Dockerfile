FROM python:3.6.8
ENV PYTHONUNBUFFERED 1



# Anaconda installing
RUN wget https://repo.continuum.io/archive/Anaconda3-5.2.0-Linux-x86_64.sh
RUN bash Anaconda3-5.2.0-Linux-x86_64.sh -b
RUN rm Anaconda3-5.2.0-Linux-x86_64.sh

# Set path to conda
#ENV PATH /root/anaconda3/bin:$PATH
ENV PATH /root/anaconda3/bin:$PATH



RUN conda create -n py36 python=3.6

ENV PATH /root/anaconda3/envs/py36/bin:$PATH

RUN conda update conda

RUN conda install jupyter


