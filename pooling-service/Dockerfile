FROM python:3.6.8 as pooling-service-base
ENV PYTHONUNBUFFERED 1

RUN apt-get update && \
    apt-get install -y r-base


# Create and add files to Docker
WORKDIR /pooling-service
ADD . /pooling-service

RUN /pooling-service/install_python.sh

FROM heartsteps_service-template:latest
RUN chmod 777 utils/copy-files

RUN pip install -r requirements.txt
RUN Rscript install.r

ENV googleStorageBucket walking-suggestions-data

# Mount GCSFuse Run the server
RUN mkdir -p ./data
CMD gcsfuse --implicit-dirs walking-suggestions-data ./data && gunicorn -b 0.0.0.0:8080 wsgi
