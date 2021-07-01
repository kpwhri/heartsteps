FROM node:10

# enables live reload for windows
ENV CHOKIDAR_USEPOLLING 1

RUN npm install cordova @ionic/cli sass -g
# RUN npm install @ionic/app-scripts -g

ADD . /client
WORKDIR /client

RUN rm -Rf .sourcemaps
RUN rm -Rf node_modules
RUN rm -Rf platform/ios
RUN rm -Rf plugins
RUN rm -Rf www

RUN ls
RUN ls /client
RUN npm install
CMD npm i -D -E @ionic/app-scripts && npm run build:app --prod
