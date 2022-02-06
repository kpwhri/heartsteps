#!/bin/bash

cordova clean
npm run build:app:android
./cpapk.sh