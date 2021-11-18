FROM python:3
ENV PYTHONUNBUFFERED 1

RUN apt-get update

ADD ./study-parser /study-parser
WORKDIR /study-parser

#Load python dependencies
RUN pip install -r requirements.txt

# Authorize gcloud, then run everything
CMD python load_study.py
