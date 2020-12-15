<template>
  <div v-if="pinpointEnabled && user">
    <button @click="triggerAbandonedCartEmail" class="abandoned-cart-btn btn btn-primary btn-block btn-lg mb-2">
      Trigger Abandoned Cart email
    </button>

    <div class="text-center">
      <DemoGuideBadge :article="demoGuideBadgeArticle"></DemoGuideBadge>
    </div>
  </div>
</template>

<script>
import { mapState, mapActions } from 'vuex';

import DemoGuideBadge from '@/components/DemoGuideBadge/DemoGuideBadge';

import { Articles } from '@/partials/AppModal/DemoGuide/config';

export default {
  name: 'AbandonCartButton',
  components: { DemoGuideBadge },
  data() {
    return {
      pinpointEnabled: process.env.VUE_APP_PINPOINT_APP_ID,
      demoGuideBadgeArticle: Articles.PERSONALIZED_EMAILS,
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

<style>
.abandoned-cart-btn {
  background: var(--blue-500);
  border-color: var(--blue-500);
  font-size: 1rem;
}

.abandoned-cart-btn:hover,
.abandoned-cart-btn:focus {
  background: var(--blue-600);
  border-color: var(--blue-600);
}

@media (min-width: 768px) {
  .abandoned-cart-btn {
    font-size: 1.25rem;
  }
}
</style>
