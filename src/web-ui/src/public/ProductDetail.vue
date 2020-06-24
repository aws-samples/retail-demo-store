<template>
<div class="container">

  <!-- Loading Indicator -->
  <div class="container mb-4" v-if="!product">
    <i class="fas fa-spinner fa-spin fa-3x"></i>
  </div>

  <!-- Product Detail-->
  <div class="row" v-if="product">
    <div class="col-sm-12 col-md-6 col-lg-6">
      <img :src="productImageURL" class="card-img-top" alt="...">
    </div>
    <div class="col-sm-12 col-md-6 col-lg-6">
       <h5>{{ product.name }}</h5>
       <p>{{ product.description }}</p>
       <p>${{ product.price }}</p>
       <p>
        <i class="fas fa-star"></i><i class="fas fa-star"></i><i class="fas fa-star"></i><i class="fas fa-star"></i><i class="fas fa-star"></i>
       </p>       
       <button class="btn btn-outline-primary" v-on:click="addToCart()"> Add to Cart </button>
    </div>
  </div>

  <!-- Recommendations -->
  <hr/>
  <h5>What other items do customers view related to this product?</h5>
  <div v-if="explain_recommended" class="text-muted text-center">
    <small><em><i v-if="active_experiment" class="fa fa-balance-scale"></i><i v-if="personalized" class="fa fa-user-check"></i> {{ explain_recommended }}</em></small>
  </div>

  <div class="container related-products">
    <div class="container mb-4" v-if="!related_products.length">
      <i class="fas fa-spinner fa-spin fa-3x"></i>
    </div>
    <div class="row">
      <div class="card-deck col-sm-12 col-md-12 col-lg-12 mt-4">
        <Product v-for="recommendation in related_products" 
          v-bind:key="recommendation.product.id"
          :product="recommendation.product"
          :experiment="recommendation.experiment"
          :feature="feature"
        />
      </div>
    </div>
  </div>
    
</div>
</template>

<script>
import AmplifyStore from '@/store/store'

import { RepositoryFactory } from '@/repositories/RepositoryFactory'
import { AnalyticsHandler } from '@/analytics/AnalyticsHandler'

const ProductsRepository = RepositoryFactory.get('products')
const CartsRepository = RepositoryFactory.get('carts')
const RecommendationsRepository = RepositoryFactory.get('recommendations')
const MaxRecommendations = 6
const ExperimentFeature = 'product_detail_related'

import Product from './components/Product.vue'

import swal from 'sweetalert';

export default {
  name: 'ProductDetail',
  components: {
    Product
  },
  props: {
  },
  data () {
    return {
      feature: ExperimentFeature,
      errors: [],
      product: null,
      related_products: [],
      explain_recommended: '',
      active_experiment: false,
      personalized: false
    }
  },
  async created () {
    this.fetchData();
  },
  methods: {
    addToCart: function () {

      if (this.cart.items == null) {
        this.cart.items = new Array()
      } 

      var exists = false
      var qty = 1
      for (var item in this.cart.items) {
        if (this.cart.items[item].product_id == this.product.id)
        {
          exists = true
          qty = this.cart.items[item].quantity + 1
          this.cart.items[item].quantity = this.cart.items[item].quantity + 1
        } 
      }

      if (exists == false) {
          let newItem = {
            product_id: this.product.id,
            quantity: qty,
            price: this.product.price
          }
          this.cart.items.push(newItem)
      }

      CartsRepository.updateCart(this.cart)
      this.getCart()

      AnalyticsHandler.productAddedToCart(this.user, this.cart, this.product, qty, this.$route.query.feature, this.$route.query.exp)

      swal({
        title: "Added to Cart",
        icon: "success",
        buttons: {
          cancel: "Continue Shopping",
          cart: "View Cart"
        }
      }).then((value) => {
        switch (value) {
          case "cancel":  
            break;
          case "cart":
            this.$router.push('/cart');
        }
      });
    },
    async getProductByID (product_id){
      const { data } = await ProductsRepository.getProduct(product_id)
      this.product = data
      this.getRelatedProducts()
    },
    async fetchData (){
      await this.getProductByID(this.$route.params.id)
      this.getCart()
      this.recordProductViewed()
    },
    recordProductViewed() {
      if (this.product) {
        AnalyticsHandler.productViewed(this.user, this.product, this.$route.query.feature, this.$route.query.exp)
      }
    },
    async getRelatedProducts() {
      const response = await RecommendationsRepository.getRelatedProducts(this.user ? this.user.id : '', this.product.id, MaxRecommendations, ExperimentFeature)

      if (response.headers) {
        if (response.headers['x-personalize-recipe']) {
          this.personalized = true
          this.explain_recommended = 'Personalize recipe: ' + response.headers['x-personalize-recipe']
        }
        if (response.headers['x-experiment-name']) {
          this.active_experiment = true
          this.explain_recommended = 'Active experiment: ' + response.headers['x-experiment-name']
        }
      }

      this.related_products = response.data

      if (this.related_products.length > 0 && 'experiment' in this.related_products[0]) {
        AnalyticsHandler.identifyExperiment(this.user, this.related_products[0].experiment)
      }
    },
    async getCart () {
      if (this.cartID) {
        const { data } = await CartsRepository.getCartByID(this.cartID)
        // Since cart service holds carts in memory, they can be lost on restarts. 
        // Make sure our cart was returned. Otherwise create a new one.
        if (data.id == this.cartID) {
          this.cart = data
        }
        else {
          console.warn('Cart ' + this.cartID + ' not found. Creating new cart. Was cart service restarted?')
          this.createCart()
        }
      }
      else {
        this.createCart()
      }
    }, 
    async createCart (){
      if (this.user) {
        const { data } = await CartsRepository.createCart(this.user.username)
        this.cart = data
      } else {
        const { data } = await CartsRepository.createCart('guest')
        this.cart = data
      }
      AmplifyStore.commit('setCartID', this.cart.id)
    }
  },
  computed: {
    user() { 
      return AmplifyStore.state.user
    },
    cartID() {
      return AmplifyStore.state.cartID
    },
    productImageURL: function () {
      if (this.product.image.includes('://')) {
        return this.product.image
      }
      else {
        let root_url = process.env.VUE_APP_IMAGE_ROOT_URL
        return root_url + this.product.category + '/' + this.product.image
      }
    }
  },
  watch: {
    // call again the method if the route changes
    '$route': 'fetchData'
  },
}
</script>

<style scoped>
  
</style>