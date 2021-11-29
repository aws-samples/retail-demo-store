<template>
  <component :is="component"></component>
</template>

<script>
import { mapState } from 'vuex';
import { ClientelingModals } from './config';

import ShareProduct from "@/partials/ClientelingModal/modals/ShareProduct";

export default {
  name: 'ClientelingModal',
  computed: {
    ...mapState({ name: (state) => state.clientelingModal.name }),
    component() {
      if (!this.name) return null;

      switch (this.name) {
        case ClientelingModals.ShareProduct:
          return ShareProduct;
      }

      throw new Error('Invalid clienteling modal name');
    },
  },
};
</script>