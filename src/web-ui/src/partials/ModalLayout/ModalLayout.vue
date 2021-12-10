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

          <slot></slot>

          <button v-if="showCloseButton" class="close-modal btn btn-outline-primary" @click="closeModal">Close</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>


export default {
  name: 'ModalLayout',
  props: {
    name: {
      type: String,
      required: true
    },
    showCloseButton: {
      type: Boolean,
      default: true
    }
  },
  methods: {
    closeModal () {
      this.$emit('closeModal')
    }
  },
  mounted() {
    // eslint-disable-next-line no-undef
    $(this.$refs.modal).modal('show');

    // eslint-disable-next-line no-undef
    $(this.$refs.modal).on('hidden.bs.modal', this.closeModal);
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
