<template>
  <section>
    <div v-if="hasTitle" class="title d-inline-block px-4 py-1">
      <slot name="title"></slot>
    </div>
    <div class="content p-3">
      <slot></slot>
    </div>
  </section>
</template>

<script>
export default {
  name: 'ArticleFeature',
  computed: {
    hasTitle() {
      return !!this.$slots.title;
    },
  },
};
</script>

<style scoped>
.title {
  background: var(--grey-500);
  font-size: 0.8rem;
  color: var(--white);
}

.content {
  border: 1px solid var(--grey-500);
}
</style>
