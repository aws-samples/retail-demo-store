<template>
  <div>
    <i :class="iconClass"></i>
  </div>
</template>

<script>
export default {
  name: 'LoadingFallback',
  props: {
    small: { type: Boolean, default: false },
  },
  data() {
    return { iconClass: { 'fas fa-spinner fa-spin': true, 'fa-3x': !this.small, 'fa-2x': this.small } };
  },
};
</script>
