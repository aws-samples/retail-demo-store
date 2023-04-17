import { RepositoryFactory } from '@/repositories/RepositoryFactory';
import { AnalyticsHandler } from '@/analytics/AnalyticsHandler';

import { ConfirmationModals } from '@/partials/ConfirmationModal/config';

const UsersRepository = RepositoryFactory.get('users');

export const confirmationModal = {
  state: () => ({ name: null, progress: 0, isError: false }),
  mutations: {
    setConfirmationModal: (state, { name, progress = 0, isError = false }) => {
      state.name = name;
      state.progress = progress;
      state.isError = isError;
    },
    setProgress: (state, newProgress) => (state.progress = newProgress),
    setError: (state) => {
      state.progress = 100;
      state.isError = true;
    },
  },
  actions: {
    triggerAbandonedCartEmail: async ({ commit, rootState }) => {
      commit('setConfirmationModal', { name: ConfirmationModals.AbandonCart });

      const { cart } = rootState.cart;
      const { user } = rootState;

      if (cart && cart.items.length > 0) {
        try {


          commit('setProgress', 20);

          await AnalyticsHandler.recordAbanonedCartEvent(user, cart);

          commit('setProgress', 100);
        } catch {
          commit('setError');
        }
      } else {
        console.error('No items to export');
      }
    },

    triggerTextAlerts: async ({ commit, dispatch, rootState }, phoneNumber) => {
      commit('setConfirmationModal', { name: ConfirmationModals.TextAlerts });

      try {
        const { data } = await UsersRepository.verifyAndUpdateUserPhoneNumber(rootState.user.id, `${phoneNumber}`);

        dispatch('setUser', data);

        commit('setProgress', 100);
      } catch {
        commit('setError');
      }
    },

    openConfirmationModal: ({ commit }, name) => commit('setConfirmationModal', { name }),
    closeConfirmationModal: ({ commit }) => commit('setConfirmationModal', { name: null }),
  },
};
