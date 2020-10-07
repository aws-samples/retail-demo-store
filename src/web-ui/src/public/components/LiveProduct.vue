<template>
  <router-link :to="{name:'ProductDetail', params: {id: product.id}, query: {di: discount, exp: experimentCorrelationId, feature: experimentFeature}}" target="_blank" class="unstyled-link" >
    <div class="card mb-1 live-product-card" style="max-width: 540px" v-bind:class="{active: active}">
      <div class="row no-gutters">
        <div class="col-md-4 my-auto">
          <img :src="productImageURL" class="card-img align-items-center ml-xl-0 ml-1" :alt="product.name">
        </div>
        <div class="col-md-8 my-auto">
          <div class="card-body p-2">
            <p class="card-text m-0 product-name text-secondary">{{ product.name }}</p>
            <small v-bind:class="{discountprice: discount}">${{ product.price }}</small>
            <small v-if="discount" class="ml-1 font-weight-bold"> ${{ (product.price * 0.8).toFixed(2) }}</small><br>
            <p v-if="discount"  class="m-0 font-weight-bold discount-message">Limited offer, only for you!</p>
          </div>
        </div>
      </div>
    </div>
  </router-link>

</template>

<script>
export default {
  name: "LiveProduct",
  props: {
    product: null,
    active: null,
    experiment: null,
    discount: null
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
.active {
  background-color: #daf6c0 !important;
}

.discountprice {
  text-decoration: line-through;
}

.unstyled-link {
  text-decoration: none;
  color: inherit;

}

.live-product-card {
  border: none;
  background-color: #f1f1f1;
}

.product-name {
  font-size: 0.8rem;
  font-weight: bold;
}

.discount-message {
  color: #ee814c;
  font-size: 0.8rem;
}

</style>