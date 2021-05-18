# FROM ubuntu:20.04
FROM node:10

RUN rm /bin/sh && ln -s /bin/bash /bin/sh

RUN apt-get -y update
RUN apt-get -y install git
RUN apt-get -y install curl
RUN apt-get -y install python

ADD ./client /client

# RUN git clone https://github.com/kpwhri/heartsteps.git

WORKDIR /client

RUN rm -Rf .sourcemaps
RUN rm -Rf node_modules
RUN rm -Rf platform/ios
RUN rm -Rf plugins
RUN rm -Rf www

RUN npm install
RUN npm rebuild node-sass
RUN npm install -g @ionic/cli
RUN npm install -g cordova
RUN npm install -g ionic-angular
RUN npm install -g onesignal-cordova-plugin
# RUN npm install -g pod

RUN ionic cordova platform add ios

# WORKDIR /client/platform/ios
# RUN pod repo update
# RUN pod install
CMD ionic cordova prepare ios