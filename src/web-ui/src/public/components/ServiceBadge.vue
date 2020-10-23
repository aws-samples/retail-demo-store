<template>
  <span class="d-flex align-items-center">
    <img v-bind:src="src" v-bind:alt="text" class="badge-img" />
    {{text}}
  </span>
</template>

<script>
export default {
  name: 'ServicePage',
  props: {
    text: String,
    src: String,
  },
};
</script>

<style scoped>
.badge-img {
  margin-right: 10px;
  height: 40px;
}
</style>
