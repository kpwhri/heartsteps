FROM python:3.6
ENV PYTHONUNBUFFERED 1

# Create and add files to Docker
WORKDIR /activity-suggestion
ADD . /activity-suggestion

#Load python dependencies
RUN pip install -r requirements.txt

# Run the server
#CMD supervisord -n -c supervisord.conf