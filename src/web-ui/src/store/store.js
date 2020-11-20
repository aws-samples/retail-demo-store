// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0

import Vue from 'vue'
import Vuex from 'vuex'

import createPersistedState from 'vuex-persistedstate'
import { v4 as uuidv4 } from 'uuid';

Vue.use(Vuex)

const store = new Vuex.Store({
  state: {
    user: null,
    cartID: null,
    provisionalUserID: uuidv4(),
    sessionEventsRecorded: 0
  },
  mutations: {
    setLoggedOut(state) {
      state.user = null
      state.cartID = null
      state.provisionalUserID = uuidv4()
      state.sessionEventsRecorded = 0
    },
    setUser(state, user) {
      if (user && Object.prototype.hasOwnProperty.call(user, "storage")) {
        // Clear "user.storage" to prevent recursively nested user state
        // from being stored which eventually leads to exhausting local storage.
        user.storage = null
      }
      state.user = user
    },
    setCartID(state, cartID) {
      state.cartID = cartID
    },
    incrementSessionEventsRecorded(state) {
      state.sessionEventsRecorded += 1
    }
  },
  getters: {
    personalizeUserID: state => {
      return state.user ? state.user.id : state.provisionalUserID
    },
    personalizeRecommendationsForVisitor: state => {
      return state.user || (state.provisionalUserID && state.sessionEventsRecorded > 2)
    }
  },
  plugins: [createPersistedState()]
})

export default store