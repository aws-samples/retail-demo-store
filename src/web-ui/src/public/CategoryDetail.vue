<template>
  <Layout :isLoading="!products.length">
      <!-- Product List -->
      <div class="container" v-if="products.length">
        <h2 class="text-left">{{ capitalize(this.display) }} <DemoGuideBadge v-if="demoGuideBadgeArticle" :article="demoGuideBadgeArticle" hideTextOnSmallScreens></DemoGuideBadge></h2>
        <div v-if="experiment" class="text-muted text-left">
          <small><em><i v-if="experiment" class="fa fa-balance-scale"></i> {{ experiment }}</em></small>
        </div>

        <div class="mt-4 d-flex flex-column flex-lg-row">
          <div class="filters mb-4 mb-lg-4 mr-lg-4 text-left">
            <h4 class="bg-light p-2">Filters</h4>
            <div class="gender-filter-border" v-if="showGenderFilter">
              <a
                class="filter-title mb-1 mt-1"
                data-toggle="collapse"
                data-target="#gender-filter"
                :aria-expanded="!isInitiallyMobile"
                aria-controls="gender-filter"
              >
                <i class="chevron fa fa-chevron-up ml-2"></i>
                Gender
              </a>
              <div :class="['collapse', isInitiallyMobile ? 'hide' : 'show']" id="gender-filter" ref="genderCollapse">
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
                :aria-expanded="!isInitiallyMobile"
                aria-controls="style-filter"
              >
                <i class="chevron fa fa-chevron-up ml-2"></i>
                Styles
              </a>
              <div :class="['collapse', isInitiallyMobile ? 'hide' : 'show']" id="style-filter" ref="styleCollapse">
                <div class="p-1 pl-2" v-for="style in styles" v-bind:key="style">
                  <label class="mb-0">
                    <input class="mr-1" type="checkbox"  :value="style" v-model="selectedStyles">
                    {{ capitalize(style) }}
                  </label>
                </div>
              </div>
            </div>
          </div>

          <div class="products">
            <Product v-for="product in filteredProducts"
              v-bind:key="product.id"
              :product="product"
              :experiment="product.experiment"
              :feature="feature"
            />
          </div>
        </div>
      </div>
  </Layout>
</template>

<script>
import {mapState, mapGetters} from 'vuex'

import { RepositoryFactory } from '@/repositories/RepositoryFactory'
import { AnalyticsHandler } from '@/analytics/AnalyticsHandler'

import Product from '@/components/Product/Product.vue'
import Layout from '@/components/Layout/Layout.vue'
import DemoGuideBadge from '@/components/DemoGuideBadge/DemoGuideBadge.vue';
import { getDemoGuideArticleFromPersonalizeARN } from '@/partials/AppModal/DemoGuide/config';
import { capitalize } from '@/util/capitalize'

const ProductsRepository = RepositoryFactory.get('products')
const RecommendationsRepository = RepositoryFactory.get('recommendations')

const ExperimentFeature = 'category_detail_rank'
const MaxProducts = 60

export default {
  name: 'Products',
  components: {
    Product,
    Layout,
    DemoGuideBadge
  },
  data() {
    return {
      feature: ExperimentFeature,
      demoGuideBadgeArticle: null,
      experiment: null,
      products: [],
      errors: [],
      display: '',
      selectedGenders: [],
      selectedStyles: [],
      isInitiallyMobile: window.matchMedia('(max-width: 992px)').matches
    }
  },
  created () {
    this.fetchData()
  },
  mounted() {
    this.mediaQueryList = window.matchMedia('(max-width: 992px)');

    this.listener = () => {
      const collapseElements = this.showGenderFilter ? [this.$refs.genderCollapse, this.$refs.styleCollapse] : [this.$refs.styleCollapse]

      // eslint-disable-next-line no-undef
      $(collapseElements).collapse(this.mediaQueryList.matches ? 'hide' : 'show')
    };

    this.mediaQueryList.addEventListener('change', this.listener);
  },
  beforeUnmount() {
    this.mediaQueryList.removeEventListener('change', this.listener);
  },
  methods: {
    async fetchData (){
      this.getProductsByCategory(this.$route.params.id)
    },
    async getProductsByCategory(categoryName) {
      this.demoGuideBadgeArticle = null
      this.experiment = null
      this.products = []

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
          const personalizeRecipe = response.headers['x-personalize-recipe'];
          const experimentName = response.headers['x-experiment-name'];

          if (personalizeRecipe) this.demoGuideBadgeArticle = getDemoGuideArticleFromPersonalizeARN(personalizeRecipe);

          if (experimentName) this.experiment = `Active experiment: ${experimentName}`
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
    capitalize
  },
  computed: {
    ...mapState({user: state => state.user, categories: state => state.categories.categories}),
    ...mapGetters(['personalizeUserID']),
    showGenderFilter() {
      const category = this.categories?.find(category => category.name === this.$route.params.id);

      if (!category) return false;

      return category.has_gender_affinity;
    },
    styles() {
      const styles = this.products.map(product => product.style)
      const uniqueStyles = styles.filter((style, index, styles) => styles.indexOf(style) === index).sort()
      return uniqueStyles;      
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
  watch: {
    $route() {
      this.selectedGenders = [];
      this.selectedStyles = [];

      this.fetchData();
    },
  },
}
</script>

<style scoped>
  .products {
    flex: 1;
    align-self: center;
    display: grid;
    grid-gap: 1rem;
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr) ) ;
  }

  .filter-title {
    font-size: 1.2em;
    font-weight: bold;
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

  @media(min-width: 992px) {
    .filters {
      width: 300px;
    }

    .products {
      align-self: flex-start;
    }
  }

</style>
