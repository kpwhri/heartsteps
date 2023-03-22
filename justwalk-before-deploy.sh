docker-compose -f justwalk.docker-compose.yaml build server > /dev/null
docker-compose -f justwalk.docker-compose.yaml build client > /dev/null
docker-compose -f justwalk.docker-compose.yaml run server python manage.py migrate > /dev/null
docker-compose -f justwalk.docker-compose.yaml run client npm install