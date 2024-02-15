<template>
  <button type="button" @click="onClick" :aria-label="copy" class="demo-guide-badge align-items-center text-left">
    <div class="logo mr-1"><img :src="serviceLogo" alt="" class="img-fluid" /></div>
    <div :class="{ text: true, 'hide-text-on-small-screens': hideTextOnSmallScreens }">
      <div>{{ copy }}</div>
      <div class="powered-by">
        powered by <span class="service">{{ poweredByService }}</span>
      </div>
    </div>
  </button>
</template>

<script>
import { mapActions } from 'vuex';

import { Articles } from '@/partials/AppModal/DemoGuide/config';

const Services = {
  Pinpoint: 'Pinpoint',
  Personalize: 'Personalize',
  Bedrock: 'Bedrock',
};

export default {
  name: 'DemoGuideBadge',
  props: {
    article: { type: String, required: true },
    hideTextOnSmallScreens: {
      type: Boolean,
      default: false,
    },
  },
  computed: {
    service() {
      switch (this.article) {
        case Articles.SMS_MESSAGING:
        case Articles.PERSONALIZED_EMAILS:
          return Services.Pinpoint;
        case Articles.USER_PERSONALIZATION:
        case Articles.PERSONALIZED_RANKING:
        case Articles.SIMS_RECOMMENDATIONS:
        case Articles.SIMILAR_ITEMS_RECOMMENDATIONS:
        case Articles.SIMILAR_ITEMS_WITH_THEME:
        case Articles.ECOMM_CUSTOMERS_WHO_VIEWED_X:
        case Articles.ECOMM_FBT:
        case Articles.ECOMM_POPULAR_BY_PURCHASES:
        case Articles.ECOMM_POPULAR_BY_VIEWS:
        case Articles.ECOMM_RFY:
          return Services.Personalize;
        case Articles.PERSONALIZED_PRODUCT:
          return Services.Bedrock;
      }

      throw new Error('Invalid article passed to DemoGuideBadge');
    },
    serviceLogo() {
      switch (this.service) {
        case Services.Pinpoint:
          return '/pinpoint.svg';
        case Services.Personalize:
          return '/personalize.svg';
        case Services.Bedrock:
          return '/bedrock.svg';
      }

      throw new Error('Invalid article passed to DemoGuideBadge');
    },
    copy() {
      switch (this.article) {
        case Articles.SMS_MESSAGING:
          return 'Learn more about personalized product recommendations via SMS';
        case Articles.USER_PERSONALIZATION:
          return 'Learn more about user personalization';
        case Articles.PERSONALIZED_RANKING:
          return 'Learn more about personalized rankings';
        case Articles.SIMS_RECOMMENDATIONS:
          return 'Learn more about similar item (SIMS) recommendations';
        case Articles.SIMILAR_ITEMS_RECOMMENDATIONS:
          return 'Learn more about similar items recommendations with personalized ranking';
        case Articles.SIMILAR_ITEMS_WITH_THEME:
          return 'Learn more about similar items with generative AI theme';
        case Articles.ECOMM_CUSTOMERS_WHO_VIEWED_X:
          return 'Learn more about customers who viewed X viewed';
        case Articles.ECOMM_FBT:
          return 'Learn more about frequently bought together';
        case Articles.ECOMM_POPULAR_BY_PURCHASES:
          return 'Learn more about most purchased';
        case Articles.ECOMM_POPULAR_BY_VIEWS:
          return 'Learn more about most viewed';
        case Articles.ECOMM_RFY:
          return 'Learn more about recommended for you';
        case Articles.PERSONALIZED_EMAILS:
          return 'Learn more about the abandoned shopping cart email notifications';
        case Articles.PERSONALIZED_PRODUCT:
          return 'Learn more about personalized product descriptions';
      }

      throw new Error('Invalid article passed to DemoGuideBadge');
    },
    poweredByService() {
      switch (this.service) {
        case Services.Pinpoint:
          return 'Amazon Pinpoint';
        case Services.Personalize:
          return 'Amazon Personalize';
        case Services.Bedrock:
          return 'Amazon Bedrock';
      }

      throw new Error('Invalid article passed to DemoGuideBadge');
    },
  },
  methods: {
    ...mapActions(['demoGuideBadgeClicked']),
    onClick() {
      this.demoGuideBadgeClicked(this.article);
    },
  },
};
</script>

<style scoped>
.demo-guide-badge {
  border: none;
  background: none;
  display: inline-flex;
}

.logo {
  width: 40px;
}

.text {
  flex: 1;
  font-size: 0.8rem;
  line-height: 1rem;
}

.powered-by {
  font-size: 0.7rem;
}

.service {
  color: var(--blue-600);
}

@media (max-width: 768px) {
  .hide-text-on-small-screens {
    display: none;
  }
}
</style>
