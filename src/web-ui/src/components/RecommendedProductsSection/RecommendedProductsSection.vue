<template>
  <section>
    <div class="mb-3 text-left">
      <h2 class="recommendations-heading"><slot name="heading"></slot></h2>
      <div v-if="explainRecommended" class="recommendation-explanation text-muted">
        <i v-if="explainRecommended.activeExperiment" class="fa fa-balance-scale px-1"></i>
        <i v-if="explainRecommended.personalized" class="fa fa-user-check px-1"></i>
        {{ explainRecommended.explanation }}
      </div>
    </div>

    <div class="row">
      <LoadingFallback v-if="isLoading" class="col my-4 text-center"></LoadingFallback>

      <ProductCarousel
        v-else
        :recommendedProducts="recommendedProducts"
        :feature="feature"
        class="col mb-5"
      ></ProductCarousel>
    </div>
  </section>
</template>

<script>
import LoadingFallback from '@/components/LoadingFallback/LoadingFallback';
import ProductCarousel from './ProductCarousel/ProductCarousel';

export default {
  name: 'RecommendedProductsSection',
  props: {
    explainRecommended: {
      type: Object,
      required: false,
    },
    recommendedProducts: {
      type: Array,
      required: false,
    },
    feature: {
      type: String,
      required: false,
    },
  },
  components: {
    LoadingFallback,
    ProductCarousel,
  },
  computed: {
    isLoading() {
      return !this.recommendedProducts;
    },
  },
};
</script>

<style scoped>
.recommendations-heading {
  font-size: 1.5rem;
}

.recommendation-explanation {
  font-style: italic;
}
</style>
