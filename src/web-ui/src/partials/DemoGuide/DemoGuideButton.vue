<template>
  <button class="button btn btn-primary">
    <div class="demo-guide">DEMO GUIDE</div>
    <div class="learn-more">Learn more about this demo</div>
  </button>
</template>

<script>
export default { name: 'DemoGuideButton' };
</script>

<style scoped>
  .button {
    border: none;
    border-radius: 12px 12px 0 0;
    background: var(--blue-500);
  }

  .button:hover, .button:focus {
    background: var(--blue-600);
  }

  .demo-guide {
    font-weight: bold;
    font-size: 1.5rem;
  }

  .learn-more {
    font-weight: 500;
    font-size: 1.35rem;
  }
</style>
