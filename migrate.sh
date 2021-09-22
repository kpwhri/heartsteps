#!/bin/bash

docker-compose run server python manage.py makemigrations
docker-compose run server python manage.py migrate