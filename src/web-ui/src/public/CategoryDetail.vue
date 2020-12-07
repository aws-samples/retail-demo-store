<template>
  <Layout>
    <div class="content">

      <!-- Loading Indicator -->
      <div class="container mb-4" v-if="!products.length">
        <i class="fas fa-spinner fa-spin fa-3x"></i>
      </div>

      <!-- Product List -->
      <div class="container mt-3" v-if="products.length">
        <h4 class="text-left">{{ this.display | capitalize }}</h4>
        <div v-if="explain_recommended" class="text-muted text-center">
          <small><em><i v-if="active_experiment" class="fa fa-balance-scale"></i><i v-if="personalized" class="fa fa-user-check"></i> {{ explain_recommended }}</em></small>
        </div>
        <div class="row">

          <div class="col-sm-3 col-md-3 col-lg-3 text-left">
            <div class="card mb-3">
              <div class="card-body">
                <h5 class="card-title mb-0">Gender</h5>
                </div>
                <ul class="list-group list-group-flush">
              <li class="list-group-item" v-for="gender in [ 'M', 'F' ]" v-bind:key="gender">
                <label class="mb-0">
                  <input type="checkbox" :value="gender" v-model="selectedGenders">
                  {{ { M: 'Male', F: 'Female'}[gender] }}
                </label>
              </li>
              </ul>
            </div>
            <div class="card">
              <div class="card-body">
                <h5 class="card-title mb-0">Styles</h5>
                </div>
                <ul class="list-group list-group-flush">
              <li class="list-group-item" v-for="style in styles" v-bind:key="style">
                <label class="mb-0">
                  <input type="checkbox"  :value="style" v-model="selectedStyles">
                  {{style | capitalize}}
                </label>
              </li>
              </ul>
            </div>
          </div>

          <div class="card-deck col-sm-9 col-md-9 col-lg-9 mt-4">
            <Product v-for="product in filteredProducts"
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
      errors: [],
      display: '',
      explain_recommended: '',
      active_experiment: false,
      personalized: false,
      selectedGenders: [],
      selectedStyles: []
    }
  },
  async created () {
    this.fetchData()
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
    }
  },
  computed: {
    user() {
      return AmplifyStore.state.user
    },
    personalizeUserID() {
      return AmplifyStore.getters.personalizeUserID
    },
    styles() {
      const styles = this.products.map(product => product.style)
      const uniqueStyles = styles.filter((style, index, styles) => styles.indexOf(style) === index).sort()
      return uniqueStyles
    },
    filteredProducts() {
      let products = this.products

      const selectedStyles = this.selectedStyles
      const selectedGenders = this.selectedGenders

      if (selectedStyles.length) {
        products = products.filter(product => selectedStyles.includes(product.style))
      }

      if (selectedGenders.length) {
        products = products.filter(product => selectedGenders.includes(product.gender_affinity) || !product.gender_affinity)
      }

      return products
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
