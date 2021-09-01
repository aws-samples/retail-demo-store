<template>
  <div :id="accordionId" class="menu accordion">
    <DemoGuideMenuSection
      v-for="section in sections"
      :key="section.id"
      :section="section"
      :menuAccordionId="accordionId"
      class="mb-2"
    ></DemoGuideMenuSection>
  </div>
</template>

<script>
import DemoGuideMenuSection from './DemoGuideMenuSection/DemoGuideMenuSection';
import { sections } from '../config';

export default {
  name: 'DemoGuideMenu',
  components: { DemoGuideMenuSection },
  data() {
    return {
      accordionId: 'demo-guide-menu-accordion',
      sections,
    };
  },
};
</script>

<style scoped>
.menu {
  background: var(--aws-deep-squid-ink);
  color: var(--white);
}
</style>
