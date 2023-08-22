// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0

import { RepositoryFactory } from '@/repositories/RepositoryFactory';
import { parseCart } from './util';
import { formatPrice } from '@/util/formatPrice';
import { AnalyticsHandler } from '@/analytics/AnalyticsHandler';

const CartsRepository = RepositoryFactory.get('carts');

function maybeUpdateUsername (state, commit, dispatch, rootState) {
  if(state.cart.username !== rootState.username){
    console.log("Updating username from " + state.cart.username + " to " + rootState.username )
    commit({ type: 'setUsername', username: rootState.username });
    console.log("Username in state is now "+state.cart.username)
  }
}

export const cart = {
  state: () => ({ cart: null }),
  getters: {
    cartTotal: (state) => state.cart?.items.reduce((subtotal, item) => subtotal + item.quantity * item.price, 0) ?? 0,
    cartQuantity: (state) => state.cart?.items.reduce((total, item) => total + item.quantity, 0) ?? 0,
    formattedCartTotal: (state, getters) => {
      if (!state.cart) return null;

      return formatPrice(getters.cartTotal);
    },
  },
  mutations: {
    setCart: (state, { cart: newCart }) => (state.cart = newCart),
    addQuantityToItem: (state, { index, quantity }) => (state.cart.items[index].quantity += quantity),
    addItemToCart: (state, { item }) => state.cart.items.push(item),
    removeItemFromCart: (state, { index }) => state.cart.items.splice(index, 1),
    setUsername: (state, { username }) => {state.cart.username = username;}
  },
  actions: {
    createCart: async ({ commit, getters }) => {
      console.log('Creating cart with username ' + getters.username.toString())
      const { data } = await CartsRepository.createCart(getters.username);
      let newCart = parseCart(data);
      newCart.username = getters.username;
      commit({ type: 'setCart', cart: newCart });
  },

    getCart: async ({ state, commit, dispatch, getters }) => {
      // Since cart service holds carts in memory, they can be lost on restarts.
      // Make sure our cart was returned. Otherwise create a new one.
      if (!state.cart || !state.cart.id) {
        console.log('Looking up your cart by username: ' + getters.username.toString())
        const { data } = await CartsRepository.getCartByUsername(getters.username);
        if (data.length > 0) {
          commit({ type: 'setCart', cart: parseCart(data[0]) });
        } else {
          return dispatch('createCart');
        }
      } else {
        console.log('Looking up your cart by ID: ' + state.cart.id.toString())
        const { data } = await CartsRepository.getCartByID(state.cart.id);
        if (data.id !== state.cart.id) {
          console.warn(`Cart ${state.cart.id} not found. Creating new cart. Was cart service restarted?`);
          return dispatch('createCart');
        }
        commit({ type: 'setCart', cart: parseCart(data) });
        maybeUpdateUsername(state, commit, dispatch, getters);
      }
      console.log("Retrieved cart with id "+state.cart.id+" and username "+state.cart.username);
    },
  

    updateCart: async ({ state, commit, dispatch, getters }) => {
      maybeUpdateUsername(state, commit, dispatch, getters);
      const { data } = await CartsRepository.updateCart(state.cart);
      commit({ type: 'setCart', cart: parseCart(data) });
      console.log("Updated cart with id "+state.cart.id+" and username "+state.cart.username);
    },
    addToCart: async ({ state, commit, dispatch, rootState }, { product, quantity, feature, exp }) => {
      maybeUpdateUsername(state, commit, dispatch, rootState);

      const index = state.cart.items.findIndex((item) => item.product_id === product.id);

      if (index !== -1) {
        commit({ type: 'addQuantityToItem', index, quantity });
      } else {
        commit({ type: 'addItemToCart', item: { product_id: product.id, product_name: product.name, price: product.price, quantity } });
      }

      await dispatch('updateCart');

      const newQuantity = product.quantity;

      AnalyticsHandler.productAddedToCart(rootState.user, state.cart, product, newQuantity, feature, exp);
    },
    removeFromCart: async ({ state, commit, dispatch, rootState }, product_id) => {
      maybeUpdateUsername(state, commit, dispatch, rootState);

      const index = state.cart.items.findIndex((item) => item.product_id === product_id);

      if (index === -1) return;

      const removedItem = state.cart.items[index];
      commit({ type: 'removeItemFromCart', index });

      await dispatch('updateCart');

      AnalyticsHandler.productRemovedFromCart(rootState.user, state.cart, removedItem, removedItem.quantity);
    },
    increaseQuantity: async ({ state, commit, dispatch, rootState }, product_id) => {
      maybeUpdateUsername(state, commit, dispatch, rootState);

      const index = state.cart.items.findIndex((item) => item.product_id === product_id);

      if (index === -1) return;

      commit({ type: 'addQuantityToItem', index, quantity: 1 });

      await dispatch('updateCart');

      AnalyticsHandler.productQuantityUpdatedInCart(rootState.user, state.cart, state.cart.items[index], 1);
    },
    decreaseQuantity: async ({ state, commit, dispatch, rootState }, product_id) => {
      maybeUpdateUsername(state, commit, dispatch, rootState);

      const index = state.cart.items.findIndex((item) => item.product_id === product_id);

      if (index === -1) return;

      const item = state.cart.items[index];

      if (item.quantity === 1) {
        commit({ type: 'removeItemFromCart', index });
        await dispatch('updateCart');
        AnalyticsHandler.productRemovedFromCart(rootState.user, state.cart, item, item.quantity);
      } else {
        commit({ type: 'addQuantityToItem', index, quantity: -1 });
        await dispatch('updateCart');
        AnalyticsHandler.productQuantityUpdatedInCart(rootState.user, state.cart, item, -1);
      }
    },
    getNewCart: ({ commit, dispatch }) => {
      commit({ type: 'setCart', cart: null });

      dispatch('createCart');
    },
  },
};
