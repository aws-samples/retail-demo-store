<template>
  <ConfirmationModalLayout>
    <h1 class="heading mb-3">Text alert notification</h1>

    <p v-if="isError" class="mb-3">
      Something went wrong while trying to opt into receiving text alerts via SMS. Please try again.
    </p>

    <template v-else>
      <p class="mb-3">
        You just opted in to receive text alerts via SMS. A text message has been sent to the number you entered.
      </p>

      <p class="mb-3">
        Reply "Y" to confirm. Next, you'll receive one text message with one personalized product recommendation. the
        message will include a URL that will redirect you to the Retail Demo Store.
      </p>
    </template>
  </ConfirmationModalLayout>
</template>

<script>
import { mapState } from 'vuex';
import ConfirmationModalLayout from '../ConfirmationModalLayout/ConfirmationModalLayout';

export default {
  name: 'TextAlertsModal',
  components: { ConfirmationModalLayout },
  computed: {
    ...mapState({ isError: (state) => state.confirmationModal.isError }),
  },
};
</script>

<style scoped>
.heading {
  font-size: 1.5rem;
}
</style>
