FROM python:3.6.8
ENV PYTHONUNBUFFERED 1

RUN apt-get update && \
    apt-get install -y r-base

FROM heartsteps_service-template:latest
RUN chmod 777 utils/copy-files


# Create and add files to Docker
WORKDIR /pooling-service
ADD . /pooling-service

RUN pip install -r requirements.txt
RUN Rscript install.r

ENV googleStorageBucket walking-suggestions-data

# Mount GCSFuse Run the server
RUN mkdir -p ./data
CMD gcsfuse --implicit-dirs walking-suggestions-data ./data && gunicorn -b 0.0.0.0:8080 wsgi




RUN install_python.sh