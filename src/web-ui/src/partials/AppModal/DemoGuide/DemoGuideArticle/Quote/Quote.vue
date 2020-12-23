<template>
  <figure class="quote-container mb-0 p-3">
    <blockquote class="quote">
      <slot name="quote"> </slot>
    </blockquote>
    <figcaption class="attribution text-right"><slot name="attribution"></slot></figcaption>
    <slot></slot>
  </figure>
</template>

<script>
export default {
  name: 'Quote',
};
</script>

<style scoped>
.quote-container {
  background: var(--blue-100);
}

.quote {
  font-family: Ember-Serif, Georgia, serif;
}
</style>
