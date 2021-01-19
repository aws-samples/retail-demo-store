<template>
  <DemoWalkthroughPageLayout :drawArrows="drawArrows">
    <div :class="{ 'personalized-ranking-container d-flex': true, 'personalized-ranking-container--mobile': isMobile }">
      <div class="personalized-ranking-text">
        <h1 class="heading mb-3">
          <div ref="personalized-ranking" class="personalized-ranking pr-2 d-inline-block">Personalized Ranking</div>
        </h1>

        <p>
          The personalized ranking use-case allows you to re-order by relevance. It takes in a user AND a collection of
          items and ranks the items in order of most relevant to least based on the user’s historical and real-time
          activity.
        </p>

        <p>
          This is great for promoting a pre-selected collection of items and knowing what is the right thing to promote
          for a particular user.
        </p>

        <p>Personalized ranking is implemented in the “Featured" page.</p>
      </div>

      <div class="personalized-ranking-img-container">
        <img
          src="/personalized-ranking.png"
          alt=""
          ref="personalized-ranking-img"
          class="personalized-ranking-img img-fluid"
        />
      </div>
    </div>
  </DemoWalkthroughPageLayout>
</template>

<script>
import { mapState } from 'vuex';
import DemoWalkthroughPageLayout from '../DemoWalkthroughPageLayout';

export default {
  name: 'DemoWalkthroughPersonalizedRankingPage',
  components: { DemoWalkthroughPageLayout },
  computed: {
    ...mapState({ isMobile: (state) => state.modal.isMobile }),
  },
  data() {
    return {
      drawArrows: {
        desktop: [
          {
            from: { ref: 'personalized-ranking', target: 'RIGHT' },
            to: {
              ref: 'personalized-ranking-img',
              target: ({ left, top, height }) => [left, top + height * 0.18],
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
}

.personalized-ranking {
  color: var(--blue-500);
}

.personalized-ranking-container {
  height: 100%;
}

.personalized-ranking-text {
  flex: 1;
}

.personalized-ranking-img-container {
  margin-left: 16px;
  width: 55%;
}

.personalized-ranking-img {
  width: 100%;
}

.personalized-ranking-container--mobile {
  flex-direction: column;
  height: auto;
}

.personalized-ranking-container--mobile .personalized-ranking-img-container {
  margin-left: 0;
  width: 90%;
  align-self: center;
}
</style>
