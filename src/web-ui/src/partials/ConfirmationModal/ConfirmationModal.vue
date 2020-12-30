<template>
  <component :is="component"></component>
</template>

<script>
import { mapState } from 'vuex';
import { ConfirmationModals } from './config';

import AbandonCart from './modals/AbandonCart';
import TextAlerts from './modals/TextAlerts';

export default {
  name: 'ConfirmationModal',
  computed: {
    ...mapState({ name: (state) => state.confirmationModal.name }),
    component() {
      if (!this.name) return null;

      switch (this.name) {
        case ConfirmationModals.AbandonCart:
          return AbandonCart;
        case ConfirmationModals.TextAlerts:
          return TextAlerts;
      }

      throw new Error('Invalid confirmation modal name');
    },
  },
};
</script>
