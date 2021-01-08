<template>
  <DemoWalkthroughPageLayout :drawArrows="drawArrows">
    <h1 class="heading">Demo guide</h1>

    <p>
      The Retail Demo Store has been designed to be a stand-alone tool that provides the necessary instructions to use
      this demo without relying on external documentation. The demo guide is located at the bottom of your browser
      window (blue tab).
    </p>

    <div :class="{ images: true, 'images--mobile': isMobile }">
      <div ref="demo-guide" class="demo-guide pl-2">Demo guide</div>

      <div class="demo-guide-closed">
        <img src="/demo-walkthrough-overview.png" alt="" class="img-fluid" ref="demo-guide-closed" />
      </div>

      <div class="services">
        <div id="demo-guide-services" class="mb-2 pr-2 d-inline-block" ref="services">
          Services and use cases enabled in the Retail Demo Store demo
        </div>

        <ul aria-labelledby="demo-guide-services" class="service-list d-flex pl-0">
          <li class="service d-flex align-items-center">
            <img src="/personalize.svg" alt="" class="service-logo mr-2" />Amazon Personalize
          </li>
          <li class="service d-flex align-items-center">
            <img src="/pinpoint.svg" alt="" class="service-logo mr-2" />Amazon Pinpoint
          </li>
          <li class="service d-flex align-items-center">
            <img src="/lex.svg" alt="" class="service-logo mr-2" />Amazon Lex
          </li>
        </ul>
      </div>

      <div class="demo-guide-open"><img src="/demo-guide-open.png" alt="" class="img-fluid" ref="demo-guide-open" /></div>
    </div>
  </DemoWalkthroughPageLayout>
</template>

<script>
import { mapState } from 'vuex';
import DemoWalkthroughPageLayout from '../DemoWalkthroughPageLayout';

export default {
  name: 'DemoWalkthroughDemoGuidePage',
  components: { DemoWalkthroughPageLayout },
  computed: {
    ...mapState({ isMobile: (state) => state.modal.isMobile }),
  },
  data() {
    return {
      drawArrows: {
        desktop: [
          {
            from: { ref: 'demo-guide', target: 'LEFT' },
            to: {
              ref: 'demo-guide-closed',
              target: ({ left, width, bottom, height }) => [left + width / 2, bottom - height * 0.1],
            },
            drawPoints: ({ fromX, fromY, toX, toY }) => [
              [fromX, fromY],
              [toX, fromY],
              [toX, toY],
            ],
          },
          {
            from: { ref: 'services', target: 'RIGHT' },
            to: {
              ref: 'demo-guide-open',
              target: ({ left, width, top, height }) => [left + width * 0.05, top + height * 0.3],
            },
            drawPoints: ({ fromX, fromY, toX, toY }) => [
              [fromX, fromY],
              [fromX + (toX - fromX) / 2, fromY],
              [fromX + (toX - fromX) / 2, toY],
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

.images {
  display: grid;
  grid-gap: 10px;
  grid-template-columns: 450px 60px 1fr;
  grid-template-rows: auto auto 1fr;
  grid-template-areas:
    'DemoGuide . Open'
    'Closed . Open'
    'Services Services Open';
}

.demo-guide {
  grid-area: DemoGuide;
  justify-self: end;
  color: var(--blue-500);
}

.demo-guide-closed {
  grid-area: Closed;
}

.services {
  grid-area: Services;
}

.service-list {
  list-style-type: none;
}

.service + .service {
  margin-left: 20px;
}

.service-logo {
  width: 30px;
}

#demo-guide-services {
  color: var(--blue-500);
}

.demo-guide-open {
  grid-area: Open;
}

.images--mobile {
  grid-template-columns: 1fr;
  grid-template-rows: auto;
  grid-gap: 20px;
  grid-template-areas:
    'Open'
    'Services';
}

.images--mobile .demo-guide,
.images--mobile .demo-guide-closed {
  display: none;
}

.images--mobile .demo-guide-open {
  margin: auto;
  width: 90%;
}

.images--mobile #demo-guide-services {
  margin-bottom: 16px;
  font-size: 1.25rem;  
}

.images--mobile .service-list {
  flex-direction: column;
}

.images--mobile .service + .service {
  margin-left: 0;
  margin-top: 20px;
}
</style>
