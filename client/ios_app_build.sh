cd client
node --version
cordova platform add ios
cd platforms/ios
export HEARTSTEPS_URL=https://dev.heartsteps.net/api
export BUILD_PLATFORM=ios
export BUILD_VERSION=2.3.0
export BUILD_NUMBER=2056
export ONESIGNAL_APP_ID=ce147de3-15d0-4bbd-9d32-ad17c3986cc1
npm run build:app:ios
open HeartSteps.xcworkspace