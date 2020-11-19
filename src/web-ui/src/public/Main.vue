<template>
  <Layout>
    <div class="content container">
      <!-- Category List -->
      <div class="container">
        <h4>Categories</h4>
        <div class="container mb-4" v-if="!categories">
          <i class="fas fa-spinner fa-spin fa-3x"></i>
        </div>
        <div class="row">
          <div class="card-deck col-sm-12 col-md-12 col-lg-12 mt-4">
            <Category v-for="category in categories" v-bind:key="category.id" :category="category" />
          </div>
        </div>
      </div>

      <RecommendedProductsSection
        v-if="user"
        :feature="feature"
        :recommendedProducts="userRecommendations"
        :explainRecommended="explainRecommended"
      >
        <template #heading>
          Inspired by your shopping trends
        </template>
      </RecommendedProductsSection>

      <RecommendedProductsSection :feature="feature" :recommendedProducts="featuredProducts">
        <template #heading>
          Featured products
        </template>
      </RecommendedProductsSection>
    </div>
  </Layout>
</template>

<script>
import { RepositoryFactory } from '@/repositories/RepositoryFactory';
import { AnalyticsHandler } from '@/analytics/AnalyticsHandler';

import Category from './components/Category.vue';
import Layout from '@/components/Layout/Layout';
import RecommendedProductsSection from '@/components//RecommendedProductsSection/RecommendedProductsSection';

import { user } from '@/mixins/user';

const ProductsRepository = RepositoryFactory.get('products');
const RecommendationsRepository = RepositoryFactory.get('recommendations');
const MAX_RECOMMENDATIONS = 9;
const EXPERIMENT_FEATURE = 'home_product_recs';

export default {
  name: 'Main',
  components: {
    Category,
    Layout,
    RecommendedProductsSection,
  },
  mixins: [user],
  data() {
    return {
      feature: EXPERIMENT_FEATURE,
      categories: null,
      featuredProducts: null,
      userRecommendations: null,
      explainRecommended: null,
    };
  },
  async created() {
    this.getCategories();
    this.getFeaturedProducts();
    this.getUserRecommendations();
  },
  methods: {
    async getCategories() {
      const { data } = await ProductsRepository.getCategories();

      this.categories = data;
    },
    async getFeaturedProducts() {
      const { data } = await ProductsRepository.getFeatured();

      this.featuredProducts = data.slice(0, MAX_RECOMMENDATIONS).map((product) => ({ product }));
    },
    async getUserRecommendations() {
      if (!this.user) return;

      const response = await RecommendationsRepository.getRecommendationsForUser(
        this.user.id,
        '',
        MAX_RECOMMENDATIONS,
        EXPERIMENT_FEATURE,
      );

      if (response.headers) {
        const experimentName = response.headers['x-experiment-name'];
        const personalizeRecipe = response.headers['x-personalize-recipe'];

        if (experimentName || personalizeRecipe) {
          const explanation = experimentName
            ? `Active experiment: ${experimentName}`
            : `Personalize recipe: ${personalizeRecipe}`;

          this.explainRecommended = {
            activeExperiment: !!experimentName,
            personalized: !!personalizeRecipe,
            explanation,
          };
        }
      }

      this.userRecommendations = response.data;

      if (this.userRecommendations.length > 0 && 'experiment' in this.userRecommendations[0]) {
        AnalyticsHandler.identifyExperiment(this.user, this.userRecommendations[0].experiment);
      }
    },
  },
};
</script>

<style scoped>
.content {
  padding-top: 1rem;
}
</style>
