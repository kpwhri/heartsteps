#!/bin/bash

cordova clean
npm run build:app:android
cd platforms/android/
./gradlew bundleRelease
cd /client
./cpapk.sh