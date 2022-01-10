<template>
  <router-link to="/alerts">
    <span v-if="alertsExist" class="alert-icon" title="You have new alerts!">✉</span>
  </router-link>
</template>

<script>

import {mapGetters} from "vuex";

export default {
  name: "AlertLink",
  computed: {
    ...mapGetters(["numAlerts"]),
    alertsExist () {
      return this.numAlerts && this.numAlerts > 0
    }
  }
}
</script>

<style>

.alert-icon {
    display: inline-block;
    vertical-align: middle;
    line-height: 1;
    font-size: 4em;
    color: #DD6666;
    cursor: pointer;
    -webkit-transition: color .2s ease-out;
    transition: color .2s ease-out;

    -webkit-user-select: none;
    -moz-user-select: none;
    -ms-user-select: none;
    user-select: none;
}
.alert-icon:hover,
.alert-icon:focus {
  color: var(--blue-600);
  cursor: pointer;
}
</style>