export const lastVisitedPage = {
  state: () => ({ route: null }),
  mutations: {
    setLastVisitedPage: (state, newRoute) => (state.route = newRoute),
  },
  actions: {
    pageVisited: ({ commit }, newRoute) => commit('setLastVisitedPage', newRoute),
  },
};
