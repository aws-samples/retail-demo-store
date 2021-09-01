<template>
  <div class="container mb-4">
    <div class="row col-sm-12 col-md-12 col-lg-12 d-none d-sm-block">
      <ul class="nav nav-pills nav-fill mx-auto">
        <li class="nav-item">
          <router-link class="nav-link" :to="{name:'Main'}">Back to Storefront</router-link>
        </li>
        <li class="nav-item" >
          <router-link class="nav-link" :to="{name:'Collections'}">In-Store View</router-link>
        </li>
        <li class="nav-item" >
          <router-link class="nav-link" :to="{name:'Location'}">Location Geofence</router-link>
        </li>
      </ul>
    </div>
  </div>
</template>

<script>
export default {
  name: "LocationDemoNavigation"
}
</script>

<style scoped>

</style>