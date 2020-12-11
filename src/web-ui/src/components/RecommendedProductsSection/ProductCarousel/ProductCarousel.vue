<template>
  <Carousel :settings="carouselSettings">
    <div
      v-for="recommendation in recommendedProducts"
      :key="recommendation.product.id"
      class="px-1 text-left align-self-stretch d-flex align-items-stretch text-decoration-none"
    >
      <router-link
        :to="{
          name: 'ProductDetail',
          params: { id: recommendation.product.id },
          query: { exp: getExperimentCorrelationId(recommendation.experiment), feature },
        }"
        class="featured-product d-flex flex-column justify-content-between"
      >
        <div>
          <div class="mb-2"><img :src="getProductImageUrl(recommendation.product)" alt="" class="img-fluid" /></div>

          <div class="px-3 pb-3">
            <div class="product-name">
              {{ recommendation.product.name }}
            </div>

            <FiveStars class="my-1"></FiveStars>
            <div>{{ formatPrice(recommendation.product.price) }}</div>
          </div>
        </div>

        <div v-if="recommendation.experiment" class="experiment mt-1 p-3 d-flex align-items-center text-muted">
          <i class="icon-scale fa fa-balance-scale mr-2"></i> {{ getExperimentDescription(recommendation.experiment) }}
        </div>
      </router-link>
    </div>
  </Carousel>
</template>

<script>
import { getProductImageUrl } from '@/util/getProductImageUrl';
import { formatPrice } from '@/util/formatPrice';
import Carousel from '@/components/Carousel/Carousel';
import FiveStars from '@/components/FiveStars/FiveStars';

const getFullExperimentType = (type) => {
  switch (type) {
    case 'ab':
      return 'Experiment: A/B';
    case 'interleaving':
      return 'Experiment: Interleaved';
    case 'mab':
      return 'Experiment: Multi-Armed Bandit';
    case 'optimizely':
      return 'Experiment: Optimizely';
    default:
      return 'Experiment: Unknown';
  }
};

export default {
  name: 'ProductCarousel',
  components: { Carousel, FiveStars },
  props: {
    recommendedProducts: {
      type: Array,
      required: true,
    },
    feature: {
      type: String,
      required: false,
    },
  },
  data() {
    return {
      carouselSettings: {
        dots: false,
        slidesToShow: 2,
        responsive: [
          {
            breakpoint: 480,
            settings: { slidesToShow: 3 },
          },
          {
            breakpoint: 768,
            settings: { slidesToShow: 4 },
          },
        ],
      },
    };
  },
  methods: {
    getExperimentCorrelationId(experiment) {
      return experiment?.correlationId;
    },
    getExperimentDescription(experiment) {
      if (!experiment) return null;

      return `${getFullExperimentType(experiment.type)}; Variation: ${experiment.variationIndex}`;
    },
    getProductImageUrl,
    formatPrice,
  },
};
</script>

<style scoped>
.featured-product {
  border: 1px solid var(--grey-300);
  text-decoration: none;
  color: inherit;
}

.product-name {
  display: -webkit-box;
  -webkit-line-clamp: 1;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.experiment {
  font-size: 0.95rem;
}

.scale-icon { 
  color: var(--blue-600);
}
</style>
