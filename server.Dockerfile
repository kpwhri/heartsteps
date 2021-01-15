FROM python:3.6.8
ENV PYTHONUNBUFFERED 1

RUN apt-get update

# Install google cloud sdk and gcsfuse
ENV GOOGLE_APPLICATION_CREDENTIALS /credentials/google-storage-service.json
ENV CLOUD_SDK_REPO cloud-sdk-jessie
ENV GCSFUSE_REPO gcsfuse-jessie
RUN echo "deb http://packages.cloud.google.com/apt $CLOUD_SDK_REPO main" | tee -a /etc/apt/sources.list.d/google-cloud-sdk.list && \
    echo "deb http://packages.cloud.google.com/apt $GCSFUSE_REPO main" | tee /etc/apt/sources.list.d/gcsfuse.list && \
    curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key add - && \
    apt-get update && apt-get install -y gcsfuse google-cloud-sdk

ADD service-template/utils /utils 
ENV PATH $PATH:/utils
RUN chmod +x /utils/*

RUN apt-get update && \
    apt-get install -y postgresql

# Install cloud-sql-proxy
RUN wget https://dl.google.com/cloudsql/cloud_sql_proxy.linux.amd64 -O cloud_sql_proxy && \
    chmod +x cloud_sql_proxy

# Create and add files to Docker
ADD ./server /server
WORKDIR /server


# RUN easy_install apns2

#Load python dependencies
RUN pip install -r requirements.txt

# Authorize gcloud, then run everything
CMD gcloud auth activate-service-account --key-file=$GOOGLE_APPLICATION_CREDENTIALS && \
    gcloud config set project heartsteps-kpwhri && \
    honcho start web cloudsql celery

#Install dataexport virtual environment and dependencies
#to support the use of pandas
ENV OLDPATH=$PATH
ENV VIRTUAL_ENV=/export_venv
RUN python -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
RUN pip install -r requirements.txt
RUN pip install -r requirements_export.txt
ENV PATH=$OLDPATH