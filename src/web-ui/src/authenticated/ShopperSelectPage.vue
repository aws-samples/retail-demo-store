<template>
  <SecondaryLayout>
    <div class="container">
      <ShopperSelect @profileSwitched="onProfileSwitch"></ShopperSelect>
    </div>
  </SecondaryLayout>
</template>

<script>
import SecondaryLayout from '@/components/SecondaryLayout/SecondaryLayout.vue';
import ShopperSelect from '@/partials/ShopperSelect/ShopperSelect.vue';

export default {
  name: 'ShopperSelectPage',
  components: { SecondaryLayout, ShopperSelect },
  methods: {
    onProfileSwitch() {
      this.$router.push('/');
    },
  },
};
</script>

<style></style>
