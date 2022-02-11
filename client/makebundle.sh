#!/bin/bash

npm run build:app:android
cd platforms/android/
./gradlew bundleRelease
cd /client
./cpapk.sh