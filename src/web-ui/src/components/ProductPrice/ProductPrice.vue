<template>
  <div>
    <span class="grey">Price:</span> <b>{{ formattedPrice }}</b>
  </div>
</template>

<script>
import { formatPrice } from '@/util/formatPrice';

export default {
  name: 'ProductPrice',
  props: {
    price: {
      type: Number,
      required: true,
    },
  },
  computed: {
    formattedPrice() {
      return formatPrice(this.price);
    },
  },
};
</script>

<style scoped>
.grey {
  color: var(--grey-600);
}
</style>