<template>

    <div class="col-sm-12 col-md-4 col-lg-2 ">
      <router-link :to="{name:'ProductDetail', params: {id: product.id}, query: {exp: experimentCorrelationId, feature: experimentFeature}}" class="unstyled-link" target="_blank">
      <div class="card h-100 recommendation" >
        <img :src="productImageURL" class="card-img" :alt="product.name">
        <div class="card-body d-flex flex-column text-left p-0">
          <p class="card-text m-0 product-name text-muted">{{ product.name }}</p>
          <p class="card-text mt-auto"><small >${{ product.price }}</small></p>
        </div>
      </div>
      </router-link>
    </div>


</template>

<script>
export default {
  name: "LiveRecommendation",
  props: {
    product: null,
    experiment: null
  },
  computed: {
    productImageURL: function () {
      if (this.product.image.includes('://')) {
        return this.product.image;
      } else {
        let root_url = process.env.VUE_APP_IMAGE_ROOT_URL;
        return root_url + this.product.category + '/' + this.product.image;
      }
    },
    experimentCorrelationId: function() {
      return this.experiment ? this.experiment.correlationId : ''
    },
    experimentFeature: function()  {
      return this.experiment ? this.experiment.feature : ''
    }
  }
}
</script>

<style scoped>
.recommendation {
  border: none;
  background-color: transparent;
}

.unstyled-link {
  text-decoration: none;
  color: inherit;
}

.product-name {
  font-size: 0.8rem;
  font-weight: bold;
}
</style>