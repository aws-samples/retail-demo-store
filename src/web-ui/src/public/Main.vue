<template>
  <Layout>
    <div class="container">
      <section class="mb-5">
        <div v-if="userRecommendationsTitle" class="mb-3 text-left">
          <h2 class="recommendations-heading">
            {{ userRecommendationsTitle }}
            <DemoGuideBadge
              v-if="userRecommendationsDemoGuideBadgeArticle"
              :article="userRecommendationsDemoGuideBadgeArticle"
              hideTextOnSmallScreens
            ></DemoGuideBadge>
          </h2>
          <div v-if="recommendationsExperiment" class="recommendation-explanation text-muted small">
            <i class="fa fa-balance-scale px-1"></i>
            {{ recommendationsExperiment }}
          </div>
        </div>

        <div
          v-if="
            personalizeUserID &&
              ((isLoadingRecommendations && !userRecommendations) || (!isLoadingRecommendations && userRecommendations))
          "
        >
          <LoadingFallback v-if="!userRecommendations" class="col my-4 text-center"></LoadingFallback>

          <div v-else class="user-recommendations">
            <Product
              v-for="item in userRecommendations"
              :key="item.product.id"
              :product="item.product"
              :experiment="item.experiment"
              :promotionName="item.promotionName"
              :feature="featureUserRecs"
            ></Product>
          </div>
        </div>

        <div v-if="!isLoadingRecommendations && !userRecommendationsTitle" class="text-left">
          <em>
            Personalized recommendations do not appear to be enabled for this instance of the storefront yet. Please complete the Personalization workshop labs to add personalized capabilities.
            In the meantime, the default user experience will provide product information directly from the catalog.
          </em>
        </div>
      </section>

      <RecommendedProductsSection
        :feature="featureRerank"
        :recommendedProducts="featuredProducts"
        :experiment="featuredProductsExperiment"
      >
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

import Layout from '@/components/Layout/Layout.vue';
import RecommendedProductsSection from '@/components/RecommendedProductsSection/RecommendedProductsSection.vue';
import DemoGuideBadge from '@/components/DemoGuideBadge/DemoGuideBadge.vue';
import Product from '@/components/Product/Product.vue';
import LoadingFallback from '@/components/LoadingFallback/LoadingFallback.vue';

import { getDemoGuideArticleFromPersonalizeARN } from '@/partials/AppModal/DemoGuide/config';

const ProductsRepository = RepositoryFactory.get('products');
const RecommendationsRepository = RepositoryFactory.get('recommendations');
const MAX_RECOMMENDATIONS = 12;
const EXPERIMENT_USER_RECS_FEATURE = 'home_product_recs';
const EXPERIMENT_USER_RECS_COLD_FEATURE = 'home_product_recs_cold';
const EXPERIMENT_RERANK_FEATURE = 'home_featured_rerank';

export default {
  name: 'Main',
  components: {
    Layout,
    RecommendedProductsSection,
    DemoGuideBadge,
    Product,
    LoadingFallback,
  },
  data() {
    return {
      featureUserRecs: EXPERIMENT_USER_RECS_FEATURE,
      featureRerank: EXPERIMENT_RERANK_FEATURE,
      isLoadingRecommendations: true,
      featuredProducts: null,
      featuredProductsDemoGuideBadgeArticle: null,
      featuredProductsExperiment: null,
      userRecommendationsDemoGuideBadgeArticle: null,
      userRecommendations: null,
      recommendationsExperiment: null,
      userRecommendationsTitle: null,
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
      this.featuredProductsExperiment = null;
      this.featuredProducts = null;

      const { data: featuredProducts } = await ProductsRepository.getFeatured();

      if (this.personalizeUserID && featuredProducts.length > 0) {
        const { data: rerankedProducts, headers } = await RecommendationsRepository.getRerankedItems(
          this.personalizeUserID,
          featuredProducts,
          EXPERIMENT_RERANK_FEATURE,
        );

        const personalizeRecipe = headers['x-personalize-recipe'];
        const experimentName = headers['x-experiment-name'];

        if (personalizeRecipe)
          this.featuredProductsDemoGuideBadgeArticle = getDemoGuideArticleFromPersonalizeARN(personalizeRecipe);

        if (experimentName) this.featuredProductsExperiment = `Active experiment: ${experimentName}`;

        this.featuredProducts = rerankedProducts.slice(0, MAX_RECOMMENDATIONS).map((product) => ({ product }));
      } else {
        this.featuredProducts = featuredProducts.slice(0, MAX_RECOMMENDATIONS).map((product) => ({ product }));
      }
    },
    async getUserRecommendations() {
      this.isLoadingRecommendations = true;
      this.userRecommendationsTitle = null;
      this.userRecommendations = null;
      this.recommendationsExperiment = null;
      this.userRecommendationsDemoGuideBadgeArticle = null;

      var response;
      if (this.personalizeRecommendationsForVisitor) {
        this.featureUserRecs = EXPERIMENT_USER_RECS_FEATURE;

        response = await RecommendationsRepository.getRecommendationsForUser(
          this.personalizeUserID,
          '',
          MAX_RECOMMENDATIONS,
          this.featureUserRecs
        );
      }
      else {
        this.featureUserRecs = EXPERIMENT_USER_RECS_COLD_FEATURE;

        response = await RecommendationsRepository.getPopularProducts(
          this.personalizeUserID,
          '',
          MAX_RECOMMENDATIONS,
          this.featureUserRecs
        );
      }

      if (response.headers) {
        const experimentName = response.headers['x-experiment-name'];
        const personalizeRecipe = response.headers['x-personalize-recipe'];

        if (experimentName || personalizeRecipe) {
          if (experimentName) this.recommendationsExperiment = `Active experiment: ${experimentName}`;

          if (personalizeRecipe) {
            this.userRecommendationsTitle = this.personalizeRecommendationsForVisitor
              ? 'Inspired by your shopping trends'
              : 'Popular products';

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
.recommendations-heading {
  font-size: 1rem;
}

.recommendation-explanation {
  font-style: italic;
}

.user-recommendations {
  display: grid;
  grid-gap: 1rem;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
}

@media (min-width: 768px) {
  .recommendations-heading {
    font-size: 1.4rem;
  }

  .user-recommendations {
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  }
}
</style>
