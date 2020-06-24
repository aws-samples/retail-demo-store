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

    <div class="container" v-if="showCheckout == false">
      <div class="row justify-content-center">
        <div class="card p-4" style="width: 15rem">
          <button class="btn btn-success mb-3" v-on:click="signIn">Login to Checkout</button>  
          <button class="btn btn-light" v-on:click="guestCheckout">Checkout as Guest</button>
        </div>
      </div>
    </div>

    <div class="container" v-if="cart">
      <div class="row justify-content-center" v-if="showCheckout == true">
        <div class="alert alert-secondary">This storefront is not real. Please do not enter actual billing information. Your order will not be fulfilled.</div>
      </div>
      <div class="row text-left" v-if="showCheckout == true">
        <div class="col-md-4 order-md-2 mb-4">
          <h4 class="d-flex justify-content-between align-items-center mb-3">
            <span class="text-muted">Summary</span>
            <span class="badge badge-secondary badge-pill">{{ this.cartQuantity }}</span>
          </h4>
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
          <form class="card p-2">
            <div class="input-group">
              <input type="text" class="form-control" v-model="order.promo_code" placeholder="Promo code">
              <div class="input-group-append">
                <button type="submit" class="btn btn-secondary">Redeem</button>
              </div>
            </div>
          </form>
        </div>
        <div class="col-md-8 order-md-1">
          <h4 class="d-flex justify-content-between align-items-center mb-3">
            <span class="text-muted">Details</span>
          </h4>          
          <hr/>
          <h5 class="mb-3">Billing Address</h5>
          <form>
            <div class="row">
              <div class="col-md-6 mb-3">
                <label for="firstName">First name</label>
                <input type="text" class="form-control" id="firstName" v-model="order.billing_address.first_name" placeholder="" value="" required>
              </div>
              <div class="col-md-6 mb-3">
                <label for="lastName">Last name</label>
                <input type="text" class="form-control" id="lastName" v-model="order.billing_address.last_name" placeholder="" value="" required>
              </div>
            </div>

            <div class="mb-3">
              <label for="email">Email <span class="text-muted">(Optional)</span></label>
              <input type="email" class="form-control" id="email" v-model="order.email" placeholder="you@example.com">
            </div>

            <div class="mb-3">
              <label for="address">Address</label>
              <input type="text" class="form-control" id="address" v-model="order.billing_address.address1" placeholder="1234 Main St" required>
            </div>

            <div class="mb-3">
              <label for="address2">Address 2 <span class="text-muted">(Optional)</span></label>
              <input type="text" class="form-control" id="address2" v-model="order.billing_address.address2" placeholder="Apartment or suite">
            </div>

            <div class="row">
              <div class="col-md-5 mb-3">
                <label for="country">Country</label>
                <select class="custom-select d-block w-100" id="country" v-model="order.billing_address.country" required>
                  <option value="">Choose...</option>
                  <option value="US">United States</option>
                </select>
              </div>
              <div class="col-md-4 mb-3">
                <label for="state">State</label>
                <select class="custom-select d-block w-100" id="state" v-model="order.billing_address.state" required>
                  <option value="">Choose...</option>
                  <option value="CA">California</option>
                </select>
              </div>
              <div class="col-md-3 mb-3">
                <label for="zip">Zip</label>
                <input type="text" class="form-control" id="zip" v-model="order.billing_address.zipcode" placeholder="" required>
                <div class="invalid-feedback">
                  Zip code required.
                </div>
              </div>
            </div>
            <hr class="mb-4">
            <div class="custom-control custom-checkbox">
              <input type="checkbox" class="custom-control-input" id="same-address">
              <label class="custom-control-label" for="same-address">Shipping address is the same as my billing address</label>
            </div>
            <div class="custom-control custom-checkbox">
              <input type="checkbox" class="custom-control-input" id="save-info">
              <label class="custom-control-label" for="save-info">Save this information for next time</label>
            </div>
            <hr class="mb-4">

            <h5 class="mb-3">Payment</h5>

            <div class="row">
              <div class="col-md-6 mb-3">
                <label for="cc-name">Name on card</label>
                <input type="text" class="form-control" id="cc-name" placeholder="" required>
                <small class="text-muted">Full name as displayed on card</small>
              </div>
              <div class="col-md-6 mb-3">
                <label for="cc-number">Credit card number</label>
                <input type="text" class="form-control" id="cc-number" placeholder="" required>
              </div>
            </div>
            <div class="row">
              <div class="col-md-3 mb-3">
                <label for="cc-expiration">Expiration</label>
                <input type="text" class="form-control" id="cc-expiration" placeholder="" required>
              </div>
              <div class="col-md-3 mb-3">
                <label for="cc-expiration">CVV</label>
                <input type="text" class="form-control" id="cc-cvv" placeholder="" required>
              </div>
            </div>
            <hr class="mb-4">
            <button class="btn btn-primary btn-lg btn-block" v-on:click="submitOrder">Confirm Order</button>
          </form>
        </div>
      </div>
    </div>
    
  </div>
</template>

<script>
import AmplifyStore from '@/store/store'

import { RepositoryFactory } from '@/repositories/RepositoryFactory'
import { AnalyticsHandler } from '@/analytics/AnalyticsHandler'

import swal from 'sweetalert';

const CartsRepository = RepositoryFactory.get('carts')
const OrdersRepository = RepositoryFactory.get('orders')

export default {
  name: 'Checkout',
  components: {
  },
  props: {
  },
  data () {
    return {  
      errors: [],
      cart: null,
      order: null,
      showCheckout: false
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

      if (!Object.prototype.hasOwnProperty.call(this.order, 'billing_address')) {
        this.order.billing_address = {}
        this.order.billing_address.first_name = ""
        this.order.billing_address.last_name = ""
        this.order.billing_address.email = ""
        this.order.billing_address.address1 = ""
        this.order.billing_address.address2 = ""
        this.order.billing_address.city = ""
        this.order.billing_address.state = ""
        this.order.billing_address.zipcode = ""
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
        // eslint-disable-next-line no-unused-vars
        }).then((value) => {
          AmplifyStore.commit('setCartID', null)
          // Add Delete Cart From Service Below

          // End
          this.$router.push('/');
        });
     })
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
</style>