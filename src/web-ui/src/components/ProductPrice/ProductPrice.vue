<template>
  <div >
    <span class="grey">Price:</span> <b v-bind:class="{discounted: discount}">{{ formattedPrice }}</b> <b v-if="discount">{{ discountedPrice }}</b>
  </div>
</template>

<script>
import { discountProductPrice } from '@/util/discountProductPrice';
import { formatPrice } from '@/util/formatPrice';

export default {
  name: 'ProductPrice',
  props: {
    price: {
      type: Number,
      required: true,
    },
    discount: {
      type: Boolean,
      required: false,
      default: false
    }
  },
  computed: {
    formattedPrice() {
      return formatPrice(this.price);
    },
    discountedPrice() {
      return formatPrice(discountProductPrice(this.price))
    }
  },
};
</script>

<style scoped>
.grey {
  color: var(--grey-600);
}

.discounted {
  text-decoration: line-through;
  color: red;
}
</style>