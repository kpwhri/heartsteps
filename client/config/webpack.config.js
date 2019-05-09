var path = require('path');
var webpack = require('webpack');
var webpackConfig = require('@ionic/app-scripts/config/webpack.config');

const env = process.env.IONIC_ENV;

webpackConfig[env].resolve = {
    extensions: ['.ts', '.js'],
    alias: {
        '@app': path.resolve('./src/app/'),
        '@heartsteps': path.resolve('./src/heartsteps/'),
        '@infrastructure': path.resolve('./src/infrastructure/'),
        '@pages': path.resolve('./src/pages/')
    }
}

var envs = new webpack.EnvironmentPlugin({
    PRODUCTION: false,
    HEARTSTEPS_URL: '/api',
    FCM_SENDER_ID: 'firebase-id', // kpwhri heartsteps firebase ID
    ONESIGNAL_APP_ID: 'onesignal-app-id',
    PUSH_NOTIFICATION_DEVICE_TYPE: 'onesignal',
    BUILD_VERSION: '2.0.0',
    BUILD_DATE: '2019-04-22'
});

webpackConfig.dev.plugins.push(envs);
webpackConfig.prod.plugins.push(envs);

module.exports = function() {
    return webpackConfig;   
};