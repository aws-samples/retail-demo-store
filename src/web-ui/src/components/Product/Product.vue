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
        <div class="position-relative">
          <div v-if="promotionName != null" class="small promoted-product-banner">Promoted</div>
          <img :src="productImageURL" class="card-img-top" :alt="product.name" />
        </div>

        <div class="p-3">
          <div class="product-name">{{ product.name }}</div>
          <FiveStars></FiveStars>
          <div>{{ formattedPrice }}</div>
          <div v-if="experiment" class="experiment mt-1 align-items-center text-muted small">
            <i class="scale-icon fa fa-balance-scale mr-1"></i> {{ experimentDescription }}
          </div>
        </div>
        <div v-if="fenixenablePDP == 'TRUE'" class="fenix-estimates">
          <FenixList
            :currentvariant="fenixcurrentvariant"
          >
          </FenixList>
        </div>
      </div>
    </router-link>
  </div>
</template>

<script>
import { getProductImageUrl } from '@/util/getProductImageUrl';
import { formatPrice } from '@/util/formatPrice';

import FiveStars from '../../components/FiveStars/FiveStars.vue';
import FenixList from '@/components/Fenix/FenixList.vue';

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
    FenixList
  },
  props: {
    product: { type: Object, required: true },
    experiment: { type: Object, required: false },
    promotionName: { type: String, required: false },
    feature: { type: String, required: true },
  },

  data() {
    return {
      fenixenablePDP : import.meta.env.VITE_FENIX_ENABLED_PDP,
    };
  },
  computed: {
    fenixcurrentvariant(){
      return this.product.id;
    },
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
    promotedProduct() {
      return this.promotionName
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

.promoted-product-banner {
  float: left;
  position: absolute;
  top: 0px;
  left: 0px;
  width: 100%;
  color: white;
  background-color: var(--blue-500);
  text-align: center;
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
