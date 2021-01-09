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
  src: url('/fonts/ember-light.ttf');
  font-weight: 100 400;
  font-style: normal;
}

@font-face {
  font-family: Ember;
  src: url('/fonts/ember-light-italic.ttf');
  font-weight: 100 400;
  font-style: italic;
}

@font-face {
  font-family: Ember;
  src: url('/fonts/ember-medium.ttf');
  font-weight: 500 900;
  font-style: normal;
}

@font-face {
  font-family: Ember;
  src: url('/fonts/ember-medium-italic.ttf');
  font-weight: 500 900;
  font-style: italic;
}

@font-face {
  font-family: Ember-Serif;
  src: url("/fonts/ember-serif.ttf");
}

:root {
  font-size: 18px;
}

body {
  font-family: Ember, sans-serif;
}
</style>
