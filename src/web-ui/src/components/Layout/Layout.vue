<template>
  <div :class="{ 'layout--has-nav': showNav, 'layout--has-demo-guide': showDemoGuide }">
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

    <Footer v-if="showFooter" class="my-4 container"></Footer>

    <AppModal></AppModal>

    <ConfirmationModal></ConfirmationModal>

    <DemoGuideButton v-if="showDemoGuide" class="demo-guide-button"></DemoGuideButton>
  </div>
</template>

<script>
import LoadingFallback from '../LoadingFallback/LoadingFallback';
import PreviousPageLink from './PreviousPageLink';
import Footer from '@/partials/Footer/Footer';
import TextAlerts from '@/partials/TextAlerts/TextAlerts';
import Navigation from '@/partials/Navigation/Navigation';
import AppModal from '@/partials/AppModal/AppModal';
import DemoGuideButton from '@/partials/DemoGuideButton/DemoGuideButton';
import ConfirmationModal from '@/partials/ConfirmationModal/ConfirmationModal';

export default {
  name: 'Layout',
  components: {
    Navigation,
    LoadingFallback,
    PreviousPageLink,
    TextAlerts,
    Footer,
    AppModal,
    DemoGuideButton,
    ConfirmationModal
  },
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
    showDemoGuide: {
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
  methods: {
    updateBackgroundColor(color) {
      document.body.style.setProperty('--background-color', color);
    },
  },
  mounted() {
    this.updateBackgroundColor(this.backgroundColor);
  },
  watch: {
    backgroundColor: {
      handler(newBg) {
        this.updateBackgroundColor(newBg);
      },
    },
  },
  beforeDestroy() {
    document.body.style.removeProperty('--background-color');
  },
};
</script>

<style scoped>
.layout--has-nav {
  padding-top: 250px;
}

.layout--has-demo-guide {
  padding-bottom: 100px;
}

.demo-guide-button {
  position: fixed;
  z-index: 3;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 90%;
  max-width: 400px;
}

@media (min-width: 992px) {
  .layout--has-nav {
    padding-top: 150px;
  }
}
</style>

<style>
body {
  background-color: var(--background-color);
}
</style>
