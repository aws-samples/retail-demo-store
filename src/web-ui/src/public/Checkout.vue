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
          <div class="col-lg-auto order-lg-2 summary-column">
            <div class="summary-border-container card p-1">
              <div class="card-body">
                <h4 class="d-flex justify-content-between align-items-center mb-3 card-title text-muted">
                  Order Summary
                </h4>
                <div class="p-1 mb-1 d-flex justify-content-between">
                  <span>{{ cartQuantity }} item{{ cartQuantity === 1 ? '' : 's' }} in cart</span>
                  <strong>{{ formattedCartTotal }}</strong>
                </div>
                <button class="checkout-btn btn btn-outline-dark btn-block btn-lg btn-block" :disabled="!placeOrderEnabled" v-on:click="handleSubmitOrderButton">Place your order</button>
                <div class="mt-3">
                  <amazon-pay-button v-if="placeOrderEnabled && amazonPayEnabled" @click="finalizeAmazonPayOrder"/>
                </div>
              </div>
            </div>

            <div class="m-4">
              <AbandonCartButton class="abandon-cart"></AbandonCartButton>
            </div>

          </div>
          <div class="col order-lg-1">
            <div class="alert text-center ml-0 not-real-warning" v-if="showCheckout == true">This storefront is not real.<br/>Your order will not be fulfilled.</div>

            <form>

              <div class="d-flex">
                <h5 class="p-4 col-lg-4 bg-light font-weight-bold d-flex align-items-center">Delivery Method</h5>
                <div class="col-lg-8">
                  <p class="form-check mt-2 mb-0">
                    <input class="form-check-input" type="radio" name="collectionOptions" id="collectionOption2" :value="false" v-model="collection">
                    <label class="form-check-label" for="collectionOption2">Delivery</label>
                  </p>
                  <p class="form-check mt-0">
                    <input class="form-check-input" type="radio" name="collectionOptions" id="collectionOption1" :value="true" v-model="collection">
                    <label class="form-check-label" for="collectionOption1">Pickup at Store</label>
                  </p>
                  <div v-if="collection">
                    <input
                      v-maska data-maska="['+# (###) ### - ####', '+## (###) ### - ####']"
                      name="collectionPhone"
                      placeholder="Your phone number so we can contact you about your order"
                      id="collectionPhone"
                      v-model="collectionPhone"
                      type="tel"
                      class="input py-1 px-2 mb-2"
                    />
                    <div class="consent d-flex align-items-start text-left">
                      <input type="checkbox" class="consent-checkbox mr-2" id="order-alerts-consent" v-model="hasConsentedPhone" />
                      <label class="" for="order-alerts-consent">
                        I consent to receive automated text messages at my mobile number above to inform me about the
                        status of my order. For in-store collection, consent is a conditon of purchase.</label>
                    </div>
                  </div>
                </div>
              </div>

              <div class="d-flex">
                <h5 class="p-4 col-lg-4 bg-light font-weight-bold d-flex align-items-center">
                  <span v-if="!collection">Shipping Address</span>
                  <span v-if="collection">Billing Address</span>
                </h5>
                <div class="col-lg-8">
                  <p class="mb-1 font-weight-bold">{{order.shipping_address.first_name}} {{order.shipping_address.last_name}}</p>
                  <p class="mb-1">{{order.shipping_address.address1}}</p>
                  <p class="mb-1" v-if="order.shipping_address.address2">{{order.shipping_address.address2}}</p>
                  <p class="mb-1">{{order.shipping_address.city}}, {{order.shipping_address.state}} {{order.shipping_address.zipcode}}</p>
                </div>
              </div>

              <div class="fenix-estimates">
                <FenixCheckout
                v-if="fenixenableCHECKOUT == 'TRUE'"
                :lineItems="cart">
                </FenixCheckout>
              </div>

              <hr class="mb-4">

              <div class="d-flex">
                <h5 class="p-4 col-lg-4 bg-light font-weight-bold d-flex align-items-center">Payment</h5>
                <div class="col-lg-8">
                  <p class="mb-1">VISA ending in 0965</p>
                  <p class="mb-1" v-if="!collection">Billing address: Same as shipping address</p>

                  <div class="input-group">
                    <input type="text" class="form-control" v-model="order.promo_code" placeholder="Promo code">
                    <div class="input-group-append">
                      <button type="button" class="btn btn-secondary" @click="promoApplied">Apply</button>
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
import {mapGetters, mapState} from 'vuex';

import AmplifyStore from '@/store/store'

import { RepositoryFactory } from '@/repositories/RepositoryFactory'
import { AnalyticsHandler } from '@/analytics/AnalyticsHandler'


import swal from 'sweetalert';

import Layout from '@/components/Layout/Layout.vue'
import AbandonCartButton from '@/partials/AbandonCartButton/AbandonCartButton.vue'
import AmazonPayButton from "@/public/components/AmazonPayButton.vue";
import { vMaska } from "maska"
import FenixCheckout from '@/components/Fenix/FenixCheckout.vue';

const CartsRepository = RepositoryFactory.get('carts')
const OrdersRepository = RepositoryFactory.get('orders')

export default {
  name: 'Checkout',
  components: {
    Layout,
    AbandonCartButton,
    AmazonPayButton,
    FenixCheckout
  },
  directives: { maska: vMaska },
  data () {
    return {
      errors: [],
      cart: null,
      order: null,
      showCheckout: false,
      collectionPhone: '',
      previousPageLinkProps: {
        to: '/cart',
        text: 'Back to shopping cart'
      },
      collection: false,
      hasConsentedPhone: false,
      fenixenableCHECKOUT: import.meta.env.VITE_FENIX_ENABLED_CHECKOUT,
    }
  },
  async created () {
    await this.getCart()

    if (this.user) {
      this.showCheckout = true
    }

    if (this.cart) {
      AnalyticsHandler.checkoutStarted(this.user, this.cart, this.cartQuantity, this.cartTotal)
    }
  },
  methods: {
    async getCart (){
      if (this.cartID) {
        console.log('Ready for checkout - getting card fresh from server - ID: ' + this.cartID.toString())
        const { data } = await CartsRepository.getCartByID(this.cartID)
        this.cart = data
        this.order = this.cart
        this.order.total = this.cartTotal
        this.order.collection_phone = ''

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

      if (!this.order.billing_address) {
        this.order.billing_address = this.order.shipping_address = {
          first_name: 'Joe',
          last_name: 'Doe',
          email: this.user && this.user.email || 'joe.doe@example.com',
          address1: '2730 Sample address Ave.',
          address2: '',
          city: 'Seattle',
          state: 'WA',
          zipcode: '98109'
        }
      }
    },
    promoApplied() {
      swal({
          title: "Promo Applied",
          icon: "success",
          buttons: {
            cancel: "OK",
          }
        })
    },
    signIn () {
      this.$router.push('/auth')
    },
    guestCheckout () {
      this.showCheckout = true
    },
    finalizeAmazonPayOrder () {
      // As the Amazon Pay integration is truncated, we finalize the checkout here.
      this.submitOrder( () => {})
    },
    handleSubmitOrderButton () {
      this.submitOrder( () => {
        swal({
          title: "Order Submitted",
          icon: "success",
          buttons: {
            cancel: "OK",
          }
        }).then(() => {
          this.$router.push('/')
        });
      })
    },
    submitOrder (callback) {

      if (this.collection) {
        this.order.shipping_address = {}
        this.order.delivery_type = 'COLLECTION'
        // we tack the + back on the phone number - we mask out non-numeric characters in our input
        // but Pinpoint expects it.
        this.order.collection_phone = '+' + this.collectionPhone
      } else {
        this.order.delivery_type = 'DELIVERY'
      }
      console.log(this.order)
      OrdersRepository.createOrder(this.cart).then(response => {

      AnalyticsHandler.orderCompleted(this.user, this.cart, response.data)
      AmplifyStore.dispatch('getNewCart')
      callback()

     })
    },
  },
  computed: {
    ...mapState({ user: state => state.user, cartID: state => state.cart.cart?.id }),
    ...mapGetters([ 'cartQuantity', 'cartTotal', 'formattedCartTotal' ]),
    placeOrderEnabled() {
      return !this.collection || this.hasConsentedPhone
    },
    amazonPayEnabled() {
      const enabled = import.meta.env.VITE_AMAZON_PAY_PUBLIC_KEY_ID && import.meta.env.VITE_AMAZON_PAY_PUBLIC_KEY_ID !== '' &&
                      import.meta.env.VITE_AMAZON_PAY_STORE_ID && import.meta.env.VITE_AMAZON_PAY_STORE_ID !== '' &&
                      import.meta.env.VITE_AMAZON_PAY_MERCHANT_ID && import.meta.env.VITE_AMAZON_PAY_MERCHANT_ID !== ''
      if(enabled) {
        console.log('Amazon Pay Button Enabled')
      }
      return enabled;
    }
  }
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


  .summary-column {
    min-width: 20em;
  }

  .summary-border-container {
    border-color: var(--grey-300);
  }

  .consent {
    font-size: 0.85rem;
  }

  .consent-checkbox {
    /* fine-tuning for alignment */
    margin-top: 4px;
  }

  @media (min-width: 768px) {
    .checkout-btn {
      font-size: 1.25rem;
    }    
  }

  @media (min-width: 992px) {
    .abandon-cart {
      max-width: 400px;
    }
  }
</style>
