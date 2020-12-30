<template>
  <ConfirmationModalLayout>
    <template v-if="isError">
      <h1 class="heading mb-3">Something went wrong while sending an abandoned shopping cart email.</h1>

      <p class="mb-3">
        Please try again.
      </p>
    </template>

    <template v-else>
      <h1 class="heading mb-3">An abandoned shopping cart email {{ complete ? 'was sent' : 'is in progress' }}.</h1>

      <p class="mb-3">
        <template v-if="complete">
          Check the email account provided during account creation. An email from the Retail Demo Store will be in your
          inbox. The goal of this email is to encourage shoppers to complete the order and will include the products
          left in the shopping cart.
        </template>

        <LoadingFallback v-else></LoadingFallback>
      </p>
    </template>
  </ConfirmationModalLayout>
</template>

<script>
import { mapState } from 'vuex';

import ConfirmationModalLayout from '../ConfirmationModalLayout/ConfirmationModalLayout';
import LoadingFallback from '@/components/LoadingFallback/LoadingFallback';

export default {
  name: 'AbandonCartModal',
  components: { ConfirmationModalLayout, LoadingFallback },
  computed: {
    ...mapState({
      complete: (state) => state.confirmationModal.progress === 100,
      isError: (state) => state.confirmationModal.isError,
    }),
  },
};
</script>

<style scoped>
.heading {
  font-size: 1.5rem;
}
</style>
