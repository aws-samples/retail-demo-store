// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0

import Vue from 'vue';
import Router from 'vue-router';
import Main from '@/public/Main.vue'
import ProductDetail from '@/public/ProductDetail.vue'
import CategoryDetail from '@/public/CategoryDetail.vue'
import Live from '@/public/Live.vue'
import Help from '@/public/Help.vue'
import Cart from '@/public/Cart.vue'
import AuthScreen from '@/public/Auth.vue'
import Checkout from '@/public/Checkout.vue'
import Welcome from '@/public/Welcome.vue'
import Orders from '@/authenticated/Orders.vue'
import Admin from '@/authenticated/Admin.vue'
import ShopperSelectPage from '@/authenticated/ShopperSelectPage'

import { AmplifyEventBus } from 'aws-amplify-vue';
import { Auth, Logger, I18n, Analytics, Interactions } from 'aws-amplify';
import { AmplifyPlugin } from 'aws-amplify-vue';
import AmplifyStore from '@/store/store';

import { RepositoryFactory } from '@/repositories/RepositoryFactory'
import { AnalyticsHandler } from '@/analytics/AnalyticsHandler'

import { Credentials } from '@aws-amplify/core';

const UsersRepository = RepositoryFactory.get('users')

Vue.use(Router);
// Explicitly add only components needed to keep deployment as small as possible
Vue.use(AmplifyPlugin, { "Auth": Auth, "Logger": Logger, "I18n": I18n, "Interactions": Interactions, "Analytics": Analytics })

// Load User
// eslint-disable-next-line
getUser().then((_user, error) => {
  if (error) {
    // eslint-disable-next-line
    console.log(error)
  }
})

function getCognitoUser() {
  return Vue.prototype.$Amplify.Auth.currentAuthenticatedUser().then((cognitoUser) => {
    if (cognitoUser && cognitoUser.signInUserSession) {
      return cognitoUser
    }
  }).catch((error) => {
    // eslint-disable-next-line
    console.log('Error getting current authd cognito user: ' + error)
    return null
  });
}

// Event Handles for Authentication
AmplifyEventBus.$on('authState', async (state) => {
  if (state === 'signedOut') {
    AmplifyStore.dispatch('logout');
    AnalyticsHandler.clearUser()
    
    if (router.currentRoute.path !== '/') router.push({ path: '/' })
  } 
  else if (state === 'signedIn') {
    const cognitoUser = await getCognitoUser()

    let storeUser = null

    const hasAssignedShopperProfile = !!cognitoUser.attributes?.['custom:profile_user_id'];

    if (hasAssignedShopperProfile) {
      const { data } = await UsersRepository.getUserByID(cognitoUser.attributes['custom:profile_user_id'])
      storeUser = data
    }
    else {
      const { data } = await UsersRepository.getUserByUsername(cognitoUser.username)
      storeUser = data
    }

    const credentials = await Credentials.get();

    if (!storeUser.id) {
      // Store user does not exist. Create one on the fly.
      console.log('store user does not exist for cognito user... creating on the fly')
      let identityId = credentials ? credentials.identityId : null;
      let provisionalUserId = AmplifyStore.getters.personalizeUserID;
      const { data } = await UsersRepository.createUser(provisionalUserId, cognitoUser.username, cognitoUser.attributes.email, identityId)
      storeUser = data
    }

    console.log('Syncing store user state to cognito user custom attributes')
    // Store user exists. Use this as opportunity to sync store user 
    // attributes to Cognito custom attributes.
    await Vue.prototype.$Amplify.Auth.updateUserAttributes(cognitoUser, {
      'custom:profile_user_id': storeUser.id.toString(),
      'custom:profile_email': storeUser.email,
      'custom:profile_first_name': storeUser.first_name,
      'custom:profile_last_name': storeUser.last_name,
      'custom:profile_gender': storeUser.gender,
      'custom:profile_age': storeUser.age.toString(),
      'custom:profile_persona': storeUser.persona
    })

    // Sync identityId with user to support reverse lookup.
    if (credentials && storeUser.identity_id != credentials.identityId) {
      console.log('Syncing credentials identity_id with store user profile')
      storeUser.identity_id = credentials.identityId
    }
    
    // Update last sign in and sign up dates on user.
    let newSignUp = false

    const now = new Date()
    storeUser.last_sign_in_date = now.toISOString()

    if (!storeUser.sign_up_date) {
      storeUser.sign_up_date = now.toISOString()
      newSignUp = true
    }

    // Wait for identify to complete before sending sign in/up events 
    // so that endpoint is created/updated first. Impacts Pinpoint campaign timing.
    await AnalyticsHandler.identify(storeUser)
    
    // Fire sign in and first time sign up events.
    AnalyticsHandler.userSignedIn(storeUser)

    if (newSignUp) {
      AnalyticsHandler.userSignedUp(storeUser)
    }

    // Finally, update user profile with sign in/up updated dates.
    UsersRepository.updateUser(storeUser)

    AmplifyStore.commit('setUser', storeUser);

    if (newSignUp && !hasAssignedShopperProfile) {
      AmplifyStore.dispatch('firstTimeSignInDetected');
      
      router.push({path: '/shopper-select'});
    } else {
      router.push({path: '/'});
    }
  }
  else if (state === 'profileChanged') {
    const cognitoUser = await getCognitoUser()
    const storeUser = AmplifyStore.state.user

    if (cognitoUser && storeUser) {
      // Store user exists. Use this as opportunity to sync store user 
      // attributes to Cognito custom attributes.
      Vue.prototype.$Amplify.Auth.updateUserAttributes(cognitoUser, {
        'custom:profile_user_id': storeUser.id.toString(),
        'custom:profile_email': storeUser.email,
        'custom:profile_first_name': storeUser.first_name,
        'custom:profile_last_name': storeUser.last_name,
        'custom:profile_gender': storeUser.gender,
        'custom:profile_age': storeUser.age.toString(),
        'custom:profile_persona': storeUser.persona
      })
    }
  }
});

// Get store user from local storage, making sure session is authenticated
async function getUser() {
  const cognitoUser = await getCognitoUser()
  if (!cognitoUser) {
    AmplifyStore.commit('setUser', null);
  }

  return AmplifyStore.state.user;
}

// Routes
const router = new Router({
  routes: [
    {
      path: '/welcome',
      name: 'Welcome',
      component: Welcome,
      meta: { requiresAuth: false },
    },
    {
      path: '/',
      name: 'Main',
      component: Main,
      meta: { requiresAuth: false}
    },
    {
      path: '/product/:id',
      name: 'ProductDetail',
      component: ProductDetail,
      props: route => ({ discount: route.query.di === "true" || route.query.di === true}),
      meta: { requiresAuth: false}
    },  
    {
      path: '/category/:id',
      name: 'CategoryDetail',
      component: CategoryDetail,
      meta: { requiresAuth: false}
    },
    {
      path: '/live',
      name: 'Live',
      component: Live,
      meta: { requiresAuth: false}
    },
    {
      path: '/help',
      name: 'Help',
      component: Help,
      meta: { requiresAuth: false}
    },       
    {
      path: '/orders',
      name: 'Orders',
      component: Orders,
      meta: { requiresAuth: true}
    },  
    {
      path: '/cart',
      name: 'Cart',
      component: Cart,
      meta: { requiresAuth: false}
    },    
    {
      path: '/checkout',
      name: 'Checkout',
      component: Checkout,
      meta: { requiresAuth: false}
    },
    {
      path: '/admin',
      name: 'Admin',
      component: Admin,
      meta: { requiresAuth: true}
    },      
    {
      path: '/auth',
      name: 'Authenticator',
      component: AuthScreen,
    },
    {
      path: '/shopper-select',
      name: 'ShopperSelect',
      component: ShopperSelectPage,
      meta: { requiresAuth: true },
    }
  ],
  scrollBehavior (_to, _from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    } else {
      return { x: 0, y: 0 }
    }
  }
});

// Check if we need to redirect to welcome page - if redirection has never taken place and user is not authenticated
// Check For Authentication
router.beforeResolve(async (to, from, next) => {
  AmplifyStore.dispatch('pageVisited', from.fullPath);

  if (!AmplifyStore.state.welcomePageVisited.visited) {
    const user = await getUser();

    if (!user) {
      AmplifyStore.dispatch('welcomePageVisited');
      return next('/welcome');
    }
  }     

  if (to.matched.some(record => record.meta.requiresAuth)) {
    const user = await getUser();
    if (!user) {
      return next({
        path: '/auth',
        query: {
          redirect: to.fullPath,
        }
      });
    }
    return next()
  }
  return next()
})

export default router