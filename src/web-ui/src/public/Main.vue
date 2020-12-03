<template>
  <Layout>
    <div class="content container">
      <RecommendedProductsSection
        v-if="
          personalizeUserID &&
            ((isLoadingRecommendations && !userRecommendations) || (!isLoadingRecommendations && userRecommendations))
        "
        :feature="feature"
        :recommendedProducts="userRecommendations"
        :explainRecommended="explainRecommended"
      >
        <template #heading>
          {{ userRecommendationsTitle }}
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
import { mapState, mapGetters } from 'vuex';

import { RepositoryFactory } from '@/repositories/RepositoryFactory';
import { AnalyticsHandler } from '@/analytics/AnalyticsHandler';

import Layout from '@/components/Layout/Layout';
import RecommendedProductsSection from '@/components/RecommendedProductsSection/RecommendedProductsSection';

const ProductsRepository = RepositoryFactory.get('products');
const RecommendationsRepository = RepositoryFactory.get('recommendations');
const MAX_RECOMMENDATIONS = 9;
const EXPERIMENT_FEATURE = 'home_product_recs';

export default {
  name: 'Main',
  components: {
    Layout,
    RecommendedProductsSection,
  },
  data() {
    return {
      feature: EXPERIMENT_FEATURE,
      isLoadingRecommendations: true,
      featuredProducts: null,
      userRecommendationsTitle: null,
      userRecommendations: null,
      explainRecommended: null,
    };
  },
  computed: { ...mapState(['user']), ...mapGetters(['personalizeUserID', 'personalizeRecommendationsForVisitor']) },
  async created() {
    this.getFeaturedProducts();
    this.getUserRecommendations();
  },
  methods: {
    async getFeaturedProducts() {
      const { data } = await ProductsRepository.getFeatured();

      this.featuredProducts = data.slice(0, MAX_RECOMMENDATIONS).map((product) => ({ product }));
    },
    async getUserRecommendations() {
      const response = await RecommendationsRepository.getRecommendationsForUser(
        this.personalizeUserID,
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

          if (personalizeRecipe) {
            this.userRecommendationsTitle = this.personalizeRecommendationsForVisitor
              ? 'Inspired by your shopping trends'
              : 'Trending products';
          } else if (experimentName) {
            this.userRecommendationsTitle = 'Recommended for you';
          }

          this.userRecommendations = response.data;

          if (this.userRecommendations.length > 0 && 'experiment' in this.userRecommendations[0]) {
            AnalyticsHandler.identifyExperiment(this.user, this.userRecommendations[0].experiment);
          }
        }
      }

      this.isLoadingRecommendations = false;
    },
  },
};
</script>

<style scoped>
.content {
  padding-top: 1rem;
}
</style>
