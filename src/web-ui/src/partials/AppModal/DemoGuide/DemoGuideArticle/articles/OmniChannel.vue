<template>
  <ArticleLayout>
    <template #heading>Omni-Channel Personalization & ML Model Retraining</template>

    <p>
      By connecting Amazon Pinpoint with Amazon Personalize (or other ML services), organizations can take their
      customers’ interactions across channels and feed them into their foundational Personalization models for
      omni-channel ML model retraining.
    </p>

    <p class="digital-interactions">
      This enables organizations to utilize all of their customers’ digital interactions within a centralized ML model
      to get smarter, faster. This also enables organizations to deliver personalized experiences in an omni-channel
      fashion, meaning the experiences are harmonized and responsive across their channels of engagement.
    </p>

    <ArticleFeature>
      <template #title>Case Study</template>

      <template #default>
        <div :class="{ 'd-flex align-items-center': true, 'logo-and-quote--mobile': isMobile }">
          <div class="dominos"><img src="/dominos.png" alt="" class="img-fluid" /></div>
          <p class="dominos-text">
            Domino's Pizza Enterprises Ltd (DPE) is one of the largest pizza businesses in the world; their vision is to
            be the leader in deliveries in every neighborhood.
          </p>
        </div>

        <Quote>
          <template #quote>
            "The customer is at the heart of everything we do at Domino's and we are working relentlessly to improve and
            enhance their experience. Using Amazon Personalize, we are able to achieve personalization at scale across
            our entire customer base, which was previously impossible. Amazon Personalize enables us to apply context
            about individual customers and their circumstances, and deliver customized communications such as special
            deals and offers through our digital channels."
          </template>

          <template #attribution>
            <div>Allan Collins, Group Chief Marketing Officer</div>
            <div>Domino's Pizza Enterprises</div>
          </template>
        </Quote>

        <p class="mb-0">
          Read full Domino's Pizza’s case study:
          <a
            href="https://aws.amazon.com/solutions/case-studies/dominos-case-study/"
            target="_blank"
            rel="noreferrer noopener"
            >Domino’s Pizza Enterprises Delivers in Record Time Using AWS for Predictive Ordering</a
          >
        </p>
      </template>
    </ArticleFeature>
  </ArticleLayout>
</template>

<script>
import { mapState } from 'vuex';

import ArticleLayout from '../ArticleLayout';
import ArticleFeature from '../ArticleFeature/ArticleFeature';
import Quote from '../Quote/Quote';

export default {
  name: 'OmniChannel',
  components: { ArticleLayout, ArticleFeature, Quote },
  computed: { ...mapState({ isMobile: (state) => state.modal.isMobile }) },
};
</script>

<style scoped>
.digital-interactions {
  margin-bottom: 9rem;
}

.logo-and-quote--mobile {
  margin-bottom: 20px;
  flex-direction: column;
}

.logo-and-quote--mobile .dominos {
  width: auto;
  max-width: 300px;
}

.dominos {
  width: 220px;
}

.dominos-text {
  flex: 1;
}
</style>
