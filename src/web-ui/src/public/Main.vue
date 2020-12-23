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
        :experiment="recommendationsExperiment"
      >
        <template #heading v-if="userRecommendationsTitle">
          {{ userRecommendationsTitle }}
          <DemoGuideBadge
            v-if="userRecommendationsDemoGuideBadgeArticle"
            :article="userRecommendationsDemoGuideBadgeArticle"
            hideTextOnSmallScreens
          ></DemoGuideBadge>
        </template>
      </RecommendedProductsSection>

      <RecommendedProductsSection :feature="feature" :recommendedProducts="featuredProducts">
        <template #heading>
          Featured products
          <DemoGuideBadge
            v-if="featuredProductsDemoGuideBadgeArticle"
            :article="featuredProductsDemoGuideBadgeArticle"
            hideTextOnSmallScreens
          ></DemoGuideBadge>
        </template>
      </RecommendedProductsSection>
    </div>
  </Layout>
</template>

<script>
import { mapState, mapGetters, mapActions } from 'vuex';

import { RepositoryFactory } from '@/repositories/RepositoryFactory';
import { AnalyticsHandler } from '@/analytics/AnalyticsHandler';
import { Modals } from '@/partials/AppModal/config';

import Layout from '@/components/Layout/Layout';
import RecommendedProductsSection from '@/components/RecommendedProductsSection/RecommendedProductsSection';
import DemoGuideBadge from '@/components/DemoGuideBadge/DemoGuideBadge';

import { getDemoGuideArticleFromPersonalizeARN } from '@/partials/AppModal/DemoGuide/config';

const ProductsRepository = RepositoryFactory.get('products');
const RecommendationsRepository = RepositoryFactory.get('recommendations');
const MAX_RECOMMENDATIONS = 9;
const EXPERIMENT_FEATURE = 'home_product_recs';

export default {
  name: 'Main',
  components: {
    Layout,
    RecommendedProductsSection,
    DemoGuideBadge,
  },
  data() {
    return {
      feature: EXPERIMENT_FEATURE,
      isLoadingRecommendations: true,
      featuredProductsDemoGuideBadgeArticle: null,
      userRecommendationsDemoGuideBadgeArticle: null,
      recommendationsExperiment: null,
      featuredProducts: null,
      userRecommendationsTitle: null,
      userRecommendations: null,
    };
  },
  computed: {
    ...mapState({ user: (state) => state.user, demoWalkthroughShown: (state) => state.demoWalkthroughShown.shown }),
    ...mapGetters(['personalizeUserID', 'personalizeRecommendationsForVisitor']),
  },
  async created() {
    this.fetchData();
  },
  mounted() {
    if (!this.demoWalkthroughShown) {
      this.openModal(Modals.DemoWalkthrough);
      this.markDemoWalkthroughAsShown();
    }
  },
  methods: {
    ...mapActions(['openModal', 'markDemoWalkthroughAsShown']),
    fetchData() {
      this.getFeaturedProducts();
      this.getUserRecommendations();
    },
    async getFeaturedProducts() {
      this.featuredProductsDemoGuideBadgeArticle = null;
      this.featuredProducts = null;

      const { data, headers } = await ProductsRepository.getFeatured();

      const personalizeRecipe = headers['x-personalize-recipe'];

      if (personalizeRecipe)
        this.featuredProductsDemoGuideBadgeArticle = getDemoGuideArticleFromPersonalizeARN(personalizeRecipe);

      this.featuredProducts = data.slice(0, MAX_RECOMMENDATIONS).map((product) => ({ product }));
    },
    async getUserRecommendations() {
      this.isLoadingRecommendations = true;
      this.userRecommendationsTitle = null;
      this.userRecommendations = null;
      this.recommendationsExperiment = null;
      this.userRecommendationsDemoGuideBadgeArticle = null;

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
          if (experimentName) this.recommendationsExperiment = `Active experiment: ${experimentName}`;

          if (personalizeRecipe) {
            this.userRecommendationsTitle = this.personalizeRecommendationsForVisitor
              ? 'Inspired by your shopping trends'
              : 'Trending products';

            this.userRecommendationsDemoGuideBadgeArticle = getDemoGuideArticleFromPersonalizeARN(personalizeRecipe);
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
  watch: {
    user() {
      this.fetchData();
    },
  },
};
</script>

<style scoped>
.content {
  padding-top: 1rem;
}
</style>
