// import { ClientelingModals } from "@/partials/ClientelingModal/config";


export const clientelingModal = {
  state: () => ({ name: null, product: null }),
  mutations: {
    setClientelingModal: (state, { name, product }) => {
      state.name = name;
      state.product = product
    },
  },
  actions: {
    openClientelingModal: ({ commit }, {name, product}) => commit('setClientelingModal', { name, product }),
    closeClientelingModal: ({ commit }) => commit('setClientelingModal', { name: null }),
  },
};
