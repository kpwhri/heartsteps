FROM node:10

# enables live reload for windows
ENV CHOKIDAR_USEPOLLING 1

RUN npm install cordova @ionic/cli sass -g

ADD . /client
WORKDIR /client

RUN ls
RUN ls /client
RUN npm install
CMD npm run build:app --prod
