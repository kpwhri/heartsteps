FROM node:8

RUN mkdir code
WORKDIR /code
ADD . /code

ENV http_proxy http://svcctrhs:password05@proxy.ghc.org:8080
ENV https_proxy http://svcctrhs:password05@proxy.ghc.org:8080
RUN npm install ionic -g