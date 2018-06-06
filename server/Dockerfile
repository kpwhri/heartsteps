FROM python:3
ENV PYTHONUNBUFFERED 1

# Create and add files to Docker
RUN mkdir /server
WORKDIR /server
ADD . /server

#Load python dependencies
RUN pip install -r requirements.txt

# Load google sql dependency
RUN wget https://dl.google.com/cloudsql/cloud_sql_proxy.linux.amd64 -O /cloud_sql_proxy && \
    chmod +x /cloud_sql_proxy

# Run the server
EXPOSE 8080
ENV GCLOUD_SQL_INSTANCE heartsteps-205523:us-west1:heartsteps-test
CMD /cloud_sql_proxy -instances=${GCLOUD_SQL_INSTANCE}=tcp:5432 -credential_file=gce.json & \ 
    gunicorn -b :8080 heartsteps.wsgi