<template>
  <div class="col-sm-12 col-md-4 col-lg-4 mb-4">
    <!-- Card -->
    <div class="card mx-auto h-100 product-card">
      <router-link :to="{name:'ProductDetail', params: {id: product.id}, query: {exp: experimentCorrelationId}}">
        <img :src="productImageURL" class="card-img-top" :alt="product.name">
      </router-link>
      <div class="card-body">
        <router-link class="btn btn-secondary btn-block mt-auto" :to="{name:'ProductDetail', params: {id: product.id}, query: {feature: feature, exp: experimentCorrelationId}}">Details</router-link>  
      </div>
      <div class="card-footer" v-if="experiment">
        <small class="text-muted"><i class="fa fa-balance-scale"></i> {{ experimentDescription }}</small>
      </div>
  </div>

  </div>
</template>

<script>
export default {
  name: 'Product',
  components: {
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

  .card-img-overlay {
    opacity: 0.75;
  }
  
</style>