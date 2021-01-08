#!/bin/bash

gcloud auth activate-service-account --key-file=credentials/google-service-account.json
gcloud auth configure-docker -q
gcloud config set project heartsteps-kpwhri
gcloud container clusters get-credentials heartsteps-kpw --region=us-west1-a

cp credentials/.env-production server/.env
cp credentials/.env-production client/.env

docker-compose -f docker-compose.activity-suggestions.yaml build walking-suggestion-service anti-sedentary-service > /dev/null
docker-compose -f docker-compose.gcloud.yaml build nginx > /dev/null
docker-compose build server > /dev/null
docker-compose build client > /dev/null

docker-compose run client npm run build:app --prod
gsutil -m rsync -dr client/www gs://heartsteps-assets/app

docker-compose run -e BUILD_NUMBER=$TRAVIS_BUILD_NUMBER client npm run build:website --prod
gsutil -m rsync -dr client/www gs://heartsteps-assets/website

docker-compose run server python manage.py collectstatic
gsutil -m rsync -dr server/static gs://heartsteps-assets/static

docker tag heartsteps_nginx gcr.io/heartsteps-kpwhri/heartsteps-nginx
docker push gcr.io/heartsteps-kpwhri/heartsteps-nginx
docker tag heartsteps_server gcr.io/heartsteps-kpwhri/heartsteps-server
docker push gcr.io/heartsteps-kpwhri/heartsteps-server
docker tag heartsteps_walking-suggestion-service gcr.io/heartsteps-kpwhri/walking-suggestion-service
docker push gcr.io/heartsteps-kpwhri/walking-suggestion-service
docker tag heartsteps_anti-sedentary-service gcr.io/heartsteps-kpwhri/anti-sedentary-service
docker push gcr.io/heartsteps-kpwhri/anti-sedentary-service
# update kubernetes images...
sed -i "s/DEFAULT_BUILD_NUMBER/'$TRAVIS_BUILD_NUMBER'/g" deployment.yaml
kubectl apply -f deployment.yaml
# Migrate database
docker-compose -f docker-compose.gcloud.yaml run server python manage.py migrate
