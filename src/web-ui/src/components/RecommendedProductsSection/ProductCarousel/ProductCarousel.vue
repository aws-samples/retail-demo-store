<template>
  <div>
    <Carousel v-if="showCarousel" :settings="carouselSettings">
      <div
          v-for="item in recommendedProducts"
          :key="item.product.id"
          class="px-1 text-left align-self-stretch d-flex align-items-stretch text-decoration-none"
      >
        <Product :product="item.product" :experiment="item.experiment" :feature="feature"
                 @click="onProductClick"></Product>
      </div>
    </Carousel>
    <div v-else class="container">
      <div class="row">
        <div
            v-for="item in recommendedProducts"
            :key="item.product.id"
            class="col-3 px-1 text-left align-self-stretch d-flex align-items-stretch text-decoration-none"
        >
          <Product :product="item.product" :experiment="item.experiment" :feature="feature"
                   @click="onProductClick"></Product>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import Carousel from '@/components/Carousel/Carousel';
import Product from '@/components/Product/Product';

export default {
  name: 'ProductCarousel',
  components: {
    Carousel,
    Product,
  },
  props: {
    recommendedProducts: {
      type: Array,
      required: true,
    },
    feature: {
      type: String,
      required: false,
    },
  },
  data() {
    return {
      carouselSettings: {
        dots: false,
        slidesToShow: 2,
        responsive: [
          {
            breakpoint: 480,
            settings: {slidesToShow: 3},
          },
          {
            breakpoint: 768,
            settings: {slidesToShow: 4},
          },
        ],
      },
      windowWidth: window.innerWidth
    };
  },
  mounted() {
    this.$nextTick(() => {
      window.addEventListener('resize', this.onResize);
    })
  },
  methods: {
    onProductClick(e, product) {
      this.$emit('productClick', e, product)
    },
    onResize() {
      this.windowWidth = window.innerWidth
    }
  },
  computed: {
    showCarousel() {
      if (this.windowWidth > 768) {
        return this.recommendedProducts.length > 3
      } else if (this.windowWidth > 480) {
        return this.recommendedProducts.length > 2
      } else {
        return this.recommendedProducts.length > 1
      }
    }
  }
};
</script>
