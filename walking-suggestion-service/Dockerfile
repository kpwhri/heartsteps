FROM python:3.6
ENV PYTHONUNBUFFERED 1

RUN apt-get update && \
    apt-get install -y r-base

# Create and add files to Docker
WORKDIR /walking-suggestions
ADD . /walking-suggestions

#Load python dependencies
RUN pip install -r requirements.txt

#Load R dependencies
RUN Rscript install.r

RUN apt-get install -y vim

# # Anaconda installing
RUN wget https://repo.continuum.io/archive/Anaconda3-5.0.1-Linux-x86_64.sh && \
    bash Anaconda3-5.0.1-Linux-x86_64.sh -b && \
    rm Anaconda3-5.0.1-Linux-x86_64.sh

# Set path to conda
#ENV PATH /root/anaconda3/bin:$PATH
ENV PATH /root/anaconda3/bin:$PATH

ENV GOOGLE_APPLICATION_CREDENTIALS /credentials/gae-storage-service.json
ENV GCSFUSE_REPO gcsfuse-jessie

RUN echo "deb http://packages.cloud.google.com/apt $GCSFUSE_REPO main" | tee /etc/apt/sources.list.d/gcsfuse.list
RUN curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key add -
RUN apt-get update && apt-get install -y gcsfuse

RUN mkdir -p data

# Run the server
CMD gcsfuse walking-suggestions-data ./data && gunicorn -b 0.0.0.0:8080 wsgi
