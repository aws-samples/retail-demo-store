// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0

import Vue from 'vue'
import App from './App.vue'
import router from './router';
import { Auth, Logger, Analytics, Interactions, AWSPinpointProvider, AmazonPersonalizeProvider } from 'aws-amplify';
import { components } from 'aws-amplify-vue'; 
import moment from 'moment'
import Amplitude from 'amplitude-js'

Vue.prototype.moment = moment

// Base configuration for Amplify
const amplifyConfig = {
  Auth: {
      identityPoolId: process.env.VUE_APP_AWS_IDENTITY_POOL_ID,
      region: process.env.VUE_APP_AWS_REGION,
      identityPoolRegion: process.env.VUE_APP_AWS_REGION,
      userPoolId: process.env.VUE_APP_AWS_USER_POOL_ID,
      userPoolWebClientId: process.env.VUE_APP_AWS_USER_POOL_CLIENT_ID,
      mandatorySignIn: false,
  },
  Analytics: {
    disabled: false,
    autoSessionRecord: true,
    AWSPinpoint: {
      appId: process.env.VUE_APP_PINPOINT_APP_ID,
      region: process.env.VUE_APP_PINPOINT_REGION,
      mandatorySignIn: false,
    }
  },
  Interactions: {
    bots: {
      "RetailDemoStore": {
        "name": process.env.VUE_APP_BOT_NAME,
        "alias": process.env.VUE_APP_BOT_ALIAS,
        "region": process.env.VUE_APP_BOT_REGION,
      },
    }
  }
}

Analytics.addPluggable(new AWSPinpointProvider());

// Only add Personalize event tracking if configured.
if (process.env.VUE_APP_PERSONALIZE_TRACKING_ID && process.env.VUE_APP_PERSONALIZE_TRACKING_ID != 'NONE') {
  // Amazon Personalize event tracker.
  Analytics.addPluggable(new AmazonPersonalizeProvider());

  amplifyConfig.Analytics.AmazonPersonalize = {
    trackingId: process.env.VUE_APP_PERSONALIZE_TRACKING_ID,
    region: process.env.VUE_APP_AWS_REGION,
    // OPTIONAL - The number of events to be deleted from the buffer when flushed.
    flushSize: 5,
    // OPTIONAL - The interval in milliseconds to perform a buffer check and flush if necessary.
    flushInterval: 2000, // 2s
  }
}

// Initialize Amplitude if a valid API key is specified.
if (process.env.VUE_APP_AMPLITUDE_API_KEY && process.env.VUE_APP_AMPLITUDE_API_KEY != 'NONE') {
  Amplitude.getInstance().init(process.env.VUE_APP_AMPLITUDE_API_KEY)
}

// Set the configuration
Auth.configure(amplifyConfig);
Analytics.configure(amplifyConfig);
Interactions.configure(amplifyConfig);

require('dotenv').config()

Vue.config.productionTip = false

Logger.LOG_LEVEL = 'DEBUG'
const logger = new Logger('main')

Auth.currentUserInfo()
  .then(user => logger.debug(user))
  .catch(err => logger.debug(err))

new Vue({  
  el: '#app',
  router: router,
  template: '<App/>',
  components: { 
    App,
    ...components
  },
  render: h => h(App)
}).$mount('#app')