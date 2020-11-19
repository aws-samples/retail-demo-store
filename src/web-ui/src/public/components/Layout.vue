<template>
  <div>
    <Navigation v-if="showNav"></Navigation>
    <slot></slot>
    <Footer v-if="showFooter"></Footer>
  </div>
</template>

<script>
import Navigation from '../Navigation';
import Footer from '../Footer';

export default {
  name: 'Layout',
  props: {
    showNav: {
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
  },
};
</script>

<style>
body {
  background-color: var(--background-color);
}
</style>
