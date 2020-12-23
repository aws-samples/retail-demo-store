// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0

import Vue from 'vue';
import Vuex from 'vuex';

import createPersistedState from 'vuex-persistedstate';
import { v4 as uuidv4 } from 'uuid';

import { welcomePageVisited } from './modules/welcomePageVisited/welcomePageVisited';
import { categories } from './modules/categories/categories';
import { cart } from './modules/cart/cart';
import { modal, manageResponsiveModalState } from './modules/modal/modal';
import { demoWalkthroughShown } from './modules/demoWalkthroughShown/demoWalkthroughShown';
import { lastVisitedPage } from './modules/lastVisitedPage/lastVisitedPage';
import { confirmationModal } from './modules/confirmationModal/confirmationModal';

Vue.use(Vuex);

const store = new Vuex.Store({
  modules: { welcomePageVisited, categories, cart, modal, demoWalkthroughShown, lastVisitedPage, confirmationModal },
  state: {
    user: null,
    provisionalUserID: uuidv4(),
    sessionEventsRecorded: 0,
  },
  mutations: {
    setLoggedOut(state) {
      state.user = null;
      state.provisionalUserID = uuidv4();
      state.sessionEventsRecorded = 0;
    },
    setUser(state, user) {
      if (user && Object.prototype.hasOwnProperty.call(user, 'storage')) {
        // Clear "user.storage" to prevent recursively nested user state
        // from being stored which eventually leads to exhausting local storage.
        user.storage = null;
      }
      state.user = user;
    },
    incrementSessionEventsRecorded(state) {
      state.sessionEventsRecorded += 1;
    },
  },
  getters: {
    username: (state) => state.user?.username ?? 'guest',
    personalizeUserID: (state) => {
      return state.user ? state.user.id : state.provisionalUserID;
    },
    personalizeRecommendationsForVisitor: (state) => {
      return state.user || (state.provisionalUserID && state.sessionEventsRecorded > 2);
    },
  },
  actions: {
    setUser: ({ commit }, user) => {
      commit('setUser', user);
    },
    logout: ({ commit, dispatch }) => {
      commit('setLoggedOut');
      dispatch('getNewCart');
    },
  },
  plugins: [
    createPersistedState({
      paths: [
        'user',
        'provisionalUserID',
        'sessionEventsRecorded',
        'welcomePageVisited',
        'cart',
        'demoWalkthroughShown',
        'lastVisitedPage',
      ],
    }),
  ],
  strict: process.env.NODE_ENV !== 'production',
});

manageResponsiveModalState(store);

export default store;
