#!/bin/bash

gcloud auth activate-service-account --key-file=credentials/google-service-account.json
gcloud auth configure-docker -q
gcloud config set project heartsteps-kpwhri

#re-download to save build time
docker pull gcr.io/heartsteps-kpwhri/pooling-service
docker tag gcr.io/heartsteps-kpwhri/pooling-service heartsteps_pooling-service

docker-compose -f docker-compose.activity-suggesions.yaml build pooling-service
docker tag heartsteps_pooling-service gcr.io/heartsteps-kpwhri/pooling-service:latest
docker push gcr.io/heartsteps-kpwhri/pooling-service:latest

gcloud compute instances update-container pooling-service --zone=us-west1-b \
    --container-image gcr.io/heartsteps-kpwhri/pooling-service:latest
