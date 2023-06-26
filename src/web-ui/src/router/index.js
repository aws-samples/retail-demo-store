// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0

import { createRouter,  createWebHistory} from 'vue-router'

import { Hub } from 'aws-amplify';
import { Auth } from 'aws-amplify';
import AmplifyStore from '@/store/store';

import { RepositoryFactory } from '@/repositories/RepositoryFactory'
import { AnalyticsHandler } from '@/analytics/AnalyticsHandler'

import { Credentials } from '@aws-amplify/core';
import store from '../store/store'

const UsersRepository = RepositoryFactory.get('users')

// Load User
// eslint-disable-next-line
getUser().then((_user, error) => {
  if (error) {
    // eslint-disable-next-line
    console.log(error)
  }
})

function getCognitoUser() {
  return Auth.currentAuthenticatedUser().then((cognitoUser) => {
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
const authListener = async (data) => {
  switch (data.payload.event) {
    case 'signOut':
      AmplifyStore.dispatch('logout');
      AnalyticsHandler.clearUser()

      if (router.currentRoute.path !== '/') router.push({ path: '/' })
      break;
    case 'signIn': {
      const cognitoUser = await getCognitoUser()

      let storeUser = null

      const hasAssignedShopperProfile = !!cognitoUser.attributes?.['custom:profile_user_id'];

      if (hasAssignedShopperProfile) {
        const { data } = await UsersRepository.getUserByID(cognitoUser.attributes['custom:profile_user_id'])
        storeUser = data
      }
      else {
        // Perhaps our auth user is one without an associated "profile" - so there may be no profile_user_id on the
        // cognito record - so we see if we've created a user in the user service (see below) for this non-profile user
        const { data } = await UsersRepository.getUserByUsername(cognitoUser.username)
        storeUser = data
      }

      const credentials = await Credentials.get();

      if (!storeUser.id) {
        // Store user does not exist. Create one on the fly.
        // This takes the personalize User ID which was a UUID4 for the current session and turns it into a user user ID.
        console.log('store user does not exist for cognito user... creating on the fly')
        let identityId = credentials ? credentials.identityId : null;
        let provisionalUserId = AmplifyStore.getters.personalizeUserID;
        const { data } = await UsersRepository.createUser(provisionalUserId, cognitoUser.username, cognitoUser.attributes.email, identityId)
        storeUser = data
      }

      console.log('Syncing store user state to cognito user custom attributes')
      // Store user exists. Use this as opportunity to sync store user
      // attributes to Cognito custom attributes.
      Auth.updateUserAttributes(cognitoUser, {
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
      break;
    }
  }
};
Hub.listen('auth', authListener);

const userListener = async (data) => {
  switch (data.payload.event) {
    case 'profileChanged': {
      const cognitoUser = await getCognitoUser()
      const storeUser = AmplifyStore.state.user

      if (cognitoUser && storeUser) {
        // Store user exists. Use this as opportunity to sync store user
        // attributes to Cognito custom attributes.
        Auth.updateUserAttributes(cognitoUser, {
          'custom:profile_user_id': storeUser.id.toString(),
          'custom:profile_email': storeUser.email,
          'custom:profile_first_name': storeUser.first_name,
          'custom:profile_last_name': storeUser.last_name,
          'custom:profile_gender': storeUser.gender,
          'custom:profile_age': storeUser.age.toString(),
          'custom:profile_persona': storeUser.persona
        })
      }

      // Sync identityId with user to support reverse lookup.
      const credentials = await Credentials.get();
      if (credentials && storeUser.identity_id != credentials.identityId) {
        console.log('Syncing credentials identity_id with store user profile')        
        store.commit('setIdentityId',credentials.identityId)
        UsersRepository.updateUser(storeUser)
      }
      break;
    }
  }
}
Hub.listen('user', userListener);

// Get store user from local storage, making sure session is authenticated
async function getUser() {
  const cognitoUser = await getCognitoUser()
  if (!cognitoUser) {
    AmplifyStore.commit('setUser', null);
  }

  return AmplifyStore.state.user;
}

const Main = () => import('@/public/Main.vue')
const Welcome = () => import('@/public/Welcome.vue')
const ProductDetail = () => import('@/public/ProductDetail.vue')
const CategoryDetail = () => import('@/public/CategoryDetail.vue')
const Live = () => import('@/public/Live.vue')
const Help = () => import('@/public/Help.vue')
const Cart = () => import('@/public/Cart.vue')
const AuthScreen = () => import('@/public/Auth.vue')
const Checkout = () => import('@/public/Checkout.vue')
const Location = () => import('@/public/Location.vue')
const Collections = () => import('@/public/Collections.vue')
const Orders = () => import('@/authenticated/Orders.vue')
const Admin = () => import('@/authenticated/Admin.vue')
const ShopperSelectPage = () => import('@/authenticated/ShopperSelectPage.vue')

// Routes
const router = createRouter({
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
    },
    {
      path: '/location',
      name: 'Location',
      component: Location,
      meta: { requiresAuth: true}
    },
    {
      path: '/collections',
      name: 'Collections',
      component: Collections,
      meta: { requiresAuth: true}
    }
  ],
  history: createWebHistory(),
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