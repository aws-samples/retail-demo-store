<template>
  <div class="container mb-4">
    <div class="row col-sm-12 col-md-12 col-lg-12 d-none d-sm-block">
      <ul class="nav nav-pills nav-fill mx-auto">
        <li class="nav-item">
          <router-link class="nav-link" :to="{name:'Main'}">Back to Storefront</router-link>
        </li>
        <li class="nav-item" >
          <router-link class="nav-link" v-bind:class="{'active': currentRouteName === 'Collections'}" :to="{name:'Collections'}">In-Store View</router-link>
        </li>
        <li class="nav-item" >
          <router-link class="nav-link" v-bind:class="{'active': currentRouteName === 'Waypoint'}" :to="{name:'Waypoint'}">Waypoint Geofence</router-link>
        </li>
        <li class="nav-item" >
          <router-link class="nav-link" v-bind:class="{'active': currentRouteName === 'C-Store'}" :to="{name:'C-Store'}">C-Store Geofence</router-link>
        </li>
        <li class="nav-item" >
          <router-link class="nav-link" v-bind:class="{'active': currentRouteName === 'Waypoint Demo Admin'}" :to="{name:'Waypoint Demo Admin'}">Waypoint Demo Admin</router-link>
        </li>
      </ul>
    </div>
  </div>
</template>

<script>
export default {
  name: "WaypointDemoNavigation",
  computed: {
    currentRouteName() {
      return this.$route.name;
    }
  }
}
</script>

<style scoped>

</style>