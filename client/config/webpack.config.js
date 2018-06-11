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
    HEARTSTEPS_URL: 'http://localhost:8080'
});

webpackConfig.dev.plugins.push(envs);
webpackConfig.prod.plugins.push(envs);

module.exports = webpackConfig;