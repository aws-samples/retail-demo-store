<template>
  <ConfirmationModalLayout>
    <h1 class="heading mb-3">Text alert notification</h1>
    <p class="mb-3">
      You just opted in to receive text alerts via SMS. A text message has been sent to the number you entered.
    </p>

    <p class="mb-3">
      Reply "Y" to confirm. Next, you'll receive one text message with one personalized product recommendation. the
      message will include a URL that will redirect you to the Retail Demo Store.
    </p>
  </ConfirmationModalLayout>
</template>

<script>
import ConfirmationModalLayout from '../ConfirmationModalLayout/ConfirmationModalLayout';

export default {
  name: 'TextAlertsModal',
  components: { ConfirmationModalLayout },
};
</script>

<style scoped>
.heading {
  font-size: 1.5rem;
}
</style>
