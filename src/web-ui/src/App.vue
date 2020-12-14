<template>
  <div id="app">
    <router-view class="text-center"/>
  </div>
</template>

<script>
import { mapActions } from 'vuex';

export default {
  name: 'app',
  methods: {
    ...mapActions(['getCategories','getCart',]),
  },
  created() {
    this.getCategories();

    this.getCart();
  },
};
</script>
<style>
@font-face {
  font-family: Ember;
  src: url("/ember.woff2");
}

body {
  font-family: Ember, sans-serif;
}

</style>
