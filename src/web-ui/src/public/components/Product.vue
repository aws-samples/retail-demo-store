<template>
  <div class="featured-product d-flex flex-column justify-content-between text-left">
    <!-- Card -->
    <router-link class="link" :to="{name:'ProductDetail', params: {id: product.id}, query: {feature: feature, exp: experimentCorrelationId}}">
      <div>
        <div class="p3"><img :src="productImageURL" class="card-img-top" :alt="product.name"></div>

        <div class="p-3">
          <div class="product-name">{{ product.name }}</div>
          <FiveStars />
          <div>${{ product.price.toFixed(2) }}</div>
        </div>
      </div>

      <div v-if="experiment" class="experiment mt-1 p-3 d-flex align-items-center text-muted">
        <i class="scale-icon fa fa-balance-scale mr-2"></i> {{ experimentDescription }}
      </div>
    </router-link>
  </div>
</template>

<script>
import FiveStars from '../../components/FiveStars/FiveStars.vue'
export default {
  name: 'Product',
  components: {
    FiveStars
  },
  props: {
      product: null,
      feature: null,
      experiment: null
  },
  data () {
    return {
      errors: []
    }
  },
  created () {
  },
  methods: {
  },
  computed: {
    productImageURL: function () {
      if (this.product.image.includes('://')) {
        return this.product.image
      }
      else {
        let root_url = process.env.VUE_APP_IMAGE_ROOT_URL
        return root_url + this.product.category + '/' + this.product.image
      }
    },
    experimentCorrelationId: function() {
      return this.experiment ? this.experiment.correlationId : ''
    },
    experimentDescription: function() {
      let tt
      if (this.experiment) {
        if (this.experiment.type == 'ab') {
          tt = 'Experiment: A/B'
        }
        else if (this.experiment.type == 'interleaving') {
          tt = 'Experiment: Interleaved'
        }
        else if (this.experiment.type == 'mab') {
          tt = 'Experiment: Multi-Armed Bandit'
        }
        else if (this.experiment.type == 'optimizely') {
          tt = 'Experiment: Optimizely'
        }
        else {
          tt = 'Experiment: Unknown'
        }
        tt += '; Variation: ' + this.experiment.variationIndex
      }
      return tt
    }
  }
}
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
