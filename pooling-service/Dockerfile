FROM python:3.6.8 as pooling-service-base
ENV PYTHONUNBUFFERED 1

RUN apt-get update && \
    apt-get install -y r-base


# Create and add files to Docker
ADD . /pooling-service

RUN chmod +x /pooling-service/install.sh && \
    /pooling-service/install.sh

FROM heartsteps_service-template:latest
ADD . /pooling-service
WORKDIR /pooling-service

RUN ls
RUN pwd

RUN pip install -r requirements.txt
RUN Rscript install.r

ENV googleStorageBucket walking-suggestions-data

# Mount GCSFuse Run the server
RUN mkdir -p ./data
CMD gcsfuse --implicit-dirs walking-suggestions-data ./data && gunicorn -b 0.0.0.0:8080 wsgi
