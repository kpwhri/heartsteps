docker-compose -f justwalk.docker-compose.yaml build server > /dev/null
docker-compose build client > /dev/null
docker-compose run server python manage.py migrate > /dev/null
docker-compose run client npm install