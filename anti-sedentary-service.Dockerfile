FROM python:3.6.8
ENV PYTHONUNBUFFERED 1

RUN apt-get update && \
    apt-get install -y r-base=3.3.3-1

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


ADD ./anti-sedentary-service /anti-sedentary-service
WORKDIR /anti-sedentary-service

RUN pip install -r requirements.txt
RUN Rscript install.r

ENV GOOGLE_APPLICATION_CREDENTIALS /credentials/google-storage-service.json
ENV googleStorageBucket anti-sedentary-data

# Run the server
RUN mkdir -p ./data
CMD gcloud auth activate-service-account --key-file=$GOOGLE_APPLICATION_CREDENTIALS && \
    gcloud config set project heartsteps-kpwhri && \
    gcsfuse --implicit-dirs ${googleStorageBucket} ./data && \
    gunicorn -b 0.0.0.0:8080 wsgi --log-level debug