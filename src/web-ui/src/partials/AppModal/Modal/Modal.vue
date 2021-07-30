<template>
  <div
    class="modal fade text-left"
    ref="modal"
    :id="APP_MODAL_ID"
    tabindex="-1"
    role="dialog"
    :aria-labelledby="ariaLabelledBy"
    aria-hidden="true"
  >
    <div class="modal-dialog" role="document">
      <div class="modal-content">
        <slot v-if="showHeader" name="header"><ModalHeader></ModalHeader></slot>

        <slot name="body" bodyClass="modal-body"></slot>
      </div>
    </div>
  </div>
</template>

<script>
import { mapState, mapActions } from 'vuex';

import ModalHeader from './ModalHeader/ModalHeader';
import { APP_MODAL_ID } from '../config';

export default {
  name: 'Modal',
  components: { ModalHeader },
  props: {
    ariaLabelledBy: { type: String, required: false },
    showHeader: { type: Boolean, default: true },
  },
  data() {
    return { APP_MODAL_ID };
  },
  computed: {
    ...mapState({ isMobile: (state) => state.modal.isMobile }),
  },
  watch: {
    isMobile() {
      this.handleMobileState();
    },
  },
  methods: {
    ...mapActions(['closeModal']),
    handleMobileState() {
      // toggling the class using vue's object syntax in the template causes the modal to disappear when isMobile changes for some reason
      this.$refs.modal.classList[this.isMobile ? 'add' : 'remove']('modal--mobile');
    },
  },
  mounted() {
    // keep bootstrap modal visibility in sync with state
    // eslint-disable-next-line no-undef
    $(`#${APP_MODAL_ID}`).on('hidden.bs.modal', this.closeModal);

    this.handleMobileState();
  },
};
</script>

<style scoped>
.modal--mobile .modal-content {
  height: 100%;
  max-height: none;
  border-width: 0;
  border-radius: 0;
}

.modal-dialog {
  width: 95%;
  max-width: 1200px;
  height: 90%;
}

.modal--mobile .modal-dialog {
  margin: 0;
  width: auto;
  max-width: none;
  height: 100%;
  max-height: none;
}

.modal-body {
  height: 800px;
  max-height: 80vh;
}

.modal--mobile .modal-body {
  max-height: none;
}
</style>
