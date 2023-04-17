<template>
  <div v-if="pinpointEnabled && user" class="abandon-cart">
    <form @submit.prevent="triggerAbandonedCartEmail">
      <button type="submit" :disabled="!hasConsented" class="abandoned-cart-btn btn btn-primary btn-block btn-lg mb-2">
        Trigger Abandoned Cart email
      </button>

      <div class="consent d-flex align-items-start text-left">
        <input type="checkbox" class="consent-checkbox mr-2" id="abandon-cart-consent" v-model="hasConsented" />
        <label for="abandon-cart-consent"
          >Yes, I’d like Amazon Web Services (AWS) to share information about the Retail Demo Store, including Amazon
          Pinpoint, with me by email.</label
        >
      </div>
    </form>

    <div class="text-center">
      <DemoGuideBadge :article="demoGuideBadgeArticle" class="demo-guide-badge px-0 d-flex"></DemoGuideBadge>
    </div>
  </div>
</template>

<script>
import { mapState, mapActions } from 'vuex';

import DemoGuideBadge from '@/components/DemoGuideBadge/DemoGuideBadge.vue';

import { Articles } from '@/partials/AppModal/DemoGuide/config';

export default {
  name: 'AbandonCartButton',
  components: { DemoGuideBadge },
  data() {
    return {
      pinpointEnabled: import.meta.env.VITE_PINPOINT_APP_ID,
      demoGuideBadgeArticle: Articles.PERSONALIZED_EMAILS,
      hasConsented: false,
    };
  },
  computed: {
    ...mapState({ user: (state) => state.user }),
  },
  methods: {
    ...mapActions(['triggerAbandonedCartEmail']),
  },
};
</script>

<style scoped>
.abandoned-cart-btn {
  background: var(--blue-500);
  border-color: var(--blue-500);
  font-size: 1rem;
}

.abandoned-cart-btn:hover:not([disabled]),
.abandoned-cart-btn:focus {
  background: var(--blue-600);
  border-color: var(--blue-600);
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

@media (min-width: 768px) {
  .abandoned-cart-btn {
    font-size: 1.25rem;
  }
}
</style>
