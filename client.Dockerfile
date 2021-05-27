FROM node:10

# enables live reload for windows
ENV CHOKIDAR_USEPOLLING 1

RUN npm install cordova ionic sass -g

ADD . /client
WORKDIR /client

# Turn off bin links, because docker gets cranky
# RUN npm config set bin-links false

RUN npm install
CMD npm run build:app --prod
