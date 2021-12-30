#!/bin/bash

gcloud auth activate-service-account --key-file=credentials/gcloud-dev-service-account.json
gcloud auth configure-docker -q
gcloud config set project heartsteps-dev
gcloud container clusters get-credentials dev-cluster --region=us-central1-a

cp credentials/.env-gcloud-dev server/.env
cp credentials/justwalk.env server/justwalk.env
cp credentials/.env-gcloud-dev client/.env

docker-compose -f gcloud-dev.docker-compose.yaml build nginx
docker tag heartsteps_nginx gcr.io/heartsteps-dev/heartsteps-nginx
docker push gcr.io/heartsteps-dev/heartsteps-nginx

docker-compose -f gcloud-dev.docker-compose.yaml build server
docker-compose run server python manage.py collectstatic --no-input
gsutil -m rsync -dr server/static gs://heartsteps-dev/static
docker tag heartsteps_server gcr.io/heartsteps-dev/heartsteps-server
docker push gcr.io/heartsteps-dev/heartsteps-server

# This installs node_modules into the client directory,
# which is missing because of docker-compose configuraiton
docker-compose run client npm install

docker-compose -f gcloud-dev.docker-compose.yaml build client
docker-compose run client npm run build:app --prod
gsutil -m rsync -dr client/www gs://heartsteps-dev/app

docker-compose run -e BUILD_NUMBER=$TRAVIS_BUILD_NUMBER client npm run build:website --prod
gsutil -m rsync -dr client/www gs://heartsteps-dev/website

kubectl create secret generic credentials --from-file credentials

# update kubernetes images...
sed -i "s/DEFAULT_BUILD_NUMBER/'$TRAVIS_BUILD_NUMBER'/g" gcloud-dev-deployment.yaml
kubectl apply -f gcloud-dev-deployment.yaml

# Migrate database
docker-compose -f gcloud-dev.docker-compose.yaml run server python manage.py migrate
