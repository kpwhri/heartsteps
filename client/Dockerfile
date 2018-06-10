FROM node:8

RUN mkdir client
WORKDIR /client
ADD . /client

# enables live reload for windows
ENV CHOKIDAR_USEPOLLING 1

RUN npm install ionic sass -g