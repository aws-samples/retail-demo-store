<template>
  <div class="layout">
    <main :class="{ main: true, 'main--mobile': isMobile }" ref="main">
      <slot></slot>
    </main>

    <div
      v-if="showNav"
      :class="{ 'demo-walkthrough-nav d-flex justify-content-between': true, 'demo-walkthrough-nav--mobile': isMobile }"
    >
      <button v-if="!isLast" class="end-tour end-tour--desktop-only btn btn-outline-primary" @click="skip">
        End Tour
      </button>

      <div :class="{ 'demo-walkthrough-nav__main': true, 'ml-auto': isLast }">
        <button class="prev btn btn-outline-primary" @click="prevTourPage">Previous</button>

        <button v-if="isLast" class="end-tour btn btn-primary ml-2" @click="skip">End Tour</button>
        <button v-else class="next btn btn-primary ml-2" @click="nextTourPage">Next</button>
      </div>
    </div>

    <svg ref="svg" class="arrow-svg">
      <defs>
        <marker id="arrow" refX="1.5" refY="1.5" markerWidth="2" markerHeight="3" orient="auto">
          <path d="M 0 0 L 2 1.5 L 0 3 z" />
        </marker>
      </defs>

      <template v-if="arrowPoints">
        <polyline
          v-for="(points, i) in arrowPoints"
          :key="i"
          :points="`${points.map(([x, y]) => `${x}, ${y}`).join(' ')}`"
          fill="none"
          class="arrow-line"
          stroke-width="5"
          stroke-linejoin="round"
          marker-end="url(#arrow)"
        />
      </template>
    </svg>
  </div>
</template>

<script>
import { mapActions, mapState } from 'vuex';

import { APP_MODAL_ID } from '../config';

export default {
  name: 'DemoWalkthroughPageLayout',
  props: {
    showNav: { type: Boolean, default: true },
    isLast: { type: Boolean, default: false },
    // Side: 'TOP' | 'RIGHT' | 'BOTTOM' | 'LEFT'
    // DrawElementConfig: { ref: string, target: Side | (rect: ClientRect) => [number, number] }
    // ArrowConfig:
    //   {from: DrawElementConfig, to: DrawElementConfig, drawPoints: ({
    //     fromX: number, fromY: number, fromWidth: number, fromHeight: number,
    //     toX: number, toY: number, toWidth: number, toHeight: number
    //   }) => number[][]}
    // ArrowConfig[] | { desktop: ArrowConfig[], mobile: ArrowConfig[] }
    drawArrows: { type: [Array, Object], required: false },
  },
  data() {
    return { arrowPoints: null, isDestroyed: false };
  },
  computed: {
    ...mapState({ isMobile: (state) => state.modal.isMobile }),
    arrowConfigs() {
      if (!this.drawArrows) return null;

      if (Array.isArray(this.drawArrows)) return this.drawArrows;

      return this.isMobile ? this.drawArrows.mobile : this.drawArrows.desktop;
    },
  },
  methods: {
    ...mapActions(['prevTourPage', 'nextTourPage']),
    skip() {
      // eslint-disable-next-line no-undef
      $(`#${APP_MODAL_ID}`).modal('hide');
    },
    getCoordinatesFromSide(elementRect, side) {
      switch (side) {
        case 'TOP':
          return [elementRect.left + elementRect.width / 2, elementRect.top];
        case 'RIGHT':
          return [elementRect.right, elementRect.top + elementRect.height / 2];
        case 'BOTTOM':
          return [elementRect.left + elementRect.width / 2, elementRect.bottom];
        case 'LEFT':
          return [elementRect.left, elementRect.top + elementRect.height / 2];
      }

      throw new Error('Invalid side provided');
    },
    getArrowLines() {
      return [...this.$refs.svg.children].filter((elem) => elem instanceof SVGPolylineElement);
    },
    async drawArrowElements() {
      if (!this.arrowConfigs) return;

      const svgBox = this.$refs.svg.getBoundingClientRect();

      this.arrowPoints = this.arrowConfigs.map(({ from, to, drawPoints }) => {
        const fromBox = this.$parent.$refs[from.ref].getBoundingClientRect();
        const [fromX, fromY] =
          typeof from.target === 'function' ? from.target(fromBox) : this.getCoordinatesFromSide(fromBox, from.target);
        const fromWidth = fromBox.width;
        const fromHeight = fromBox.height;

        const toBox = this.$parent.$refs[to.ref].getBoundingClientRect();
        const [toX, toY] =
          typeof to.target === 'function' ? to.target(toBox) : this.getCoordinatesFromSide(toBox, to.target);
        const toWidth = toBox.width;
        const toHeight = toBox.height;

        return drawPoints({
          fromX,
          fromY,
          fromWidth,
          fromHeight,
          toX,
          toY,
          toWidth,
          toHeight,
        }).map(([x, y]) => [x - svgBox.left, y - svgBox.top]); // normalize coordinates to be relative to svg element location
      });

      await this.$nextTick();

      this.getArrowLines().forEach((line) => {
        const length = line.getTotalLength();

        line.style.strokeDasharray = `${length} ${length}`;
      });
    },
    animateArrows() {
      this.getArrowLines().forEach((line) => {
        const length = line.getTotalLength();

        // Set up the starting positions
        line.style.strokeDasharray = `${length} ${length}`;
        line.style.strokeDashoffset = length;

        // Trigger a layout so styles are calculated & the browser
        // picks up the starting position before animating
        line.getBoundingClientRect();

        // Define our transition
        const transition = 'stroke-dashoffset 300ms';

        line.style.transition = transition;
        line.style.WebkitTransition = transition;

        // Go!
        line.style.strokeDashoffset = '0';
      });
    },
    async initializeArrowDrawing() {
      if (!this.arrowConfigs) return;

      const allImagesLoadedPromise = Promise.all(
        this.arrowConfigs.map(
          ({ to }) =>
            new Promise((resolve) => {
              const image = this.$parent.$refs[to.ref];

              if (image.complete) return resolve();

              image.addEventListener('load', resolve);
            }),
        ),
      );

      await allImagesLoadedPromise;

      if (this.isDestroyed) return;

      await this.drawArrowElements();

      window.addEventListener('resize', this.drawArrowElements);
      this.$refs.main.addEventListener('scroll', this.drawArrowElements);

      // defer returning control until after DOM has updated
      await this.$nextTick();
    },
    cleanupArrowDrawings() {
      window.removeEventListener('resize', this.drawArrowElements);
      this.$refs.main.removeEventListener('scroll', this.drawArrowElements);
    },
  },
  async mounted() {
    await this.initializeArrowDrawing();
    if (!this.isDestroyed) this.animateArrows();
  },
  beforeDestroy() {
    this.isDestroyed = true;
    this.cleanupArrowDrawings();
  },
  watch: {
    arrowConfigs() {
      this.cleanupArrowDrawings();
      this.initializeArrowDrawing();
    },
  },
};
</script>

<style scoped>
.layout {
  background: var(--aws-deep-squid-ink);
  padding: 0;
  display: grid;
  grid-template-rows: 1fr auto;
  overflow: auto;
  color: var(--white);
}

.main {
  padding: 32px;
  padding-bottom: 0;
}

.main--mobile {
  padding-top: 0;
  /* fixes inability to scroll on firefox */
  padding-bottom: 100px;
}

.demo-walkthrough-nav {
  position: sticky;
  /* above arrows */
  z-index: 2;
  padding: 32px;
  padding-top: 16px;
  bottom: 0;
  left: 0;
  width: 100%;
  background: var(--aws-deep-squid-ink);
}

.end-tour,
.prev,
.next {
  width: 120px;
  border-color: var(--blue-500);
  font-size: 1.25rem;
  color: inherit;
}

.end-tour,
.next {
  background: var(--blue-500);
}

.end-tour:hover,
.end-tour:focus,
.prev:hover,
.prev:focus,
.next:hover,
.next:focus {
  background-color: var(--blue-600);
  border-color: var(--blue-600);
}

.demo-walkthrough-nav--mobile .end-tour,
.demo-walkthrough-nav--mobile .prev,
.demo-walkthrough-nav--mobile .next {
  font-size: 1rem;
}

.demo-walkthrough-nav--mobile .end-tour--desktop-only {
  display: none;
}

.demo-walkthrough-nav--mobile .demo-walkthrough-nav__main {
  flex: 1;
  display: flex;
  justify-content: space-between;
}

.arrow-svg {
  position: absolute;
  left: 0;
  width: 100%;
  top: 0;
  height: 100%;
  pointer-events: none;
}

.arrow-line {
  stroke: var(--grey-500);
}

#arrow {
  fill: var(--grey-500);
  animation: arrow-dash 300ms;
}

@keyframes arrow-dash {
  from {
    opacity: 0;
  }
  99% {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}
</style>
