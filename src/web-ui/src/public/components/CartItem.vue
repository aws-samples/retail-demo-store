<template>
  <li>
    <LoadingFallback v-if="isLoading"></LoadingFallback>

    <div class="row" v-if="!isLoading">
      <div class="col-sm-4 mb-2 mb-sm-0"><img :src="productImageUrl" alt="" class="img-fluid" /></div>

      <div class="col d-flex flex-column justify-content-between">
        <div class="product-name font-weight-bold">{{ product.name }}</div>

        <div class="d-flex d-sm-block justify-content-between align-items-center">
          <ProductPrice :price="product.price" class="product-price"></ProductPrice>

          <div class="d-flex align-items-center">
            <button @click="decreaseQuantity" aria-label="decrease quantity" class="btn text-black-50">
              <i class="fas fa-minus"></i>
            </button>
            <div class="quantity text-center font-weight-bold" :aria-label="`quantity is ${quantity}`">
              {{ quantity }}
            </div>
            <button @click="increaseQuantity" aria-label="increase quantity" class="btn text-black-50">
              <i class="fas fa-plus"></i>
            </button>

            <button class="delete-btn btn" @click="removeFromCart">
              Delete
            </button>
          </div>
        </div>
      </div>
    </div>
  </li>
</template>

<script>
import { product } from '@/mixins/product';
import LoadingFallback from '@/components/LoadingFallback/LoadingFallback';
import ProductPrice from '@/components/ProductPrice/ProductPrice';

export default {
  name: 'CartItem',
  components: {
    LoadingFallback,
    ProductPrice,
  },
  mixins: [product],
  props: {
    product_id: {
      type: String,
      required: true,
    },
    quantity: {
      type: Number,
      required: true,
    },
  },
  created() {
    this.getProductByID(this.product_id);
  },
  methods: {
    removeFromCart() {
      this.$emit('removeFromCart', this.product_id);
    },
    increaseQuantity() {
      this.$emit('increaseQuantity', this.product_id);
    },
    decreaseQuantity() {
      this.$emit('decreaseQuantity', this.product_id);
    },
  },
  computed: {
    isLoading() {
      return !this.product;
    },
  },
};
</script>

<style scoped>
.product-name {
  font-size: 1.2rem;
}

.quantity {
  min-width: 30px;
}

.delete-btn {
  color: var(--grey-600);
}

@media (min-width: 576px) {
  .product-name {
    font-size: 1.35rem;
  }

  .product-price {
    font-size: 1.2rem;
  }

  .quantity {
    min-width: 50px;
  }

  .delete-btn {
    font-size: 1.2rem;
  }
}
</style>
