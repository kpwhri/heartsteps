FROM python:3.6.8
ENV PYTHONUNBUFFERED 1

RUN apt-get update

ADD service-template/utils /utils 
ENV PATH $PATH:/utils
RUN chmod +x /utils/*

RUN apt-get update && \
    apt-get install -y postgresql

# Create and add files to Docker
ADD ./server /server
WORKDIR /server

#Install dataexport virtual environment and dependencies
#to support the use of pandas
ENV OLDPATH=$PATH
ENV VIRTUAL_ENV=/export_venv
RUN python -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
RUN pip install -r requirements.txt
RUN pip install -r requirements_export.txt
ENV PATH=$OLDPATH
