FROM heartsteps_service-template:latest

RUN apt-get update && \
    apt-get install -y postgresql

# Install cloud-sql-proxy
RUN wget https://dl.google.com/cloudsql/cloud_sql_proxy.linux.amd64 -O cloud_sql_proxy && \
    chmod +x cloud_sql_proxy

# Create and add files to Docker
WORKDIR /server
ADD . /server

# RUN easy_install apns2

#Load python dependencies
RUN pip install -r requirements.txt

# Run everything...
CMD honcho start web cloudsql celery
