<template>
  <li role="presentation" v-if="product">
    <img :src="productImageURL" class="ml-2 search-item-img" :alt="product.name">
    <router-link class="btn btn-link mt-auto" :to="{name:'ProductDetail', params: {id: product.id}}">{{ product.name }}</router-link>  
  </li>
</template>

<script>
import { RepositoryFactory } from '@/repositories/RepositoryFactory'

const ProductsRepository = RepositoryFactory.get('products')

export default {
  name: 'SearchItem',
  components: {
  },
  props: {
      product_id: null,
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
    async getProductByID (product_id){
      const { data } = await ProductsRepository.getProduct(product_id)
      this.product = data
      console.log(this.product)
    },
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

  .search-item-img {
    max-width: 40px;
  }
  
</style>