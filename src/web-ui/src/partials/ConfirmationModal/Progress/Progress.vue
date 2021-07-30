<template>
  <div role="progressbar" :aria-valuenow="progress" aria-valuemin="0" aria-valuemax="100">
    <svg :height="radius * 2" :width="radius * 2">
      <text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle">
        {{ isError ? 'Error!' : complete ? 'Complete!' : 'Processing...' }}
      </text>

      <circle
        class="bar unachieved-progress"
        :stroke-width="stroke"
        fill="transparent"
        :r="normalizedRadius"
        :cx="radius"
        :cy="radius"
      />
      <circle
        :class="{ 'bar achieved-progress': true, 'achieved-progress--error': isError }"
        :stroke-dasharray="`${circumference} ${circumference}`"
        :style="{ strokeDashoffset }"
        :stroke-width="stroke"
        :r="normalizedRadius"
        :cx="radius"
        :cy="radius"
      />
    </svg>
  </div>
</template>

<script>
import { mapState } from 'vuex';

export default {
  name: 'Confirmation',
  data() {
    const radius = 60;
    const stroke = 4;

    const normalizedRadius = radius - stroke * 2;
    const circumference = 2 * Math.PI * normalizedRadius;

    return {
      radius,
      stroke,
      normalizedRadius,
      circumference,
    };
  },
  computed: {
    ...mapState({
      progress: (state) => state.confirmationModal.progress,
      isError: (state) => state.confirmationModal.isError,
    }),
    complete() {
      return this.progress === 100;
    },
    strokeDashoffset() {
      return this.circumference - (this.progress / 100) * this.circumference;
    },
  },
};
</script>

<style scoped>
.unachieved-progress {
  stroke: var(--grey-200);
}

.achieved-progress {
  fill: transparent;
  stroke: var(--blue-500);
  transition: stroke-dashoffset 1.5s, stroke 1.5s;
  transform: rotate(-90deg);
  transform-origin: 50% 50%;
}

.achieved-progress--error {
  stroke: var(--red-600);
}
</style>
