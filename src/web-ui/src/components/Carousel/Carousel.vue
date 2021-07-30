<template>
  <Agile :options="settings">
    <template slot="prevButton"><i class="fas fa-chevron-left" aria-label="previous"></i></template>
    <template slot="nextButton"><i class="fas fa-chevron-right" aria-label="next"></i></template>

    <slot></slot>
  </Agile>
</template>

<script>
import { VueAgile } from 'vue-agile';

export default {
  name: 'Carousel',
  components: { Agile: VueAgile },
  props: {
    settings: {
      type: Object,
      required: true,
    },
  },
};
</script>

<style>
.agile__nav-button {
  --button-distance: 5px;

  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  border: 1px solid var(--grey-300);
  cursor: pointer;
  background: var(--white);
  padding: 10px 5px;
  transition: color 150ms ease-in-out;
}

.agile__nav-button {
  color: var(--grey-500);
}

.agile__nav-button--prev {
  left: var(--button-distance);
}

.agile__nav-button--next {
  right: var(--button-distance);
}

@media (min-width: 576px) {
  .agile__nav-button {
    --button-distance: -15px;
    color: var(--grey-200);
  }

  .agile__nav-button:hover,
  .agile__nav-button:focus {
    color: var(--grey-500);
  }
}
</style>
