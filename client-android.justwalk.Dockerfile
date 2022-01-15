FROM openjdk:8

# enables live reload for windows
ENV CHOKIDAR_USEPOLLING 1


# # Install gradle
RUN apt-get update && \ 
    apt-get install -y gradle && \
    apt-get install build-essential -y --no-install-recommends



# # Install Android SDK
ENV ANDROID_HOME /usr/local/android-sdk
ENV ANDROID_SDK_ROOT /usr/local/android-sdk
RUN mkdir /usr/local/android-sdk && \
    curl -o android-sdk.zip https://dl.google.com/android/repository/sdk-tools-linux-4333796.zip && \
    unzip android-sdk.zip -d $ANDROID_HOME && rm android-sdk.zip && \
    yes | $ANDROID_HOME/tools/bin/sdkmanager --licenses && \
    $ANDROID_HOME/tools/bin/sdkmanager "build-tools;28.0.3" "platforms;android-28" "platform-tools"
ENV PATH $PATH:$ANDROID_HOME/tools:$ANDROID_HOME/platform-tools

# Install nodejs
ENV NVM_DIR /root/.nvm
ENV NODE_VERSION 10

RUN curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.1/install.sh | bash \
    && . $NVM_DIR/nvm.sh \
    && nvm install $NODE_VERSION \
    && nvm alias default $NODE_VERSION \
    && nvm use default

ENV NODE_PATH $NVM_DIR/v$NODE_VERSION/lib/node_modules
ENV PATH      $NVM_DIR/v$NODE_VERSION/bin:$PATH

RUN apt-get update && \
    apt-get install -y npm
# RUN curl -sL https://deb.nodesource.com/setup_10.x | bash - && \
#     apt-get update && \ 
#     apt-get install -y nodejs npm

RUN npm install cordova @ionic/cli sass -g

ADD ./client /client
ADD ./credentials /credentials
WORKDIR /client

RUN npm install
CMD npm run build:app:android
