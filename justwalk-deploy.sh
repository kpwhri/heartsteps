#!/bin/bash

gcloud auth activate-service-account --key-file=credentials/ucsd-publichealth-justwalk.json
gcloud auth configure-docker -q
gcloud config set project ucsd-publichealth-justwalk
gcloud container clusters get-credentials justwalk --region=us-west1-a

cp credentials/.env-gcloud-dev server/.env
cp credentials/justwalk.env server/justwalk.env
cp credentials/.env-gcloud-dev client/.env

docker-compose -f justwalk.docker-compose.yaml build nginx
docker compose -f justwalk.docker-compose.yaml push nginx

docker-compose -f justwalk.docker-compose.yaml build server
docker-compose -f justwalk.docker-compose.yaml run server python manage.py collectstatic --no-input
gsutil -m rsync -dr server/static gs://ucsd-publichealth-justwalk-media/static
docker push gcr.io/ucsd-publichealth-justwalk/justwalk-server

docker-compose -f justwalk.docker-compose.yaml build client

# This installs node_modules into the client directory,
# which is missing because of docker-compose configuraiton
docker-compose -f justwalk.docker-compose.yaml run client npm install
docker-compose -f justwalk.docker-compose.yaml run client npm run build:app --prod
gsutil -m rsync -dr client/www gs://ucsd-publichealth-justwalk-media/app

docker-compose -f justwalk.docker-compose.yaml run -e BUILD_NUMBER=$TRAVIS_BUILD_NUMBER client npm run build:website --prod
gsutil -m rsync -dr client/www gs://ucsd-publichealth-justwalk-media/website

kubectl create secret generic credentials --from-file credentials

# update kubernetes images...
sed -i "s/DEFAULT_BUILD_NUMBER/'$TRAVIS_BUILD_NUMBER'/g" justwalk-deployment.yaml
kubectl apply -f justwalk-deployment.yaml

# Migrate database
docker-compose -f justwalk.docker-compose.yaml run server python manage.py migrate
