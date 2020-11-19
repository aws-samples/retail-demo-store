<template>
  <div>
    <Navigation v-if="showNav"></Navigation>

    <LoadingFallback v-if="isLoading" class="container mb-4"></LoadingFallback>

    <PreviousPageLink
      v-if="!isLoading && previousPageLinkProps"
      :to="previousPageLinkProps.to"
      :text="previousPageLinkProps.text"
      class="container mb-2"
    ></PreviousPageLink>

    <slot v-if="!isLoading"></slot>

    <TextAlerts v-if="showTextAlerts"></TextAlerts>

    <Footer v-if="showFooter"></Footer>
  </div>
</template>

<script>
import Navigation from '@/public/Navigation';
import LoadingFallback from '../LoadingFallback/LoadingFallback';
import PreviousPageLink from './PreviousPageLink';
import Footer from '@/public/Footer';
import TextAlerts from '@/public/components/TextAlerts';

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

<style>
body {
  background-color: var(--background-color);
}
</style>
