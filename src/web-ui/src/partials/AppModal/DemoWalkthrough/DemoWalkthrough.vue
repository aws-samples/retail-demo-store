<template>
  <Modal :showHeader="isMobile">
    <template #header>
      <ModalHeader class="demo-walkthrough-header"></ModalHeader>
    </template>

    <template #body="{ bodyClass }">
      <component :is="pages[currentPageIndex]" :class="bodyClass"></component>
    </template>
  </Modal>
</template>

<script>
import { mapState } from 'vuex';

import Modal from '../Modal/Modal.vue';
import ModalHeader from '../Modal/ModalHeader/ModalHeader.vue';
import Welcome from './pages/Welcome.vue';
import Overview from './pages/Overview.vue';
import Shoppers from './pages/Shoppers.vue';
import DemoGuide from './pages/DemoGuide.vue';
import IntegratedUseCases from './pages/IntegratedUseCases.vue';
import PersonalizedRanking from './pages/PersonalizedRanking.vue';
import RelatedItemsRecommendations from './pages/RelatedItemsRecommendations.vue';
import Pinpoint from './pages/Pinpoint.vue';

export default {
  name: 'DemoWalkthrough',
  components: {
    Modal,
    ModalHeader,
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
        RelatedItemsRecommendations,
        Pinpoint,
      ],
    };
  },
  computed: {
    ...mapState({
      currentPageIndex: (state) => state.modal.openModal.pageIndex,
      isMobile: (state) => state.modal.isMobile,
    }),
  },
};
</script>

<style scoped>
.demo-walkthrough-header {
  border-radius: 0;
  background: var(--aws-deep-squid-ink);
}
</style>
