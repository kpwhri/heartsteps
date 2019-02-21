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

var push_device_type = 'apns';
if(env === 'dev') {
    push_device_type = 'apns-dev';
}

var envs = new webpack.EnvironmentPlugin({
    HEARTSTEPS_URL: '/api',
    FCM_SENDER_ID: 'firebase-id', // kpwhri heartsteps firebase ID
    PUSH_NOTIFICATION_DEVICE_TYPE: push_device_type
});

webpackConfig.dev.plugins.push(envs);
webpackConfig.prod.plugins.push(envs);

module.exports = function() {
    return webpackConfig;   
};