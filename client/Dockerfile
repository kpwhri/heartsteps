FROM openjdk:8

# enables live reload for windows
ENV CHOKIDAR_USEPOLLING 1

# # Install gradle
RUN apt-get update && apt-get install -y gradle

# # Install Android SDK
ENV ANDROID_HOME /usr/local/android-sdk
RUN mkdir /usr/local/android-sdk && \
    curl -o android-sdk.zip https://dl.google.com/android/repository/sdk-tools-linux-4333796.zip && \
    unzip android-sdk.zip -d $ANDROID_HOME && rm android-sdk.zip && \
    yes | $ANDROID_HOME/tools/bin/sdkmanager --licenses && \
    $ANDROID_HOME/tools/bin/sdkmanager "build-tools;28.0.3" "platforms;android-28" "platform-tools"
ENV PATH $PATH:$ANDROID_HOME/tools:$ANDROID_HOME/platform-tools

# Install nodejs
RUN curl -sL https://deb.nodesource.com/setup_8.x | bash - && \
    apt-get update && \ 
    apt-get install -y nodejs

# RUN npm config set bin-links false

WORKDIR /client
ADD . /client

RUN npm install cordova ionic sass -g
RUN npm install
CMD ionic build --prod
