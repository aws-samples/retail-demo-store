<template>
  <ConfirmationModalLayout>
    <h1 class="heading mb-3">An abandoned shopping cart email {{ complete ? 'was sent' : 'is in progress' }}</h1>
    <p class="mb-3">
      Check the email account provided during account creation. An email from the Retail Demo Store will be in your
      inbox. The goal of this email is to encourage shoppers to complete the order and will include the products left in
      the shopping cart.
    </p>
  </ConfirmationModalLayout>
</template>

<script>
import { mapState } from 'vuex';

import ConfirmationModalLayout from '../ConfirmationModalLayout/ConfirmationModalLayout';

export default {
  name: 'AbandonCartModal',
  components: { ConfirmationModalLayout },
  computed: {
    ...mapState({ complete: (state) => state.confirmationModal.progress === 100 }),
  },
};
</script>

<style scoped>
  .heading{ 
    font-size: 1.5rem;
  }
</style>
