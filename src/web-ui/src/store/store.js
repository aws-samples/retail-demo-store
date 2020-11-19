// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0

import Vue from 'vue';
import Vuex from 'vuex';

import createPersistedState from 'vuex-persistedstate';

import { welcomePageVisited } from './modules/welcomePageVisited/welcomePageVisited';
import { categories } from './modules/categories/categories';
import { cart } from './modules/cart/cart';

Vue.use(Vuex);

const store = new Vuex.Store({
  modules: { welcomePageVisited, categories, cart },
  state: {
    user: null,
  },
  mutations: {
    setLoggedOut(state) {
      state.user = null;
    },
    setUser(state, user) {
      if (user && Object.prototype.hasOwnProperty.call(user, 'storage')) {
        // Clear "user.storage" to prevent recursively nested user state
        // from being stored which eventually leads to exhausting local storage.
        user.storage = null;
      }
      state.user = user;
    },
  },
  getters: {
    username: (state) => state.user?.username ?? 'guest',
  },
  actions: {
    logout: ({ commit, dispatch }) => {
      commit('setLoggedOut');
      dispatch('getNewCart');
    },
  },
  plugins: [createPersistedState()],
  strict: process.env.NODE_ENV !== 'production',
});

export default store;
