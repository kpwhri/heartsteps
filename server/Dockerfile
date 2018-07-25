FROM python:3.6
ENV PYTHONUNBUFFERED 1

RUN apt-get update && \
    apt-get install -y supervisor erlang rabbitmq-server

# Create and add files to Docker
WORKDIR /server
ADD . /server

#Load python dependencies
RUN pip install -r requirements.txt

# Run the server
CMD supervisord -n -c supervisord.conf