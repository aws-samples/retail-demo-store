<template>
  <div>
    <Navigation v-if="showNav"></Navigation>
    <slot></slot>
    <TextAlerts v-if="showTextAlerts"></TextAlerts>
    <Footer v-if="showFooter"></Footer>
  </div>
</template>

<script>
import Navigation from '../Navigation';
import Footer from '../Footer';
import TextAlerts from './TextAlerts';

export default {
  name: 'Layout',
  props: {
    showNav: {
      type: Boolean,
      default: true,
    },
    showTextAlerts: {
      type: Boolean,
      default: true,
    },
    showFooter: {
      type: Boolean,
      default: true,
    },
    backgroundColor: {
      type: String,
      default: 'var(--white)',
    },
  },
  watch: {
    backgroundColor: {
      immediate: true,
      handler(newBg) {
        document.body.style.setProperty('--background-color', newBg);
      },
    },
  },
  components: {
    Navigation,
    Footer,
    TextAlerts,
  },
};
</script>

<style>
body {
  background-color: var(--background-color);
}
</style>
