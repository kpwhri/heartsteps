var path = require('path');
var webpack = require('webpack');
var webpackConfig = require('@ionic/app-scripts/config/webpack.config');

webpackConfig.resolve = {
    extensions: ['.ts', '.js'],
    alias: {
            '@app': path.resolve('./'),
            }
}

var envs = new webpack.EnvironmentPlugin({
    HEARTSTEPS_URL: '/api',
    FIREBASE_MESSAGING_SENDER_ID: '50745768851' // nick's heartsteps firebase messaging id
});

webpackConfig.dev.plugins.push(envs);
webpackConfig.prod.plugins.push(envs);

module.exports = webpackConfig;