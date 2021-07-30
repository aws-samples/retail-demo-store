<template>
  <DemoWalkthroughPageLayout isLast>
    <h1 class="heading"><img src="/pinpoint.svg" alt="" class="pinpoint-logo mr-2" />Amazon Pinpoint</h1>

    <p>
      The Retail Demo Store allows you to showcase real time personalization based on shopping behavior across multiple
      channels of engagement (online store, email and SMS).
    </p>

    <div>
      <div :class="{ 'img-container': true, 'img-container--mobile': isMobile }">
        <img src="/pinpoint.png" alt="" class="img-fluid" />
      </div>

      <p>
        When you leave items in the shopping cart and don’t complete the order, Amazon Pinpoint will send an email (to
        the email address provided during account creation) to entice shoppers to complete the order. The email will
        include the store products left in the cart.
      </p>

      <p>
        For more information on how to demonstrate this use case during customer meetings, go to the Demo Guide and look
        for the Abandoned Shopping Cart Pinpoint use case.
      </p>

      <p>Demo Guide / use cases enabled in this demo / Pinpoint / Abandoned Cart Email</p>
    </div>
  </DemoWalkthroughPageLayout>
</template>

<script>
import { mapState } from 'vuex';
import DemoWalkthroughPageLayout from '../DemoWalkthroughPageLayout';

export default {
  name: 'DemoWalkthroughPinpointPage',
  components: { DemoWalkthroughPageLayout },
  computed: { ...mapState({ isMobile: (state) => state.modal.isMobile }) },
};
</script>

<style scoped>
.heading {
  font-weight: normal;
  font-size: 1.75rem;
  color: var(--blue-500);
}

.pinpoint-logo {
  width: 50px;
}

.img-container {
  width: 25%;
  margin-right: 16px;
  float: left;
}

.img-container--mobile {
  float: initial;
  margin: auto;
  margin-bottom: 16px;
  width: 90%;
  max-width: 500px;
}
</style>
