<template>
  <div>
    <component
      :is="currentPageComponent"
      @autoSelectShopper="onAutoSelectShopper"
      @chooseAShopper="onChooseAShopper"
      @useDefaultProfile="onUseDefaultProfile"
      @shopperSelected="onShopperSelected"
      @tryAgain="onTryAgain"
      @confirm="onConfirm"
      :selection="pageData.meta && pageData.meta.selection"
      :assignedShopper="pageData.meta && pageData.meta.assignedShopper"
    ></component>
  </div>
</template>

<script>
import { ShopperSelectPages } from './config';

import GetStarted from './pages/GetStarted';
import SelectShopper from './pages/SelectShopper';
import ConfirmShopper from './pages/ConfirmShopper';

export default {
  name: 'ShopperSelect',
  data() {
    return { pageData: { currentPage: ShopperSelectPages.GetStarted, meta: null } };
  },
  computed: {
    currentPageComponent() {
      switch (this.pageData.currentPage) {
        case ShopperSelectPages.GetStarted:
          return GetStarted;
        case ShopperSelectPages.SelectShopper:
          return SelectShopper;
        case ShopperSelectPages.ConfirmShopper:
          return ConfirmShopper;
      }

      throw new Error('Invalid current page on shopper select modal');
    },
  },
  methods: {
    onAutoSelectShopper(meta) {
      this.pageData = { currentPage: ShopperSelectPages.ConfirmShopper, meta };
    },
    onChooseAShopper() {
      this.pageData = { currentPage: ShopperSelectPages.SelectShopper };
    },
    onUseDefaultProfile() {
      this.$emit('profileSwitched');
    },
    onShopperSelected(meta) {
      this.pageData = { currentPage: ShopperSelectPages.ConfirmShopper, meta };
    },
    onTryAgain() {
      this.pageData = { currentPage: ShopperSelectPages.GetStarted };
    },
    onConfirm() {
      this.$emit('profileSwitched');
    },
  },
};
</script>

<style>
.tooltip .tooltip-inner {
  background: var(--blue-600);
  padding: 16px 8px;
  min-width: 300px;
}

.tooltip.bs-tooltip-bottom .arrow::before {
  border-bottom-color: var(--blue-600);
}

.tooltip a {
  text-decoration: underline;
  color: var(--white);
}
</style>
