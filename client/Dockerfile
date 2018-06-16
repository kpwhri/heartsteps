FROM node:8

WORKDIR /client
ADD . /client

# enables live reload for windows
ENV CHOKIDAR_USEPOLLING 1

RUN npm install cordova ionic sass -g

CMD npm install -y && \
    ionic build