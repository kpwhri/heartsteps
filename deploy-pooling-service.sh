#!/bin/bash

gcloud auth activate-service-account --key-file=credentials/gce.json
gcloud auth configure-docker -q
gcloud config set project heartsteps-kpwhri

#re-download to save build time
docker pull gcr.io/heartsteps-kpwhri/pooling-service
docker tag gcr.io/heartsteps-kpwhri/pooling-service heartsteps_pooling-service

docker-compose build pooling-service
docker tag heartsteps_pooling-service gcr.io/heartsteps-kpwhri/pooling-service
docker push gcr.io/heartsteps-kpwhri/pooling-service

gcloud compute instances update-container pooling-service --zone=us-west1-b \
    --container-image gcr.io/heartsteps-kpwhri/pooling-service:latest
