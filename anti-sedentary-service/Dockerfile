FROM heartsteps_service-template:latest

# Create and add files to Docker
WORKDIR /anti-sedentary-service
ADD . /anti-sedentary-service

RUN chmod 777 ../utils/copy-files

RUN pip install -r requirements.txt
RUN Rscript install.r

ENV googleStorageBucket anti-sedentary-data

# Run the server
RUN mkdir -p ./data
CMD gcsfuse --implicit-dirs ${googleStorageBucket} ./data && gunicorn -b 0.0.0.0:8080 wsgi --log-level debug