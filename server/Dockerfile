FROM python:3
ENV PYTHONUNBUFFERED 1

RUN mkdir /server
WORKDIR /server
ADD . /server

RUN pip install -r requirements.txt

EXPOSE 8080

ENTRYPOINT env `cat .env` && gunicorn -b :8080 heartsteps.wsgi