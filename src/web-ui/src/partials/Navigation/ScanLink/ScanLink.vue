<template>
  <router-link to="/scan">
    <ScanIcon class="scan icon"></ScanIcon>
  </router-link>
</template>

<script>
import ScanIcon from "@/partials/Navigation/ScanLink/ScanIcon";

export default {
  name: "ScanLink",
  components: {ScanIcon},
}
</script>

<style>
.icon {
  transition: fill 150ms ease-in-out;
}

.scan:hover .icon,
.scan:focus .icon {
  fill: var(--blue-600);
  cursor: pointer;
}
</style>