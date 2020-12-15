import { RepositoryFactory } from '@/repositories/RepositoryFactory';
import { AnalyticsHandler } from '@/analytics/AnalyticsHandler';

import { ConfirmationModals } from '@/partials/ConfirmationModal/config';

const ProductsRepository = RepositoryFactory.get('products');

export const confirmationModal = {
  state: () => ({ name: null, progress: 0 }),
  mutations: {
    setConfirmationModal: (state, { name, progress = 0 }) => {
      state.name = name;
      state.progress = progress;
    },
    setProgress: (state, newProgress) => (state.progress = newProgress),
  },
  actions: {
    triggerAbandonedCartEmail: async ({ commit, rootState }) => {
      commit('setConfirmationModal', { name: ConfirmationModals.AbandonCart });

      const { cart } = rootState.cart;
      const { user } = rootState;

      if (cart && cart.items.length > 0) {
        const cartItem = await ProductsRepository.getProduct(cart.items[0].product_id);

        commit('setProgress', 20);

        await AnalyticsHandler.recordAbanonedCartEvent(user, cart, cartItem);

        commit('setProgress', 100);
      } else {
        console.error('No items to export');
      }
    },

    openConfirmationModal: ({ commit }, name) => commit('setConfirmationModal', { name }),
    closeConfirmationModal: ({ commit }) => commit('setConfirmationModal', { name: null }),
  },
};
