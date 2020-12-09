<template>
  <Layout :isLoading="!cart" :previousPageLinkProps="previousPageLinkProps">
    <div class="content">

      <div class="container" v-if="cart">
        <div class="alert alert-secondary" v-if="!cart.items">No Items In Cart</div>
      </div>

      <div class="container" v-if="cart">
        <div v-if="cart.items">
          <div class="alert alert-secondary" v-if="cart.items.length == 0">No Items In Cart</div>
        </div>
      </div>

      <div class="container" v-if="cart && showCheckout == false">
        <div class="row justify-content-center">
          <div class="card p-4" style="width: 15rem">
            <button class="btn btn-success mb-3" v-on:click="signIn">Login to Checkout</button>
            <button class="btn btn-light" v-on:click="guestCheckout">Checkout as Guest</button>
          </div>
        </div>
      </div>

      <div class="container" v-if="cart">
        <div class="row text-left" v-if="showCheckout == true">
          <div class="col-md-4 order-md-2">
            <div class="card p-1">
              <div class="card-body">
                <h4 class="d-flex justify-content-between align-items-center mb-3 card-title text-muted">
                  Order Summary
                </h4>
                <ul class="list-group list-group-flush mb-3">
                  <li class="list-group-item p-1 d-flex justify-content-between">
                    <span>{{ this.cartQuantity }} item{{ this.cartQuantity === 1 ? '' : 's' }} in cart</span>
                    <strong>${{ this.cartSubTotal.toFixed(2) }}</strong>
                  </li>
                  <li class="list-group-item p-1 d-flex justify-content-between border-top-0">
                    <span>Shipping & handling:</span>
                    <strong>${{ this.cartShippingRate.toFixed(2) }}</strong>
                  </li>
                  <li class="list-group-item p-1 d-flex justify-content-between">
                    <span>Total before tax:</span>
                    <strong>${{ this.cartTotalBeforeTax.toFixed(2) }}</strong>
                  </li>
                  <li class="list-group-item p-1 d-flex justify-content-between border-top-0">
                    <span>Tax to be collected:</span>
                    <strong>${{ this.cartTaxRate.toFixed(2) }}</strong>
                  </li>
                  <li class="list-group-item p-1 d-flex justify-content-between border-bottom-0">
                    <span>Order total:</span>
                    <strong>${{ this.cartTotal.toFixed(2) }}</strong>
                  </li>
                </ul>
                <button class="checkout-btn btn btn-outline-dark btn-block btn-lg btn-block" v-on:click="submitOrder">Place your Order</button>
              </div>
            </div>

            <button v-if="pinpointEnabled && user" v-on:click="triggerAbandonedCartEmail" class="abandoned-cart-btn btn btn-primary btn-lg m-4">
              Trigger Abandoned Cart email
            </button>
          </div>
          <div class="col-md-8 order-md-1">
            <div class="alert text-center ml-0 not-real-warning" v-if="showCheckout == true">This storefront is not real.<br/>Your order will not be fulfilled.</div>

            <form>
              <div class="row">
                <h5 class="p-4 col-md-4 bg-light font-weight-bold">Shipping Address</h5>
                <div class="col-md-8">
                  <p class="mb-1">Joe Doe</p>
                  <p class="mb-1">2730 Sample address Ave.</p>
                  <p class="mb-1">Seattle, WA 98109</p>
                </div>
              </div>
              <hr class="mb-4">

              <div class="row">
                <h5 class="p-4 col-md-4 bg-light font-weight-bold">Payment</h5>
                <div class="col-md-8">
                  <p class="mb-1">VISA ending in 0965</p>
                  <p class="mb-1">Billing address: Same as shipping address</p>

                  <div class="input-group">
                    <input type="text" class="form-control" v-model="order.promo_code" placeholder="Promo code">
                    <div class="input-group-append">
                      <button type="submit" class="btn btn-secondary">Apply</button>
                    </div>
                  </div>
                </div>
              </div>
            </form>
          </div>
        </div>
      </div>

    </div>
  </Layout>
</template>

<script>
import {mapState} from 'vuex';

import AmplifyStore from '@/store/store'

import { RepositoryFactory } from '@/repositories/RepositoryFactory'
import { AnalyticsHandler } from '@/analytics/AnalyticsHandler'

import swal from 'sweetalert';

import Layout from '@/components/Layout/Layout'

const CartsRepository = RepositoryFactory.get('carts')
const OrdersRepository = RepositoryFactory.get('orders')

export default {
  name: 'Checkout',
  components: {
    Layout,
  },
  props: {
  },
  data () {
    return {
      errors: [],
      cart: null,
      order: null,
      showCheckout: false,
      previousPageLinkProps: {
        to: '/cart',
        text: 'Back to shopping cart'
      }
    }
  },
  async created () {
    await this.getCart()

    if (this.user) {
      this.showCheckout = true
    }

    if (this.cart) {
      AnalyticsHandler.checkoutStarted(this.user, this.cart, this.cartQuantity, this.cartSubTotal, this.cartTotal)
    }
  },
  methods: {
    async getCart (){
      if (this.cartID) {
        const { data } = await CartsRepository.getCartByID(this.cartID)
        this.cart = data
        this.order = this.cart
        this.order.total = this.cartTotal

        if (this.user) {
          this.order.email = this.user.email
          if (this.user.addresses && this.user.addresses.length > 0) {
            this.order.billing_address = this.user.addresses[0]
            this.order.shipping_address = this.user.addresses[0]
          }
        }
      }

      if (!this.order) {
        this.order = {}
        this.order.promo_code = ""
      }
    },
    signIn () {
      this.$router.push('/auth')
    },
    guestCheckout () {
      this.showCheckout = true
    },
    submitOrder () {

      OrdersRepository.createOrder(this.cart).then(response => {

        AnalyticsHandler.orderCompleted(this.user, this.cart, response.data)

        swal({
          title: "Order Submitted",
          icon: "success",
          buttons: {
            cancel: "OK",
          }
        }).then(() => {
          AmplifyStore.dispatch('getNewCart')
          this.$router.push('/');
        });
     })
    },
    async triggerAbandonedCartEmail () {
      if (this.cart && this.cart.items.length > 0 ){
        const cartItem = await this.getProductByID(this.cart.items[0].product_id)
        AnalyticsHandler.recordAbanonedCartEvent(this.user,this.cart,cartItem)
      }
      else{
        console.error("No items to export")
      }
    }
  },
  computed: {
    ...mapState({ user: state => state.user, cartID: state => state.cart.cart?.id }),
    cartSubTotal() {
      var subtotal = 0.00

      for (var item in this.cart.items) {
        var cost = this.cart.items[item].quantity * this.cart.items[item].price
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
    cartTotalBeforeTax() {
      return this.cartSubTotal + this.cartShippingRate
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

<style scoped>
  .not-real-warning {
    background: var(--blue-100);
  }

  .checkout-btn {
    border-color: var(--grey-900);
    border-width: 2px;
    font-size: 1rem;
  }

  .checkout-btn:hover,
  .checkout-btn:focus {
    background: var(--grey-900);
  }

  .abandoned-cart-btn {
    display: block;
    background: var(--blue-500);
    border-color: var(--blue-500);
    font-size: 1rem;
  }

  .abandoned-cart-btn:hover,
  .abandoned-cart-btn:focus {
    background: var(--blue-600);
    border-color: var(--blue-600);
  }
</style>
