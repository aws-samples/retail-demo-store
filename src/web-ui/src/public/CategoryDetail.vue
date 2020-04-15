<template>
  <div class="content">

    <!-- Loading Indicator -->
    <div class="container mb-4" v-if="!products.length">
      <i class="fas fa-spinner fa-spin fa-3x"></i>
    </div>

    <!-- Categories Navigation -->
    <div class="container mb-4" v-if="categories.length">
      <div class="row col-sm-12 col-md-12 col-lg-12 d-none d-sm-block">
        <ul class="nav nav-pills nav-fill mx-auto">
          <li class="nav-item">
            <router-link class="nav-link" :to="{name:'CategoryDetail', params: {id: 'featured'}}" v-bind:class="{ active: display == 'featured' }">Featured</router-link> 
          </li>
          <li class="nav-item" v-for="category in categories" v-bind:key=category.id>
            <router-link class="nav-link" :to="{name:'CategoryDetail', params: {id: category.name}}" v-bind:class="{ active: display == category.name }">{{ category.name | capitalize }}</router-link> 
          </li>
        </ul>
      </div>
      <div class="dropdown show d-block d-sm-none">
        <a class="btn dropdown-toggle btn-primary" href="#" role="button" id="dropdownMenuLink" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
          Select Category
        </a>
        <div class="dropdown-menu" aria-labelledby="dropdownMenuLink">
          <router-link class="dropdown-item" :to="{name:'CategoryDetail', params: {id: 'featured'}}" v-bind:class="{ active: display == 'featured' }">Featured</router-link> 
          <router-link class="dropdown-item" v-for="category in categories" v-bind:key="category" :to="{name:'CategoryDetail', params: {id: category.name}}" v-bind:class="{ active: display == category.name }">
            {{ category.name | capitalize }}
          </router-link> 
        </div>
      </div>
    </div>

    <!-- Product List -->
    <div class="container mt-3" v-if="products.length">
      <h4>{{ this.display | capitalize }}</h4>
      <div class="row">
        <div class="card-deck col-sm-12 col-md-12 col-lg-12 mt-4">
          <Product v-for="product in products" 
            v-bind:key="product.id"
            :product="product"
          />
        </div>
      </div>
    </div>

  </div> 
</template>

<script>
import AmplifyStore from '@/store/store'

import { RepositoryFactory } from '@/repositories/RepositoryFactory'
import { AnalyticsHandler } from '@/analytics/AnalyticsHandler'

import Product from './components/Product.vue'

const ProductsRepository = RepositoryFactory.get('products')
const RecommendationsRepository = RepositoryFactory.get('recommendations')

const ExperimentFeature = 'category_detail_rank'

export default {
  name: 'Products',
  components: {
    Product
  },
  data() {
    return {
      products: [],
      categories: [],
      errors: [],
      display: ''
    }
  },
  async created () {
    this.fetchData()
    this.getCategories()
  },
  methods: {
    async fetchData (){
      this.getProductsByCategory(this.$route.params.id)
    }, 
    async getProductsByCategory(categoryName) {
      let intermediate = null
      if (categoryName == 'featured') {
        const { data } = await ProductsRepository.getFeatured()
        intermediate = data
      }
      else {
        const { data } = await ProductsRepository.getProductsByCategory(categoryName)
        intermediate = data
      }

      if (this.userID && intermediate.length > 0) {
        const { data } = await RecommendationsRepository.getRerankedItems(this.userID, intermediate, ExperimentFeature)
        this.products = data

        if (this.products.length > 0 && 'experiment' in this.products[0]) {
          AnalyticsHandler.identifyExperiment(this.products[0].experiment)
        }
      }
      else {
        this.products = intermediate
      }

      this.display = categoryName
    },
    async getCategories () {
      const { data } = await ProductsRepository.getCategories()
      this.categories = data
    }
  },
  computed: {
    user() { 
      return AmplifyStore.state.user
    },
    userID() { 
      return AmplifyStore.state.userID
    }
  },
  filters: {
    capitalize: function (value) {
      if (!value) return ''
      value = value.toString()
      return value.charAt(0).toUpperCase() + value.slice(1)
    }
  },
  watch: {
    // call again the method if the route changes
    '$route': 'fetchData'
  },
}
</script>

<style scoped>
  .content {
    padding-top: 1rem;
  }

  .carousel {
    max-height: 600px;
  }

  .carousel-item {
    max-height: 600px;
  }
</style>