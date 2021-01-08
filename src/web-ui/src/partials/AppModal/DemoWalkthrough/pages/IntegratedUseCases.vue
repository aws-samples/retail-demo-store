<template>
  <DemoWalkthroughPageLayout :drawArrows="drawArrows">
    <h1 class="heading">Use cases integrated in this demo</h1>

    <p>There are three personalization use cases implemented across several places within the Retail Demo Store</p>

    <ul>
      <li>User personalization</li>
      <li>Personalized rankings</li>
      <li>Similar item recommendations</li>
    </ul>

    <section :class="{'d-flex align-items-center': true, 'user-personalization-section--mobile': isMobile}">
      <div class="user-personalization-text">
        <h2 class="user-personalization-heading mb-3">
          <span ref="user-personalization" class="user-personalization pr-2">User personalization</span>
          <div class="powered-by">powered by <span class="amazon-personalize">Amazon Personalize</span></div>
        </h2>

        <p>User personalization is implemented in the "Inspired by your shopping trends" section.</p>

        <p>Try using different shoppers to experience the difference in personalized product recommendations offered.</p>
      </div>

      <div class="personalize-img-container">
        <img src="/demo-walkthrough-overview.png" alt="" class="personalize-img img-fluid" ref="personalize-img" />
      </div>
    </section>
  </DemoWalkthroughPageLayout>
</template>

<script>
import { mapState } from 'vuex';
import DemoWalkthroughPageLayout from '../DemoWalkthroughPageLayout';

export default {
  name: 'DemoWalkthroughIntegratedUseCasesPage',
  components: { DemoWalkthroughPageLayout },
  computed: {
    ...mapState({isMobile: state => state.modal.isMobile}),
  },
  data() {
    return {
      drawArrows: {
        desktop: [
          {
            from: { ref: 'user-personalization', target: 'RIGHT' },
            to: {
              ref: 'personalize-img',
              target: ({ left, top, height }) => [left, top + height * 0.16],
            },
            drawPoints: ({ fromX, fromY, toX, toY }) => [
              [fromX, fromY],
              [fromX + (toX - fromX) * 0.8, fromY],
              [fromX + (toX - fromX) * 0.8, toY],
              [toX, toY],
            ],
          },
        ],
        mobile: [],
      },
    };
  },
};
</script>

<style scoped>
.heading {
  font-weight: normal;
  font-size: 1.75rem;
  color: var(--blue-500);
}

.user-personalization-text {
  flex: 1;
}

.personalize-img-container {
  flex: 1;
  margin-left: 16px;
}

.personalize-img {
  width: 100%;
}

.user-personalization-heading {
  font-weight: normal;
}

.user-personalization {
  font-size: 1.75rem;
}

.powered-by {
  font-size: 1.25rem;
}

.amazon-personalize {
  color: var(--blue-500);
}

.user-personalization-section--mobile {
  flex-direction: column;
}

.user-personalization-section--mobile .personalize-img-container {
  margin-left: 0;
  max-width: 90%;
}
</style>
