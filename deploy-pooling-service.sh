#!/bin/bash

docker-compose build pooling-service
docker tag heartsteps_pooling-service gcr.io/heartsteps-kpwhri/pooling-service
docker push gcr.io/heartsteps-kpwhri/pooling-service

gcloud compute instances update-container pooling-service \
    --container-image gcr.io/heartsteps-kpwhri/pooling-service:latest
