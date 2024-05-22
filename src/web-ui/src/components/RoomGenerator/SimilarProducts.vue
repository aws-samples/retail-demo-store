<template>
    <div class="content">
        <div class="container" v-show="itemIds?.length>0">
            <div class="row">
                <p class="h4">Matching Products</p>
            </div>
            <div class="row">
                <div v-for="product in matchingProducts" :key="product.id" class="row">
                    <Product :product="product" :feature="`none`"/> 
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import { RepositoryFactory } from "@/repositories/RepositoryFactory";
import Product from '@/components/Product/Product.vue';
const ProductsRepository = RepositoryFactory.get('products');

const lookupItems = (component) => {
    if (component.itemIds.length > 0) {
        ProductsRepository.getProduct(component.itemIds)
            .then(({ data }) => component.matchingProducts = Array.isArray(data) ? data : [data])
    }
}

export default {
  props: {
    itemIds: Array,
  },
  components: {
    Product
  },
  name: 'SimilarItems',
  data() {
    return {
        matchingProducts: [],
        carouselSettings: {
            dots: false,
            slidesToShow: 2,
            responsive: [
                {
                    breakpoint: 480,
                    settings: { slidesToShow: 3 },
                },
                {
                    breakpoint: 768,
                    settings: { slidesToShow: 4 },
                },
            ],
        }
    }
  },
  created() {
    lookupItems(this);
  },
  watch: {
    itemIds(newVal) {
      if (newVal?.length > 0) {
        lookupItems(this);
      } else {
        this.matchingProducts = [];
      }
    }
  }
}
</script>

<style>



</style>