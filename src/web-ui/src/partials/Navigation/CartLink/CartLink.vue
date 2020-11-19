<template>
  <router-link to="/cart" aria-label="cart" class="cart d-flex flex-column align-items-center">
    <div class="quantity" ref="quantity">{{ cartQuantity }}</div>
    <CartIcon class="icon"></CartIcon>
  </router-link>
</template>

<script>
import { mapGetters } from 'vuex';
import CartIcon from './CartIcon';

export default {
  name: 'CartLink',
  components: { CartIcon },
  computed: {
    ...mapGetters(['cartQuantity']),
  },
  mounted() {
    this.updateQuantityDimensions();
  },
  watch: {
    cartQuantity() {
      this.updateQuantityDimensions();
    },
  },
  methods: {
    updateQuantityDimensions() {
      const quantityElem = this.$refs.quantity;
      const { offsetWidth, offsetHeight } = quantityElem;

      if (offsetWidth > offsetHeight) {
        quantityElem.style.height = `${offsetWidth}px`;
      } else {
        quantityElem.style.width = `${offsetHeight}px`;
      }
    },
  },
};
</script>

<style scoped>
.cart {
  width: 40px;
}

.icon {
  transition: fill 150ms ease-in-out;
}

.cart:hover .icon,
.cart:focus .icon {
  fill: var(--blue-600);
}

.quantity {
  /* fine tuning the position so it looks like one icon */
  position: relative;
  top: 8px;
  left: 2px;

  padding: 6px;
  display: grid;
  place-items: center;
  border-radius: 50%;
  background: var(--grey-600);
  font-size: 0.78rem;
  color: var(--white);
  transition: background 150ms ease-in-out;
}

.cart:hover .quantity,
.cart:focus .quantity {
  background: var(--blue-600);
}
</style>
