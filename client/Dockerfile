FROM node:8

WORKDIR /client
ADD . /client

# enables live reload for windows
ENV CHOKIDAR_USEPOLLING 1

RUN npm install cordova ionic sass -g
RUN npm install
CMD ionic build --prod