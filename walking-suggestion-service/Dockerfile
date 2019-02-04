FROM heartsteps_service-template:latest

# Create and add files to Docker
WORKDIR /walking-suggestion-service
ADD . /walking-suggestion-service

RUN pip install -r requirements.txt
RUN Rscript install.r

RUN apt-get install -y vim

# Anaconda installing
RUN wget https://repo.continuum.io/archive/Anaconda3-5.0.1-Linux-x86_64.sh && \
    bash Anaconda3-5.0.1-Linux-x86_64.sh -b && \
    rm Anaconda3-5.0.1-Linux-x86_64.sh

# Set path to conda
ENV PATH /root/anaconda3/bin:$PATH

RUN mkdir -p data

# Run the server
CMD gcsfuse walking-suggestions-data ./data && gunicorn -b 0.0.0.0:8080 wsgi
