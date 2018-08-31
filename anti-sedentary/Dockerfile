FROM python:3.6
ENV PYTHONUNBUFFERED 1

RUN apt-get update && \
    apt-get install -y r-base

# Create and add files to Docker
WORKDIR /anti-sedentary
ADD . /anti-sedentary

#Load python dependencies
RUN pip install -r requirements.txt

#Load R dependencies
RUN Rscript install.r

# Run the server
CMD gunicorn -b 0.0.0.0:8080 wsgi