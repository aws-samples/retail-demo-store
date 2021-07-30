<template>
  <div class="modal fade" tabindex="-1" role="dialog" aria-hidden="true" ref="modal">
    <div class="modal-dialog" role="document">
      <div class="modal-content">
        <div class="modal-header">
          <button type="button" class="close" data-dismiss="modal" aria-label="Close">
            <i class="fa fa-times"></i>
          </button>
        </div>

        <div class="modal-body px-5 pb-5">
          <Progress class="mb-4"></Progress>

          <slot></slot>

          <button class="close-modal btn btn-outline-primary" @click="closeConfirmationModal">Close</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { mapState, mapActions } from 'vuex';

import Progress from '../Progress/Progress';

export default {
  name: 'ConfirmationModalLayout',
  components: { Progress },
  computed: {
    ...mapState({ name: (state) => state.confirmationModal.name }),
  },
  methods: {
    ...mapActions(['closeConfirmationModal']),
  },
  mounted() {
    // eslint-disable-next-line no-undef
    $(this.$refs.modal).modal('show');

    // eslint-disable-next-line no-undef
    $(this.$refs.modal).on('hidden.bs.modal', this.closeConfirmationModal);
  },
  beforeDestroy() {
    // eslint-disable-next-line no-undef
    $(this.$refs.modal).modal('hide');
  },
  watch: {
    async name(newName) {
      // eslint-disable-next-line no-undef
      $(this.$refs.modal).modal(newName ? 'show' : 'hide');
    },
  },
};
</script>

<style scoped>
.modal-header {
  border-bottom: none;
}

.close-modal {
  width: 100%;
  max-width: 200px;
  border-color: var(--blue-500);
  color: var(--blue-500);
}

.close-modal:hover,
.close-modal:focus {
  background: var(--blue-600);
  border-color: var(--blue-600);
  color: var(--white);
}

.modal-dialog {
  max-width: 800px;
}
</style>
