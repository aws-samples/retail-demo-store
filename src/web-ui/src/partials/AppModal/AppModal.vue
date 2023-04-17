<template>
  <component v-if="component" :is="component"></component>
</template>

<script>
import { mapState } from 'vuex';

import DemoGuide from './DemoGuide/DemoGuide.vue';
import DemoWalkthrough from './DemoWalkthrough/DemoWalkthrough.vue';
import ShopperSelectModal from './ShopperSelectModal/ShopperSelectModal.vue';
import { Modals } from './config';

export default {
  name: 'AppModal',
  computed: {
    ...mapState({
      component: (state) => {
        if (!state.modal.openModal) return null;

        switch (state.modal.openModal.name) {
          case Modals.DemoGuide:
            return DemoGuide;
          case Modals.DemoWalkthrough:
            return DemoWalkthrough;
          case Modals.ShopperSelect:
            return ShopperSelectModal;
          default:
            throw new Error('Invalid modal name');
        }
      },
    }),
  },
};
</script>
