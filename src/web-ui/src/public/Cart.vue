<template>
  <Layout :isLoading="isLoading">
    <template #default>
      <div class="container text-left">
        <div class="row">
          <div class="col">
            <div class="row">
              <div class="col mb-3 mb-sm-5">
                <div class="quantity-readout p-3 font-weight-bold">{{ cartQuantityReadout }}</div>
              </div>
            </div>

            <ul class="cart-items">
              <CartItem
                v-for="item in cart.items"
                :key="item.product_id"
                :product_id="item.product_id"
                :quantity="item.quantity"
                :cartPrice="item.price"
                class="mb-4"
              ></CartItem>
            </ul>
          </div>
          <div v-if="cart.items.length > 0" class="summary-container col-lg-auto">
            <div class="summary p-4">
              <div class="summary-quantity">{{ summaryQuantityReadout }}</div>
              <div class="summary-total mb-2 font-weight-bold">Your Total: {{ formattedCartTotal }}</div>
              <router-link to="/checkout" class="checkout-btn mb-3 btn btn-outline-dark btn-block btn-lg"
                >Checkout</router-link
              >
              <AbandonCartButton></AbandonCartButton>
            </div>
          </div>
        </div>
      </div>
    </template>
  </Layout>
</template>

<script>
import { mapState, mapGetters } from 'vuex';

import { AnalyticsHandler } from '@/analytics/AnalyticsHandler';

import CartItem from './components/CartItem.vue';
import Layout from '@/components/Layout/Layout';

import AbandonCartButton from '@/partials/AbandonCartButton/AbandonCartButton';

export default {
  name: 'Cart',
  components: {
    Layout,
    CartItem,
    AbandonCartButton,
  },
  created() {
    AnalyticsHandler.cartViewed(this.user, this.cart, this.cartQuantity, this.cartTotal);
  },
  computed: {
    ...mapState({ cart: (state) => state.cart.cart, user: (state) => state.user }),
    ...mapGetters(['cartQuantity', 'cartTotal', 'formattedCartTotal']),
    isLoading() {
      return !this.cart;
    },
    cartQuantityReadout() {
      if (this.cartQuantity === null) return null;

      return `(${this.cartQuantity}) ${this.cartQuantity === 1 ? 'item' : 'items'} in your cart shopping cart`;
    },
    summaryQuantityReadout() {
      if (this.cartQuantity === null) return null;

      return `Summary (${this.cartQuantity}) ${this.cartQuantity === 1 ? 'item' : 'items'}`;
    },
  },
};
</script>

<style scoped>
.quantity-readout {
  border-radius: 4px;
  background: var(--grey-200);
  font-size: 1.15rem;
}

.cart-items {
  list-style-type: none;
  padding: 0;
}

.summary {
  border: 1px solid var(--grey-600);
  border-radius: 2px;
}

.summary-total {
  font-size: 1.15rem;
}

.summary-quantity {
  font-size: 1.15rem;
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

@media (min-width: 768px) {
  .quantity-readout {
    font-size: 1.75rem;
  }

  .summary-total {
    font-size: 1.5rem;
  }

  .summary-quantity {
    font-size: 1.5rem;
  }

  .checkout-btn {
    font-size: 1.25rem;
  }
}

@media (min-width: 992px) {
  .summary-container {
    min-width: 350px;
  }

  .summary {
    position: sticky;
    top: 120px;
  }
}
</style>
