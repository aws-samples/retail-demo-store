<template>
    <tr v-if="product">
        <td class="pl-0 pr-1 d-none d-sm-table-cell">
             <img :src="productImageURL" class="cart-item-img" :alt="product.name">
        </td>
        <td class="px-1">
            {{ product.name }}
        </td>
        <td class="px-1">
            <i class="fas fa-plus text-black-50" v-on:click="increaseQuantity(product_id)"></i> <div class="mr-1 ml-1 font-weight-bold"> {{ quantity }} </div> <i class="fas fa-minus text-black-50" v-on:click="decreaseQuantity(product_id)"></i>
        </td>
        <td class="px-1">
            ${{ product.price }}
        </td>
        <td class="pr-0 pl-1">
          <a href="#" v-on:click="removeFromCart(product_id)"><i class="fas fa-times text-muted"></i></a>
        </td>
    </tr>
</template>

<script>
import AmplifyStore from '@/store/store'

import { RepositoryFactory } from '@/repositories/RepositoryFactory'

const ProductsRepository = RepositoryFactory.get('products')

export default {
  name: 'CartItem',
  components: {
  },
  props: {
      product_id: null,
      quantity: {
        type: Number,
        default: 0
      }
  },
  data () {
    return {  
      errors: [],
      product: null
    }
  },
  created () {
    this.getProductByID(this.product_id)
  },
  methods: {
    user() { 
      return AmplifyStore.state.user
    },
    async getProductByID (product_id){
      const { data } = await ProductsRepository.getProduct(product_id)
      this.product = data
    },
    removeFromCart (value) {
      this.$emit('removeFromCart', value)
    },
    increaseQuantity (value) {
      this.$emit('increaseQuantity', value)
    },
    decreaseQuantity (value) {
      this.$emit('decreaseQuantity', value)
    }
  },
  computed: {
    productImageURL: function () {
      if (this.product.image.includes('://')) {
        return this.product.image
      }
      else {
        let root_url = process.env.VUE_APP_IMAGE_ROOT_URL
        return root_url + this.product.category + '/' + this.product.image
      }
    }
  }
}
</script>

<style scoped>
.cart-item-img {
    max-height: 50px;
}
</style>