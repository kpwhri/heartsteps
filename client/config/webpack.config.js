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
    HEARTSTEPS_URL: '/api',
    FIREBASE_MESSAGING_SENDER_ID: '50745768851' // nick's heartsteps firebase messaging id
});

webpackConfig.dev.plugins.push(envs);
webpackConfig.prod.plugins.push(envs);

module.exports = function() {
    return webpackConfig;   
};