<template>
  <article ref="article" tabindex="0" class="article">
    <div class="mb-3">
      <h1 class="heading mb-0"><slot name="heading"></slot></h1>
      <p v-if="hasRecipe" class="recipe mb-0"><slot name="recipe"></slot></p>
    </div>

    <slot></slot>
  </article>
</template>

<script>
export default {
  name: 'ArticleLayout',
  mounted() {
    this.$refs.article.focus();
  },
  computed: {
    hasRecipe() {
      return !!this.$slots.recipe;
    },
  },
};
</script>

<style scoped>
.article {
  background: var(--white);
}

.article:focus {
  outline: none;
}

.heading {
  font-size: 1.5rem;
}

.recipe {
  font-size: 1.35rem;
}
</style>
