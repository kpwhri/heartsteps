FROM heartsteps_service-template:latest

# Create and add files to Docker
WORKDIR /anti-sedentary-service
ADD . /anti-sedentary-service

RUN pip install -r requirements.txt
RUN Rscript install.r

# Run the server
RUN mkdir -p ./data
CMD gcsfuse --implicit-dirs anti-sedentary-data ./data && gunicorn -b 0.0.0.0:8080 wsgi