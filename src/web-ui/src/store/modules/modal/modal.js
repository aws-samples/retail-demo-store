import { sections } from '@/partials/AppModal/DemoGuide/config';
import { isMobileModalMediaQueryList, APP_MODAL_ID, Modals } from '@/partials/AppModal/config';

export const modal = {
  state: () => ({
    isMobile: isMobileModalMediaQueryList.matches,
    // {name: Modals, ...metadata} | null
    openModal: null,
  }),
  mutations: {
    setIsMobile: (state, isMobile) => (state.isMobile = isMobile),
    setOpenModal: (state, newOpenModal) => (state.openModal = newOpenModal),
    setSelectedArticle: (state, articleId) => {
      if (state.openModal?.name === Modals.DemoGuide) state.openModal.selectedArticle = articleId;
    },
  },
  actions: {
    toggleIsMobile: ({ commit, state }) => commit('setIsMobile', !state.isMobile),

    openModal: ({ commit }, name) => {
      switch (name) {
        case Modals.DemoGuide: {
          // not having an article selected with demo guide open is only possible on mobile
          const selectedArticle = isMobileModalMediaQueryList.matches ? null : sections[0].articles[0];

          commit('setOpenModal', { name, selectedArticle });
          break;
        }

        case Modals.DemoWalkthrough:
          commit('setOpenModal', { name, pageIndex: 0 });
          break;

        case Modals.ShopperSelect:
          commit('setOpenModal', { name });
          break;

        default:
          throw new Error('Invalid modal name');
      }

      // show bootstrap modal
      // eslint-disable-next-line no-undef
      setTimeout(() => $(`#${APP_MODAL_ID}`).modal('show'), 0);
    },
    closeModal: ({ commit }) => commit('setOpenModal', null),
    selectArticle: ({ commit }, articleId) => commit('setSelectedArticle', articleId),
    selectFirstDemoGuideArticle: ({ commit }) => commit('setSelectedArticle', sections[0].articles[0]),
    closeArticle: ({ commit }) => commit('setSelectedArticle', null),
    demoGuideBadgeClicked: ({ commit }, article) => {
      commit('setOpenModal', { name: Modals.DemoGuide, selectedArticle: article });
      // show bootstrap modal
      // eslint-disable-next-line no-undef
      setTimeout(() => $(`#${APP_MODAL_ID}`).modal('show'), 0);
    },
    prevTourPage: ({ commit, state }) => {
      if (state.openModal?.name === Modals.DemoWalkthrough && state.openModal.pageIndex > 0)
        commit('setOpenModal', { name: Modals.DemoWalkthrough, pageIndex: state.openModal.pageIndex - 1 });
    },
    nextTourPage: ({ commit, state }) => {
      if (state.openModal?.name === Modals.DemoWalkthrough)
        commit('setOpenModal', { name: Modals.DemoWalkthrough, pageIndex: state.openModal.pageIndex + 1 });
    },
  },
};

export const manageResponsiveModalState = (store) => {
  isMobileModalMediaQueryList.addEventListener('change', () => {
    const { modal } = store.state;

    // select first demo guide article if we are in desktop mode, demo guide is open, and no article is selected
    // must take place before isMobile state is toggled
    if (
      !isMobileModalMediaQueryList.matches &&
      modal.openModal?.name === Modals.DemoGuide &&
      !modal.openModal.selectedArticle
    )
      store.dispatch('selectFirstDemoGuideArticle');

    store.dispatch('toggleIsMobile');
  });
};
