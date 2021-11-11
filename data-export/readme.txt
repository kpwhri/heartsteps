The current data export script is export3.py
Output is produced in ./output
The docker file is ../data_export.Dockerfile
The script run in the container is ./run.sh
This diretory is mapped into container. Changes to code will run without the container being re-build
To run the data export use: docker-compose  -f docker-compose.gcloud.yaml run data_export

