<template>
  <Layout>
    <div class="content">

      <!-- Loading Indicator -->
      <div class="container mb-4" v-if="!products.length">
        <i class="fas fa-spinner fa-spin fa-3x"></i>
      </div>

      <!-- Product List -->
      <div class="container mt-3" v-if="products.length">
        <h4>{{ this.display | capitalize }}</h4>
        <div v-if="explain_recommended" class="text-muted text-center">
          <small><em><i v-if="active_experiment" class="fa fa-balance-scale"></i><i v-if="personalized" class="fa fa-user-check"></i> {{ explain_recommended }}</em></small>
        </div>
        <div class="row">
          <div class="card-deck col-sm-12 col-md-12 col-lg-12 mt-4">
            <Product v-for="product in products" 
              v-bind:key="product.id"
              :product="product"
              :experiment="product.experiment"
              :feature="feature"
            />
          </div>
        </div>
      </div>

    </div> 
  </Layout>
</template>

<script>
import AmplifyStore from '@/store/store'

import { RepositoryFactory } from '@/repositories/RepositoryFactory'
import { AnalyticsHandler } from '@/analytics/AnalyticsHandler'

import Product from './components/Product.vue'
import Layout from '@/components/Layout/Layout'

const ProductsRepository = RepositoryFactory.get('products')
const RecommendationsRepository = RepositoryFactory.get('recommendations')

const ExperimentFeature = 'category_detail_rank'
const MaxProducts = 60

export default {
  name: 'Products',
  components: {
    Product,
    Layout,
  },
  data() {
    return {
      feature: ExperimentFeature,
      products: [],
      categories: [],
      errors: [],
      display: '',
      explain_recommended: '',
      active_experiment: false,
      personalized: false
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

      if (this.personalizeUserID && intermediate.length > 0) {
        const response = await RecommendationsRepository.getRerankedItems(this.personalizeUserID, intermediate, ExperimentFeature)

        if (response.headers) {
          if (response.headers['x-personalize-recipe']) {
            this.personalized = true
            this.explain_recommended = 'Personalize recipe: ' + response.headers['x-personalize-recipe']
          }
          if (response.headers['x-experiment-name']) {
            this.active_experiment = true
            this.explain_recommended = 'Active experiment: ' + response.headers['x-experiment-name']
          }
        }

        this.products = response.data.slice(0, MaxProducts)

        if (this.products.length > 0 && 'experiment' in this.products[0]) {
          AnalyticsHandler.identifyExperiment(this.user, this.products[0].experiment)
        }
      }
      else {
        this.products = intermediate.slice(0, MaxProducts)
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
    personalizeUserID() {
      return AmplifyStore.getters.personalizeUserID
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