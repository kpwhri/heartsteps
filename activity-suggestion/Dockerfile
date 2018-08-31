FROM python:3.6
ENV PYTHONUNBUFFERED 1

# Add google dns server temporarily because something is funky
RUN echo "nameserver 8.8.8.8" | tee /etc/resolv.conf > /dev/null

RUN apt-get update && \
    apt-get install -y r-base

# Create and add files to Docker
WORKDIR /activity-suggestion
ADD . /activity-suggestion

#Load python dependencies
RUN pip install -r requirements.txt

#Load R dependencies
RUN Rscript install.r

# Run the server
CMD gunicorn -b 0.0.0.0:8080 wsgi