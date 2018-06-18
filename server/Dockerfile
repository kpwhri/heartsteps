FROM python:3
ENV PYTHONUNBUFFERED 1

RUN apt-get update && \
    apt-get install -y nginx supervisor

# Create and add files to Docker
WORKDIR /server
ADD . /server

#Load python dependencies
RUN pip install -r requirements.txt

# Load google sql dependency
RUN wget https://dl.google.com/cloudsql/cloud_sql_proxy.linux.amd64 -O /usr/local/bin/cloud_sql_proxy && \
    chmod +x /usr/local/bin/cloud_sql_proxy

# Used by Django to encrypt passwords & such
ARG SECRET_KEY
ENV SECRET_KEY $SECRET_KEY

# Host name is used as allowed_host for django
ARG HOST_NAME
ENV HOST_NAME $HOST_NAME

ARG GCLOUD_DB_INSTANCE
ENV GCLOUD_DB_INSTANCE ${GCLOUD_DB_INSTANCE}

ARG DATABASE_URL
ENV DATABASE_URL ${DATABASE_URL}

ARG DEBUG
ENV DEBUG ${DEBUG}

# Run the server
CMD supervisord -n -c supervisord.conf