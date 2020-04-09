<template>
  <div class="col-sm-12 col-md-3 col-lg-3 mb-4">

    <!-- Card -->
    <div class="card mx-auto h-100">
      <a href="#" data-toggle="modal" >
        <img :src="categoryImageURL" class="card-img-top" alt="...">
      </a>
      <div class="card-img-overlay d-flex flex-column">
        <router-link class="btn btn-secondary btn-block mt-auto" :to="{name:'CategoryDetail', params: {id: category.name}}">{{ category.name | capitalize }}</router-link>  
      </div>
    </div>

  </div>
</template>

<script>

export default {
  name: 'Category',
  components: {
  },
  props: {
      category: null
  },
  data () {
    return {  
      errors: []
    }
  },
  created () {
  },
  methods: {
  },
  computed: {
    categoryImageURL: function () {
      if (this.category.image.includes('://')) {
        return this.category.image
      }
      else {
        let root_url = process.env.VUE_APP_IMAGE_ROOT_URL
        return root_url + this.category.name + '/' + this.category.image
      }
    }
  },
  filters: {
    capitalize: function (value) {
      if (!value) return ''
      value = value.toString()
      return value.charAt(0).toUpperCase() + value.slice(1)
    }
  }
}
</script>

<style scoped>
  .card-img-overlay {
    opacity: 0.75;
  }
</style>