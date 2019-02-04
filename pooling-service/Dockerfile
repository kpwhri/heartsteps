FROM python:3.6.8
ENV PYTHONUNBUFFERED 1

RUN apt-get update && \
    apt-get install -y r-base

# Create and add files to Docker
WORKDIR /pooling-service
ADD . /pooling-service


ENV PATH /root/anaconda3/envs/py36/bin:$PATH

RUN echo "source activate env" > ~/.bashrc

RUN conda install jupyter