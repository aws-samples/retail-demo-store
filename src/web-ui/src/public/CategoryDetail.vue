<template>
  <Layout :loading="!products.length">
    <div class="content">

      <!-- Product List -->
      <div class="container mt-3" v-if="products.length">
        <h2 class="text-left">{{ this.display | capitalize }}</h2>
        <div v-if="explain_recommended" class="text-muted text-left">
          <small><em><i v-if="active_experiment" class="fa fa-balance-scale"></i><i v-if="personalized" class="fa fa-user-check"></i> {{ explain_recommended }}</em></small>
        </div>
        <div class="row mt-4">

          <div class="col-sm-3 col-md-3 col-lg-3 text-left">
            <h4 class="bg-light p-2">Filters</h4>
            <div class="gender-filter-border">
              <a
                class="filter-title mb-1 mt-1"
                data-toggle="collapse"
                data-target="#gender-filter"
                aria-expanded="true"
                aria-controls="gender-filter"
              >
                <i class="chevron fa fa-chevron-up ml-2"></i>
                Gender
              </a>
              <div class="collapse show" id="gender-filter">
                <div class="p-1 pl-2" v-for="gender in [ 'M', 'F' ]" v-bind:key="gender">
                  <label class="mb-1">
                    <input class="mr-1" type="checkbox" :value="gender" v-model="selectedGenders">
                    {{ { M: 'Male', F: 'Female'}[gender] }}
                  </label>
                </div>
              </div>
            </div>

            <div>
              <a
                class="filter-title mb-1 mt-1"
                data-toggle="collapse"
                data-target="#style-filter"
                aria-expanded="true"
                aria-controls="style-filter"
              >
                <i class="chevron fa fa-chevron-up ml-2"></i>
                Styles
              </a>
              <div class="collapse show" id="style-filter">
                <div class="p-1 pl-2" v-for="style in styles" v-bind:key="style">
                  <label class="mb-0">
                    <input class="mr-1" type="checkbox"  :value="style" v-model="selectedStyles">
                    {{style | capitalize}}
                  </label>
                </div>
              </div>
            </div>
          </div>

          <div class="card-deck col-sm-9 col-md-9 col-lg-9">
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

  .card-deck {
    display: grid;
    grid-gap: 1rem;
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr) ) ;
  }

  .filter-title {
    font-size: 1.2em;
    font-weight: 500;
    cursor: pointer;
    display: block;
  }

  .chevron {
    transform: rotate(180deg);
    transition: transform 150ms ease-in-out;
    font-size: 1.15rem;
  }
  [aria-expanded='true'] > .chevron {
    transform: rotate(0deg);
  }

  .gender-filter-border {
    border-bottom: 1px solid var(--grey-300);
  }
</style>
