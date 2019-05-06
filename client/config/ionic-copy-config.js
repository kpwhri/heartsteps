var ionic_copy_config = require('@ionic/app-scripts/config/copy.config');

ionic_copy_config.copyIndexContent.src.push('{{SRC}}/firebase-messaging-sw.js');

module.exports = ionic_copy_config;
