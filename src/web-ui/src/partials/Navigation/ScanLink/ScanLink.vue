<template>
<!--  <div @click="onScanClick">-->
  <router-link to="/scan">
    <ScanIcon class="scan icon"></ScanIcon>
  </router-link>
<!--  </div>-->
</template>

<script>
import ScanIcon from "@/partials/Navigation/ScanLink/ScanIcon";

export default {
  name: "ScanLink",
  components: {ScanIcon},
  // methods: {
  //   onScanClick() {
  //     if (window.location.protocol === 'https:' || window.location.hostname === 'localhost') {
  //       this.$router.push('/scan')
  //     } else {
  //       window.location = `https://${window.location.host}/#/scan`
  //     }
  //   }
  // }
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