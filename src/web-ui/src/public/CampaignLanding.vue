<template>
  <Layout :isLoading="!isLoaded">

    <div class="container">
      <h2 class="text-left">{{campaignTitle}}<DemoGuideBadge v-if="demoGuideBadgeArticle" :article="demoGuideBadgeArticle" hideTextOnSmallScreens></DemoGuideBadge></h2>
      <h4>{{subtitle}}</h4>

      <div class="mt-4 d-flex flex-column flex-lg-row">


        <div class="products">
          <Product v-for="product in products"
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

import Product from '@/components/Product/Product'
import Layout from '@/components/Layout/Layout'
import DemoGuideBadge from '@/components/DemoGuideBadge/DemoGuideBadge';
import { getDemoGuideArticleFromPersonalizeARN } from '@/partials/AppModal/DemoGuide/config';

//const ProductsRepository = RepositoryFactory.get('products')
const C360Repository = RepositoryFactory.get('c360')
const RecommendationsRepository = RepositoryFactory.get('recommendations')

const RankExperimentFeature = 'campaign_detail_rank'
const MaxProducts = 16

export default {
  name: 'CampaignLanding',
  components: {
    Product,
    Layout,
    DemoGuideBadge
  },
  data() {
    return {
      demoGuideBadgeArticle: null,
      products: [],
      errors: [],
      campaignTitle: null,
      subtitle: "",
      feature: null
    }
  },
  created () {
    this.fetchData()
  },
  methods: {
    async fetchData (){
      this.retrieveCampaignDetails(this.$route.params.campaignName)
    },
    async retrieveCampaignDetails(campaignName) {
      this.demoGuideBadgeArticle = null
      this.products = []

      const campaignDetails = await C360Repository.getCampaignDetails(campaignName, this.username)

      if (campaignDetails === null) {
        this.campaignTitle = "Unknown campaign"
        this.subtitle = `No campaign found with name ${campaignName}`
        this.products = []
      } else {

        this.feature = `${RankExperimentFeature}-${campaignName}`
        this.campaignTitle = campaignDetails.title
        this.subtitle = campaignDetails.subtitle

        if (this.personalizeUserID && campaignDetails.products.length > 0) {
          const response = await RecommendationsRepository.getRerankedItems(this.personalizeUserID, campaignDetails.products, this.feature)

          if (response.headers) {
            const personalizeRecipe = response.headers['x-personalize-recipe'];
            if (personalizeRecipe) this.demoGuideBadgeArticle = getDemoGuideArticleFromPersonalizeARN(personalizeRecipe);
          }

          this.products = response.data.slice(0, MaxProducts)

        }
        else {
          this.products = campaignDetails.products.slice(0, MaxProducts)
        }


      }
    }
  },
  computed: {
    ...mapState({user: state => state.user, categories: state => state.categories.categories}),
    ...mapGetters(['personalizeUserID', 'username']),
    isLoaded() {
      return this.campaignTitle !== null;
    },
  },
  watch: {
    $route() {
      this.fetchData();
    },
    personalizeUserID() {
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

  @media(min-width: 992px) {

    .products {
      align-self: flex-start;
    }
  }
</style>
