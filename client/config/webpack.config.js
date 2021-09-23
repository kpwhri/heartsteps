var path = require('path');
var webpack = require('webpack');
var webpackConfig = require('@ionic/app-scripts/config/webpack.config');
var xml2js = require('xml2js');
var fs = require('fs');
var moment = require('moment');

var BUILD_NUMBER = '2.0.0';
var BUILD_VERSION = '123';
var BUILD_DATE = moment().format('MMMM Do, YYYY');

// If you want to use dev.heartsteps.server, set this to false
// If you want to use localhost, set this to true
var LOCAL = false;

const env = process.env.IONIC_ENV;

var production = true;
if (env === 'dev') {
    production = false;
}


// #256 This part should be tested thoroughly with the live production build/deply environment
console.log("* Setting config.xml bundle id");

var bundle_id = (production) ? "net.heartsteps.kpw" : "net.heartsteps.dev";

fs.readFile('./config.xml', 'utf8', function(err, data) {
    var parser = new xml2js.Parser();
    parser.parseString(data, function(err, obj) {
        obj['widget']['$']['id'] = bundle_id;

        var builder = new xml2js.Builder();
        xml = builder.buildObject(obj);
        fs.writeFile('./config.xml', xml, function() {
            console.log('* Updated config.xml');
        });
    });
});
////////////////////////






if (process.env.BUILD_NUMBER && process.env.BUILD_VERSION) {
    console.log('* Setting config.xml build number and version');
    BUILD_NUMBER = process.env.BUILD_NUMBER;
    BUILD_VERSION = process.env.BUILD_VERSION;
    fs.readFile('./config.xml', 'utf8', function(err, data) {
        var parser = new xml2js.Parser();
        parser.parseString(data, function(err, obj) {
            obj['widget']['$']['android-versionCode'] = process.env.BUILD_NUMBER;
            obj['widget']['$']['osx-CFBundleVersion'] = process.env.BUILD_NUMBER;
            obj['widget']['$']['version'] = process.env.BUILD_VERSION;

            var builder = new xml2js.Builder();
            xml = builder.buildObject(obj);
            fs.writeFile('./config.xml', xml, function() {
                console.log('* Updated config.xml');
            });
        });
    });
}



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
    PRODUCTION: production,
    // HEARTSTEPS_URL: (production) ? '/api' : 'http://localhost:8080/api',
    HEARTSTEPS_URL: (production) ? '/api' : ((LOCAL) ? 'http://localhost:8080/api' : 'https://dev.heartsteps.net/api'),
    FCM_SENDER_ID: 'firebase-id', // kpwhri heartsteps firebase ID
    ONESIGNAL_APP_ID: 'onesignal-app-id',
    PUSH_NOTIFICATION_DEVICE_TYPE: 'onesignal',
    BUILD_PLATFORM: 'website',
    BUILD_VERSION: BUILD_VERSION,
    BUILD_NUMBER: BUILD_NUMBER,
    BUILD_DATE: BUILD_DATE
});

webpackConfig.dev.plugins.push(envs);
webpackConfig.prod.plugins.push(envs);



module.exports = function() {
    return webpackConfig;
};