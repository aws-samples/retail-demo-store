export const demoWalkthroughShown = {
  state: () => ({ shown: false }),
  mutations: {
    setDemoWalkthroughShown: (state, newVisited) => (state.shown = newVisited),
  },
  actions: {
    markDemoWalkthroughAsShown: ({ commit }) => commit('setDemoWalkthroughShown', true),
  },
};
