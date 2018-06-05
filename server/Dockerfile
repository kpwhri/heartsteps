FROM python:3
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code
ADD . /code/
ENV http_proxy http://svcctrhs:password05@proxy.ghc.org:8080
ENV https_proxy http://svcctrhs:password05@proxy.ghc.org:8080
RUN pip install -r requirements.txt