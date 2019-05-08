FROM heartsteps_service-template

# Create and add files to Docker
WORKDIR /walking-suggestion-service
ADD . /walking-suggestion-service

#Load python dependencies
RUN pip install -r requirements.txt

#Load R dependencies
RUN Rscript install.r

ENV googleStorageBucket walking-suggestions-data

# Mount GCSFuse Run the server
RUN mkdir -p ./data
CMD gcsfuse --implicit-dirs walking-suggestions-data ./data && gunicorn -b 0.0.0.0:8080 wsgi --log-level debug
