<template>
  <ModalLayout @closeModal="this.closeConfirmationModal" :name="this.name">
    <Progress class="mb-4"></Progress>
    <slot></slot>
  </ModalLayout>
</template>

<script>
import { mapState, mapActions } from 'vuex';

import Progress from '../Progress/Progress';
import ModalLayout from "@/partials/ModalLayout/ModalLayout";

export default {
  name: 'ConfirmationModalLayout',
  components: {ModalLayout, Progress },
  computed: {
    ...mapState({ name: (state) => state.confirmationModal.name }),
  },
  methods: {
    ...mapActions(['closeConfirmationModal']),
  },
};
</script>

