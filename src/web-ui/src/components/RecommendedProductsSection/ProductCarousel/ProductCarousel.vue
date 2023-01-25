<template>
  <Carousel :settings="carouselSettings">
    <div
      v-for="item in recommendedProducts"
      :key="item.product.id"
      class="px-1 text-left align-self-stretch d-flex align-items-stretch text-decoration-none"
    >
      <Product :product="item.product" :experiment="item.experiment" :promotionName="item.promotionName" :feature="feature"></Product>
    </div>
  </Carousel>
</template>

<script>
import Carousel from '@/components/Carousel/Carousel.vue';
import Product from '@/components/Product/Product.vue';

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
            settings: { slidesToShow: 3 },
          },
          {
            breakpoint: 768,
            settings: { slidesToShow: 4 },
          },
        ],
      },
    };
  },
};
</script>
