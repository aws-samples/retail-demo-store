<template>
  <div>
    <i v-for="i in 5" :key="i" class="fas fa-star"></i>
  </div>
</template>

<script>
export default {
  name: 'FiveStars',
};
</script>

<style scoped>
.fa-star {
  color: var(--amazon-orange);
}
</style>