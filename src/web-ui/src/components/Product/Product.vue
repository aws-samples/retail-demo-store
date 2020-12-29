<template>
  <div class="featured-product d-flex flex-column justify-content-between text-left">
    <router-link
      class="link"
      :to="{
        name: 'ProductDetail',
        params: { id: product.id },
        query: { feature, exp: experimentCorrelationId },
      }"
    >
      <div>
        <div><img :src="productImageURL" class="card-img-top" :alt="product.name" /></div>

        <div class="p-3">
          <div class="product-name">{{ product.name }}</div>
          <FiveStars></FiveStars>
          <div>{{ formattedPrice }}</div>
        </div>
      </div>

      <div v-if="experiment" class="experiment mt-1 p-3 d-flex align-items-center text-muted">
        <i class="scale-icon fa fa-balance-scale mr-2"></i> {{ experimentDescription }}
      </div>
    </router-link>
  </div>
</template>

<script>
import { getProductImageUrl } from '@/util/getProductImageUrl';
import { formatPrice } from '@/util/formatPrice';

import FiveStars from '../../components/FiveStars/FiveStars.vue';

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
  name: 'Product',
  components: {
    FiveStars,
  },
  props: {
    product: { type: Object, required: true },
    experiment: { type: Object, required: false },
    feature: { type: String, required: true },
  },

  computed: {
    productImageURL() {
      return getProductImageUrl(this.product);
    },
    formattedPrice() {
      return formatPrice(this.product.price);
    },
    experimentCorrelationId() {
      return this.experiment?.correlationId;
    },
    experimentDescription() {
      if (!this.experiment) return null;

      return `${getFullExperimentType(this.experiment.type)}; Variation: ${this.experiment.variationIndex}`;
    },
  },
};
</script>

<style scoped>
.link {
  color: inherit;
}

.link:hover {
  text-decoration: none;
}

.card-img-overlay {
  opacity: 0.75;
}

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

.scale-icon {
  color: var(--blue-600);
}
</style>
