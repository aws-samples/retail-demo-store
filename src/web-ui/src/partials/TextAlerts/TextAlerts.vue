<template>
  <section v-if="isEnabled && user" class="section container p-4">
    <h1 class="heading mb-1">Join <span class="text-alerts">text alerts</span> and get 20% off</h1>
    <p class="disclaimer mb-2">Message and data rates may apply. See details.</p>
    <form @submit.prevent="onSubmit" class="mb-2 form d-flex justify-content-center align-items-stretch">
      <input
        type="tel"
        name="phoneNumber"
        placeholder="Enter cellphone number"
        v-model="phoneNumber"
        v-mask="'+1 (###) ### - ####'"
        class="input py-1 px-2"
      />
      <button type="submit" class="submit btn">Submit</button>
    </form>
    <DemoGuideBadge :article="demoGuideBadgeArticle"></DemoGuideBadge>
  </section>
</template>

<script>
import { mapState } from 'vuex';
import { mask } from 'vue-the-mask';

import DemoGuideBadge from '@/components/DemoGuideBadge/DemoGuideBadge';
import { Articles } from '@/partials/AppModal/DemoGuide/config';

export default {
  name: 'TextAlerts',
  directives: {
    mask,
  },
  components: { DemoGuideBadge },
  data() {
    return {
      isEnabled: process.env.VUE_APP_ENABLE_TEXT_ALERTS === 'true',
      phoneNumber: '',
      demoGuideBadgeArticle: Articles.SMS_MESSAGING,
    };
  },
  computed: {
    ...mapState(['user']),
  },
  methods: {
    onSubmit() {
      console.log(`Text alerts form submitted with phone number: ${this.phoneNumber}`);
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

.disclaimer {
  font-size: 0.8rem;
}

.text-alerts {
  color: var(--blue-600);
}

.form {
  font-size: 1.25rem;
}

.input {
  flex: 1;
  max-width: 250px;
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

.submit:hover,
.submit:focus {
  background: var(--grey-900);
}
</style>
