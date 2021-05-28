FROM node:10

# enables live reload for windows
ENV CHOKIDAR_USEPOLLING 1

RUN npm install cordova ionic sass -g

ADD . /client
WORKDIR /client

RUN npm install
CMD npm run build:app --prod
