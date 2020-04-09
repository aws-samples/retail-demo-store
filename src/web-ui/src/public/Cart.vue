<template>
  <div class="content">

    <!-- Loading Indicator -->
    <div class="container" v-if="!cart">
      <i class="fas fa-spinner fa-spin fa-3x"></i>
    </div>

    <div class="container" v-if="cart">
      <div class="alert alert-secondary" v-if="!cart.items">No Items In Cart</div>
    </div>

    <div class="container" v-if="cart">
      <div v-if="cart.items">
        <div class="alert alert-secondary" v-if="cart.items.length == 0">No Items In Cart</div>
      </div>
    </div>    

    <div class="container" v-if="cart">
      <div class="row" v-if="cart.items && cart.items.length > 0">
        <div class="col-md-8 mb-4">
         <h4 class="d-flex justify-content-between align-items-center mb-3">
            <span class="text-muted">Items</span>
          </h4>
          <table class="table">
            <tr>
              <th class="pl-0 pr-1 d-none d-sm-table-cell"></th>
              <th class="px-1">Item</th>
              <th class="px-1"><span class="d-none d-sm-inline">Quantity</span><span class="d-xs-inline d-sm-none">Qty</span></th>
              <th class="px-1">Price</th>
              <th class="pr-0 pl-1"></th>          
            </tr>
            <CartItem v-for="item in cart.items" 
              v-bind:key="item.product_id"
              :product_id="item.product_id"
              :quantity="item.quantity"
              @removeFromCart="removeFromCart"
              @increaseQuantity="increaseQuantity"
              @decreaseQuantity="decreaseQuantity"
            />
          </table>
        </div>
        <div class="col-md-4">
          <h4 class="d-flex justify-content-between align-items-center mb-3">
            <span class="text-muted">Summary</span>
            <span class="badge badge-secondary badge-pill">{{ this.cartQuantity }}</span>
          </h4>
          <div class="text-dark">
          <ul class="list-group mb-3">
            <li class="list-group-item d-flex justify-content-between">
              <span>Sub Total (USD)</span>
              <strong>${{ this.cartSubTotal.toFixed(2) }}</strong>
            </li>
            <li class="list-group-item d-flex justify-content-between">
              <span>Tax (USD)</span>
              <strong>${{ this.cartTaxRate.toFixed(2) }}</strong>
            </li>
            <li class="list-group-item d-flex justify-content-between">
              <span>Shipping (USD)</span>
              <strong>${{ this.cartShippingRate.toFixed(2) }}</strong>
            </li>
            <li class="list-group-item d-flex justify-content-between">
              <span>Total (USD)</span>
              <strong>${{ this.cartTotal.toFixed(2) }}</strong>
            </li>            
          </ul>
            <button class="btn btn-primary mb-4 btn-block" v-on:click="checkout()"> Checkout </button>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>

<script>
import AmplifyStore from '@/store/store'

import { RepositoryFactory } from '@/repositories/RepositoryFactory'
import { AnalyticsHandler } from '@/analytics/AnalyticsHandler'

import CartItem from './components/CartItem.vue'

const CartsRepository = RepositoryFactory.get('carts')
const ProductsRepository = RepositoryFactory.get('products')

export default {
  name: 'Cart',
  components: {
    CartItem
  },
  props: {
  },
  data () {
    return {  
      errors: [],
      cart: null
    }
  },
  async created() {
    await this.getCart();
    if (this.cart) {
      AnalyticsHandler.cartViewed(this.user, this.cart, this.cartQuantity, this.cartSubTotal, this.cartTotal)
    }
  },
  methods: {
    async getProductByID (product_id){
      const { data } = await ProductsRepository.getProduct(product_id)
      return data
    },    
    async getCart (){
      if (this.cartID) {
        const { data } = await CartsRepository.getCartByID(this.cartID)
        // Since cart service currently holds carts in memory, they can be lost on restarts. 
        // Make sure our cart was returned. Otherwise create a new one.
        if (data.id == this.cartID) {
          this.cart = data
        }
        else {
          console.warn('Cart ' + this.cartID + ' not found. Creating new cart. Was cart service restarted?')
          this.createCart()
        }
      }
      else 
      {
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
    },
    async updateCart (){
      const { data } = await CartsRepository.updateCart(this.cart)
      this.cart = data
    },       
    checkout: function () {
      this.$router.push('/checkout');
    },    
    removeFromCart (value) {
      for (var item in this.cart.items) {
        if (this.cart.items[item].product_id == value) {
          let cartItem = this.cart.items[item]
          this.cart.items.splice(item, 1)
          AnalyticsHandler.productRemovedFromCart(this.user, this.cart, cartItem, cartItem.quantity)
        }
      }

      this.updateCart()
    },
    increaseQuantity (value) {
      for (var item in this.cart.items) {
        if (this.cart.items[item].product_id == value) {
          this.cart.items[item].quantity = this.cart.items[item].quantity + 1
          AnalyticsHandler.productQuantityUpdatedInCart(this.user, this.cart, this.cart.items[item], 1)
        }
      }

      this.updateCart()
    },
    decreaseQuantity (value) {
      for (var item in this.cart.items) {
        if (this.cart.items[item].product_id == value) {
          let origQuantity = this.cart.items[item].quantity
          this.cart.items[item].quantity = this.cart.items[item].quantity - 1
          if (this.cart.items[item].quantity == 0) {
            let cartItem = this.cart.items[item]
            this.cart.items.splice(item, 1)
            AnalyticsHandler.productRemovedFromCart(this.user, this.cart, cartItem, origQuantity)
          }
          else {
            AnalyticsHandler.productQuantityUpdatedInCart(this.user, this.cart, this.cart.items[item], -1)
          }
        }
      }

      this.updateCart()
    }
  },
  computed: {
    user() { 
      return AmplifyStore.state.user
    },    
    cartID() {
      return AmplifyStore.state.cartID
    },
    cartSubTotal() {
      var subtotal = 0.00

      for (var item in this.cart.items) {
        var cost = this.cart.items[item].quantity * this.cart.items[item].price // Need to Load Product Price
        subtotal = subtotal + cost
      }

      return subtotal

    },
    cartTaxRate() {
      const taxRate = 0.05
      return this.cartSubTotal * taxRate
    },
    cartShippingRate() {
      var shippingRate = 10.00

      if (this.cartSubTotal > 100.00) {
        shippingRate = 0.00
      }
      return shippingRate
    },
    cartTotal() {
      return this.cartSubTotal + this.cartTaxRate + this.cartShippingRate
    },
    cartQuantity() {

      var quantity = 0;

      for (var item in this.cart.items) {
        quantity = quantity + this.cart.items[item].quantity
      }
      return quantity
    }
  },
}
</script>
