FROM python:3
ENV PYTHONUNBUFFERED 1

RUN mkdir /server
WORKDIR /server
ADD . /server
ENV http_proxy http://svcctrhs:password05@proxy.ghc.org:8080
ENV https_proxy http://svcctrhs:password05@proxy.ghc.org:8080

RUN pip install -r requirements.txt
EXPOSE 8080
ENTRYPOINT env `cat .env` && gunicorn -b :8080 heartsteps.wsgi
