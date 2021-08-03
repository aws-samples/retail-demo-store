<template>
  <DemoWalkthroughPageLayout :drawArrows="drawArrows">
    <h1 class="heading">Overview</h1>

    <p id="overview-components">From an experience standpoint, there are two main components of this demo:</p>

    <ol aria-labelledby="overview-components">
      <li class="component">
        A fictitious online store that includes users (shoppers), products, carts and orders as well as services for
        search and recommendations. Interact with the store products and see how the product recommendations change
        based on shopper’s preferences, real-time behavior and history.
      </li>
      <li class="component">
        A demo guide that includes relevant information related to the AWS services integrated to the demo.
      </li>
    </ol>

    <div :class="{ 'figure-container': true, 'figure-container--mobile': isMobile }">
      <div class="online-store">
        <div class="arrow-text-heading">Fictitious online store</div>
        <div v-if="!isMobile">Interact with the store products and categories.</div>
      </div>

      <div ref="demo-guide" class="demo-guide">
        <div class="arrow-text-heading">Demo guide</div>
        <div v-if="!isMobile">Provides more information about the AWS services integrated into this demo.</div>
      </div>

      <div class="img">
        <img ref="img" src="/demo-walkthrough-overview.png" alt="" class="img-fluid" />
      </div>
    </div>
  </DemoWalkthroughPageLayout>
</template>

<script>
import { mapState } from 'vuex';

import DemoWalkthroughPageLayout from '../DemoWalkthroughPageLayout';

export default {
  name: 'DemoWalkthroughOverviewPage',
  components: { DemoWalkthroughPageLayout },
  data() {
    return {
      drawArrows: {
        desktop: [
          {
            from: { ref: 'demo-guide', target: 'RIGHT' },
            to: { ref: 'img', target: 'BOTTOM' },
            drawPoints: ({ fromX, fromY, toX, toY }) => [
              [fromX, fromY],
              [fromX + 20, fromY],
              [fromX + 20, toY + 20],
              [toX, toY + 20],
              [toX, toY],
            ],
          },
        ],
        mobile: [
          {
            from: { ref: 'demo-guide', target: 'RIGHT' },
            to: { ref: 'img', target: 'BOTTOM' },
            drawPoints: ({ fromX, fromY, toX, toY }) => [
              [fromX, fromY],
              [toX, fromY],
              [toX, toY],
            ],
          },
        ],
      },
    };
  },
  computed: {
    ...mapState({ isMobile: (state) => state.modal.isMobile }),
  },
};
</script>

<style scoped>
.heading {
  font-weight: normal;
  font-size: 1.75rem;
  color: var(--blue-500);
}

.component + .component {
  margin-top: 20px;
}

.figure-container {
  display: grid;
  grid-template-columns: 1fr 450px 1fr;
  grid-column-gap: 40px;
  grid-template-rows: 1fr 1fr;
  grid-template-areas:
    'OnlineStore Img .'
    'DemoGuide Img .';
}

.figure-container--mobile {
  grid-template-columns: 1fr;
  grid-template-rows: repeat(3, auto);
  grid-row-gap: 20px;
  grid-template-areas:
    'OnlineStore'
    'Img'
    'DemoGuide';
}

.online-store,
.demo-guide {
  font-size: 0.9rem;
  align-self: center;
}

.online-store {
  grid-area: OnlineStore;
}

.demo-guide {
  grid-area: DemoGuide;
}

.arrow-text-heading {
  color: var(--blue-500);
}

.img {
  grid-area: Img;
}

.figure-container--mobile .online-store,
.figure-container--mobile .demo-guide {
  font-size: 1rem;
}

.figure-container--mobile .online-store {
  padding-left: 8px;
  justify-self: center;
}

.figure-container--mobile .demo-guide {
  padding-right: 8px;
  justify-self: start;
}

.figure-container--mobile .img {
  justify-self: center;
  width: 90%;
}
</style>
