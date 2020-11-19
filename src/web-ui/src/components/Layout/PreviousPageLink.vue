<template>
  <div class="text-left">
    <router-link :to="to" class="link"> <i class="fa fa-chevron-left" aria-hidden></i> {{ text }}</router-link>
  </div>
</template>

<script>
export default {
  name: 'PreviousPageLink',
  props: {
    to: { type: String, required: true },
    text: { type: String, required: true },
  },
};
</script>

<style scoped>
.link {
  color: inherit;
}
</style>
