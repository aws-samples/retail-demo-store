<template>
  <DemoWalkthroughPageLayout :drawArrows="drawArrows">
    <h1 class="heading mb-3">
      <div class="heading-similar-item-recommendations">Similar item recommendations</div>
    </h1>

    <div :class="{ content: true, 'content--mobile': isMobile }">
      <p class="similar-item-recommendations pl-2" ref="similar-item-recommendations">
        The Similar item recommendations use case is implemented in all product detail pages under the “Compare similar
        items” section.
      </p>

      <div class="img-container">
        <img src="/similar-item-recommendations.jpg" alt="" class="img img-fluid" ref="img" />
      </div>
    </div>
  </DemoWalkthroughPageLayout>
</template>

<script>
import { mapState } from 'vuex';
import DemoWalkthroughPageLayout from '../DemoWalkthroughPageLayout';

export default {
  name: 'DemoWalkthroughSimilarItemRecommendationsPage',
  components: { DemoWalkthroughPageLayout },
  computed: {
    ...mapState({ isMobile: (state) => state.modal.isMobile }),
  },
  data() {
    return {
      drawArrows: {
        desktop: [
          {
            from: { ref: 'similar-item-recommendations', target: 'LEFT' },
            to: {
              ref: 'img',
              target: ({ right, top, height }) => [right, top + height * 0.815],
            },
            drawPoints: ({ fromX, fromY, toX, toY }) => [
              [fromX, fromY],
              [fromX + (toX - fromX) * 0.5, fromY],
              [fromX + (toX - fromX) * 0.5, toY],
              [toX, toY],
            ],
          },
        ],
        mobile: [
          {
            from: { ref: 'similar-item-recommendations', target: 'RIGHT' },
            to: {
              ref: 'img',
              target: ({ right, top, height }) => [right, top + height * 0.815],
            },
            drawPoints: ({ fromX, fromY, toX, toY }) => [
              [fromX, fromY],
              [toX + 20, fromY],
              [toX + 20, toY],
              [toX, toY],
            ],
          },
        ],
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

.heading-similar-item-recommendations {
  color: var(--blue-500);
}

.content {
  display: grid;
  grid-template-columns: 1fr 1fr;
  grid-column-gap: 5%;
  grid-template-areas: 'Img Recommendations';
}

.similar-item-recommendations {
  grid-area: Recommendations;
  align-self: center;
}

.img-container {
  grid-area: Img;
  width: 100%;
  max-width: 460px;
}

.content--mobile {
  grid-template-columns: 1fr;
  grid-template-rows: auto;
  grid-template-areas:
    'Recommendations'
    'Img';
}

.content--mobile .similar-item-recommendations {
  margin-right: 60px;
}

.content--mobile .img-container {
  max-width: 650px;
  width: 90%;
  justify-self: center;
}
</style>
