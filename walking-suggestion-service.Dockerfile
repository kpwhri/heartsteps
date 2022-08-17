FROM python:3.7.7-buster
ENV PYTHONUNBUFFERED 1

RUN echo "deb [trusted=yes] http://cloud.r-project.org/bin/linux/debian buster-cran40/" | tee -a /etc/apt/sources.list && \
    apt-get update && \
    apt-get install -y r-base

# Install google cloud sdk and gcsfuse
ENV CLOUD_SDK_REPO cloud-sdk-jessie
ENV GCSFUSE_REPO gcsfuse-jessie
RUN echo "deb http://packages.cloud.google.com/apt $CLOUD_SDK_REPO main" | tee -a /etc/apt/sources.list.d/google-cloud-sdk.list && \
    echo "deb http://packages.cloud.google.com/apt $GCSFUSE_REPO main" | tee /etc/apt/sources.list.d/gcsfuse.list && \
    curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key add - && \
    apt-get update && apt-get install -y gcsfuse google-cloud-sdk google-cloud-sdk-gke-gcloud-auth-plugin

ADD service-template/utils /utils 
ENV PATH $PATH:/utils
RUN chmod +x /utils/*

# Create and add files to Docker
WORKDIR /walking-suggestion-service
ADD walking-suggestion-service /walking-suggestion-service

#Load python dependencies
RUN pip install setuptools==45 && \
    pip install -r requirements.txt

#Load R dependencies
RUN Rscript install.r

ENV googleStorageBucket walking-suggestions-data
ENV GOOGLE_APPLICATION_CREDENTIALS /credentials/google-storage-service.json

# Mount GCSFuse Run the server
RUN mkdir -p ./data
CMD gcloud auth activate-service-account --key-file=$GOOGLE_APPLICATION_CREDENTIALS && \
    gcloud config set project heartsteps-kpwhri && \
    gcsfuse --implicit-dirs walking-suggestions-data ./data && \
    gunicorn -b 0.0.0.0:8080 wsgi --timeout=900 --log-level debug
