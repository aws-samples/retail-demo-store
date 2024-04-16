// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0
import { createApp } from 'vue'
import App from './App.vue'
import router from './router';
import { Auth, Logger, Analytics, Interactions, AmazonPersonalizeProvider, Storage } from 'aws-amplify';
import store from '@/store/store';
import Amplitude from 'amplitude-js'
import mParticle from '@mparticle/web-sdk';
import AmplifyStore from '@/store/store';
import VueGtag from "vue-gtag";

import './styles/tokens.css'

// Base configuration for Amplify
const amplifyConfig = {
  Auth: {
      identityPoolId: import.meta.env.VITE_AWS_IDENTITY_POOL_ID,
      region: import.meta.env.VITE_AWS_REGION,
      identityPoolRegion: import.meta.env.VITE_AWS_REGION,
      userPoolId: import.meta.env.VITE_AWS_USER_POOL_ID,
      userPoolWebClientId: import.meta.env.VITE_AWS_USER_POOL_CLIENT_ID,
      mandatorySignIn: false,
  },
  Analytics: {
    disabled: typeof import.meta.env.VITE_PINPOINT_APP_ID == 'undefined',
    autoSessionRecord: true,
    AWSPinpoint: {
      appId: import.meta.env.VITE_PINPOINT_APP_ID,
      region: import.meta.env.VITE_PINPOINT_REGION,
      mandatorySignIn: false,
    }
  },
  Interactions: {
    bots: {
      "RetailDemoStore": {
        "name": import.meta.env.VITE_BOT_NAME,
        "alias": import.meta.env.VITE_BOT_ALIAS,
        "region": import.meta.env.VITE_BOT_REGION,
      },
    }   
  },
  Storage: {
    AWSS3: {
      bucket: import.meta.env.VITE_ROOM_IMAGES_BUCKET,
      region: import.meta.env.VITE_AWS_REGION, 
    }
  }
}
Storage.configure(amplifyConfig)

if (AmplifyStore.state.user?.id) {
    amplifyConfig.Analytics.AWSPinpoint.endpoint = {
        userId: AmplifyStore.state.user.id
    }
}

// Only add Personalize event tracking if configured.
if (import.meta.env.VITE_PERSONALIZE_TRACKING_ID && import.meta.env.VITE_PERSONALIZE_TRACKING_ID != 'NONE') {
  // Amazon Personalize event tracker.
  Analytics.addPluggable(new AmazonPersonalizeProvider());

  amplifyConfig.Analytics.AmazonPersonalize = {
    trackingId: import.meta.env.VITE_PERSONALIZE_TRACKING_ID,
    region: import.meta.env.VITE_AWS_REGION,
    // OPTIONAL - The number of events to be deleted from the buffer when flushed.
    flushSize: 5,
    // OPTIONAL - The interval in milliseconds to perform a buffer check and flush if necessary.
    flushInterval: 2000, // 2s
  }
}

// Initialize Amplitude if a valid API key is specified.
if (import.meta.env.VITE_AMPLITUDE_API_KEY && import.meta.env.VITE_AMPLITUDE_API_KEY != 'NONE') {
  Amplitude.getInstance().init(import.meta.env.VITE_AMPLITUDE_API_KEY)
}

// Initialize mParticle if a valid API key is specified.
if (import.meta.env.VITE_MPARTICLE_API_KEY && import.meta.env.VITE_MPARTICLE_API_KEY != 'NONE') {
  const mParticleConfig = {
      isDevelopmentMode: true,
      logLevel: "verbose"
  };
  mParticle.init(import.meta.env.VITE_MPARTICLE_API_KEY, mParticleConfig);
}

// Set the configuration
Auth.configure(amplifyConfig);
Analytics.configure(amplifyConfig);
Interactions.configure(amplifyConfig);

const logger = new Logger('main')

Auth.currentAuthenticatedUser()
  .then((user) => {
    logger.debug('Current Authenticated User Info:');
    logger.debug(user);
    return Auth.currentUserInfo()
  })
  .then((user) => logger.debug(user))
  .catch(err => logger.debug(err))
  
const app = createApp(App)
app.use(router)
app.use(store)

if (import.meta.env.VITE_GOOGLE_ANALYTICS_ID && import.meta.env.VITE_GOOGLE_ANALYTICS_ID != 'NONE') {
  app.use(VueGtag, {
    config: {
      id: import.meta.env.VITE_GOOGLE_ANALYTICS_ID,
      params: {
        send_page_view: false
      }
    }
  }, router);
}
else {
  app.use(VueGtag, {
    enabled: false,
    disableScriptLoad: true
  });
}

app.mount('#app')