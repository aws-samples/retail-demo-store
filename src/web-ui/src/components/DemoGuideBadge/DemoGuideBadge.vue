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
        case Articles.SIMILAR_ITEM_RECOMMENDATIONS:
          return Services.Personalize;
      }

      throw new Error('Invalid article passed to DemoGuideBadge');
    },
    serviceLogo() {
      switch (this.service) {
        case Services.Pinpoint:
          return '/pinpoint.svg';
        case Services.Personalize:
          return '/personalize.svg';
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
        case Articles.SIMILAR_ITEM_RECOMMENDATIONS:
          return 'Learn more about similar item recommendations';
        case Articles.PERSONALIZED_EMAILS:
          return 'Learn more about the abandoned shopping cart email notifications';
      }

      throw new Error('Invalid article passed to DemoGuideBadge');
    },
    poweredByService() {
      switch (this.service) {
        case Services.Pinpoint:
          return 'Amazon Pinpoint';
        case Services.Personalize:
          return 'Amazon Personalize';
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
