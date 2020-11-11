<template>
  <div :class="{'layout--has-nav': showNav}">
    <Navigation v-if="showNav"></Navigation>

    <LoadingFallback v-if="isLoading" class="container mb-4"></LoadingFallback>

    <PreviousPageLink
      v-if="!isLoading && previousPageLinkProps"
      :to="previousPageLinkProps.to"
      :text="previousPageLinkProps.text"
      class="container mb-2"
    ></PreviousPageLink>

    <slot v-if="!isLoading"></slot>

    <TextAlerts v-if="showTextAlerts" class="mt-5"></TextAlerts>

    <Footer v-if="showFooter" class="my-4"></Footer>
  </div>
</template>

<script>
import LoadingFallback from '../LoadingFallback/LoadingFallback';
import PreviousPageLink from './PreviousPageLink';
import Footer from '@/partials/Footer/Footer';
import TextAlerts from '@/partials/TextAlerts/TextAlerts';
import Navigation from '@/partials/Navigation/Navigation';

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
    isLoading: {
      type: Boolean,
      default: false,
    },
    previousPageLinkProps: {
      type: Object,
      required: false,
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
    LoadingFallback,
    PreviousPageLink,
    TextAlerts,
    Footer,
  },
};
</script>

<style scoped>
.layout--has-nav {
  padding-top: 200px;
}
</style>

<style>
body {
  background-color: var(--background-color);
}
</style>
