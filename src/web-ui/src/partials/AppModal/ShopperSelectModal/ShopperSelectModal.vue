<template>
  <Modal>
    <template #body="{bodyClass}">
      <ShopperSelect
        :class="['shopper-select-page', bodyClass, isMobile ? 'shopper-select-page--mobile' : '']"
        @profileSwitched="onProfileSwitch"
      ></ShopperSelect>
    </template>
  </Modal>
</template>

<script>
import Modal from '../Modal/Modal';
import ShopperSelect from '@/partials/ShopperSelect/ShopperSelect';
import { APP_MODAL_ID } from '../config';
import { mapState } from 'vuex';

export default {
  name: 'ShopperSelectModal',
  components: { Modal, ShopperSelect },
  computed: {
    ...mapState({ isMobile: (state) => state.modal.isMobile }),
  },
  methods: {
    onProfileSwitch() {
      // eslint-disable-next-line no-undef
      $(`#${APP_MODAL_ID}`).modal('hide');
    },
  },
};
</script>

<style scoped>
.shopper-select-page {
  overflow: auto;
  padding: 16px 48px;
}

.shopper-select-page--mobile {
  padding: 16px;
  padding-top: 0px;
}
</style>
