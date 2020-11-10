export const welcomePageVisited = {
  state: () => ({ visited: false }),
  mutations: {
    setVisitedWelcomePage: (state, newVisited) => (state.visited = newVisited),
  },
  actions: {
    welcomePageVisited: ({ commit }) => commit('setVisitedWelcomePage', true),
  },
};
