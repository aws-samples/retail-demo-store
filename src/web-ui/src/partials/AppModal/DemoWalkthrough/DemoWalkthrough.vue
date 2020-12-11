<template>
  <Modal :showHeader="false">
    <template #body="{bodyClass}">
      <component :is="pages[currentPageIndex]" :class="bodyClass"></component>
    </template>
  </Modal>
</template>

<script>
import { mapState } from 'vuex';

import Modal from '../Modal/Modal';
import Welcome from './pages/Welcome';
import Overview from './pages/Overview';
import Shoppers from './pages/Shoppers';
import DemoGuide from './pages/DemoGuide';
import IntegratedUseCases from './pages/IntegratedUseCases';
import PersonalizedRanking from './pages/PersonalizedRanking';
import SimilarItemRecommendations from './pages/SimilarItemRecommendations';
import Pinpoint from './pages/Pinpoint';

export default {
  name: 'DemoWalkthrough',
  components: {
    Modal,
  },
  data() {
    return {
      pages: [
        Welcome,
        Overview,
        Shoppers,
        DemoGuide,
        IntegratedUseCases,
        PersonalizedRanking,
        SimilarItemRecommendations,
        Pinpoint,
      ],
    };
  },
  computed: {
    ...mapState({ currentPageIndex: (state) => state.modal.openModal.pageIndex }),
  },
};
</script>
