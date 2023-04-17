<template>
  <section v-if="isPinpointEnabled && user" class="section container p-4">
    <h1 class="heading mb-1">Join <span class="text-alerts">text alerts</span> and get 20% off</h1>
    <p class="mb-3">
      Enter your mobile number to receive texts about the Retail Demo Store, including Amazon Pinpoint.
    </p>
    <form @submit.prevent="onSubmit" class="mb-2 form">
      <div class="mb-2 d-flex justify-content-center align-items-stretch">
        <input
          v-maska data-maska="['+# (###) ### - ####', '+## (###) ### - ####']"
          name="phoneNumber"
          id="phoneNumber"
          v-model="phoneNumber"
          type="tel"
          class="input py-1 px-2"
        />
        <button type="submit" class="submit btn" :disabled="!hasConsented">Submit</button>
      </div>

      <div class="consent d-flex align-items-start text-left">
        <input type="checkbox" class="consent-checkbox mr-2" id="text-alerts-consent" v-model="hasConsented" />
        <label class="" for="text-alerts-consent"
          >I consent to receive automated text messages (including marketing messages) from or on behalf of Amazon Web
          Services about the Retail Demo Store, including Amazon Pinpoint, at my mobile number above. Consent is not a
          condition of any purchase. Message and data rates may apply. Amazon Web Services will only use data entered
          for demonstrating features within the Retail Demo Store.</label
        >
      </div>

      <DemoGuideBadge :article="demoGuideBadgeArticle" class="demo-guide-badge px-0 d-flex"></DemoGuideBadge>
    </form>
  </section>
</template>

<script>
import { mapActions, mapState } from 'vuex';
import { vMaska } from "maska"

import DemoGuideBadge from '@/components/DemoGuideBadge/DemoGuideBadge.vue';
import { Articles } from '@/partials/AppModal/DemoGuide/config';

export default {
  name: 'TextAlerts',
  components: {
    DemoGuideBadge,
  },
  directives: { maska: vMaska },
  data() {
    return {
      isPinpointEnabled: import.meta.env.VITE_PINPOINT_APP_ID,
      phoneNumber: '',
      hasConsented: false,
      demoGuideBadgeArticle: Articles.SMS_MESSAGING,
    };
  },
  computed: {
    ...mapState(['user']),
  },
  methods: {
    ...mapActions(['triggerTextAlerts']),
    onSubmit() {
      const phoneNumber = this.phoneNumber;

      this.phoneNumber = '';
      this.hasConsented = false;

      this.triggerTextAlerts(phoneNumber);
    },
  },
};
</script>

<style scoped>
.section {
  border-radius: 4px;
  background: var(--grey-200);
}

.heading {
  font-size: 1.75rem;
}

.text-alerts {
  color: var(--blue-600);
}

.form {
  font-size: 1.25rem;
  max-width: 500px;
  margin: auto;
}

.input {
  flex: 1;
  border: none;
  border-style: solid;
  border-width: 2px;
  border-color: var(--grey-600);
  border-right: none;
  border-top-left-radius: 4px;
  border-bottom-left-radius: 4px;
  color: var(--grey-600);
  transition: border-color 150ms ease-in-out;
}

.input:focus {
  outline: none;
  border-color: var(--blue-600);
}

.submit {
  border-radius: 0;
  border-top-right-radius: 4px;
  border-bottom-right-radius: 4px;
  border-color: var(--grey-600);
  background: var(--grey-600);
  font-size: 1.25rem;
  color: var(--white);
}

.submit:hover:not([disabled]),
.submit:focus {
  background: var(--grey-900);
}

.consent {
  font-size: 0.85rem;
}

.consent-checkbox {
  /* fine-tuning for alignment */
  margin-top: 4px;
}

.demo-guide-badge {
  width: 100%;
}
</style>
