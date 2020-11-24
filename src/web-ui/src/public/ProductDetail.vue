<template>
  <Layout :isLoading="isLoading" :previousPageLinkProps="previousPageLinkProps">
    <template #default>
      <div class="container">
        <main class="product-container mb-5 text-left">
          <div class="title-and-rating mb-md-3">
            <h1 class="product-name">{{ product.name }}</h1>
            <FiveStars></FiveStars>
          </div>

          <div class="add-to-cart-and-description">
            <ProductPrice :price="product.price" class="mb-1"></ProductPrice>

            <div class="mb-2">
              <template v-if="outOfStock">Sorry, this item is currently out of stock.</template>
              <template v-else>Items currently in stock: {{ product.current_stock }}</template>
            </div>

            <div class="mb-5 mb-md-4 d-flex">
              <button
                v-if="!outOfStock"
                class="quantity-dropdown mr-3 btn btn-outline-secondary dropdown-toggle"
                type="button"
                id="quantity-dropdown"
                data-toggle="dropdown"
                aria-haspopup="true"
                aria-expanded="false"
              >
                Qty: {{ quantity }}
              </button>
              <div class="dropdown-menu" aria-labelledby="quantity-dropdown">
                <button
                  v-for="i in Math.min(9, product.current_stock)"
                  :key="i"
                  class="dropdown-item"
                  @click="quantity = i"
                >
                  {{ i }}
                </button>
              </div>
              <button class="add-to-cart-btn btn" @click="addProductToCart" :disabled="outOfStock">Add to Cart</button>
            </div>

            <p>{{ product.description }}</p>
          </div>

          <div class="product-img">
            <img :src="productImageUrl" class="img-fluid" :alt="product.name" />
          </div>
        </main>

        <RecommendedProductsSection
          :explainRecommended="explainRecommended"
          :recommendedProducts="relatedProducts"
          :feature="feature"
        >
          <template #heading>Compare similar items</template>
        </RecommendedProductsSection>
      </div>
    </template>
  </Layout>
</template>

<script>
import swal from 'sweetalert';
import { mapState, mapActions, mapGetters } from 'vuex';

import { RepositoryFactory } from '@/repositories/RepositoryFactory';
import { AnalyticsHandler } from '@/analytics/AnalyticsHandler';

import { product } from '@/mixins/product';

import Layout from '@/components/Layout/Layout';
import ProductPrice from '@/components/ProductPrice/ProductPrice';
import FiveStars from '@/components/FiveStars/FiveStars';
import RecommendedProductsSection from '@/components/RecommendedProductsSection/RecommendedProductsSection';

const RecommendationsRepository = RepositoryFactory.get('recommendations');
const MAX_RECOMMENDATIONS = 6;
const EXPERIMENT_FEATURE = 'product_detail_related';

export default {
  name: 'ProductDetail',
  components: {
    Layout,
    ProductPrice,
    FiveStars,
    RecommendedProductsSection,
  },
  mixins: [product],
  data() {
    return {
      quantity: 1,
      feature: EXPERIMENT_FEATURE,
      relatedProducts: null,
      explainRecommended: null,
    };
  },
  computed: {
    ...mapState(['user']),
    ...mapGetters(['personalizeUserID']),
    isLoading() {
      return !this.product;
    },
    previousPageLinkProps() {
      if (!this.product) return null;

      return {
        to: `/category/${this.product.category}`,
        text: this.readableProductCategory,
      };
    },
  },
  watch: {
    $route: {
      immediate: true,
      handler() {
        this.fetchData();
      },
    },
  },
  methods: {
    ...mapActions(['addToCart']),
    resetQuantity() {
      this.quantity = 1;
    },
    async addProductToCart() {
      await this.addToCart({
        product: this.product,
        quantity: this.quantity,
        feature: this.$route.query.feature,
        exp: this.$route.query.exp,
      });

      this.renderAddedToCartConfirmation();

      this.resetQuantity();
    },
    async fetchData() {
      await this.getProductByID(this.$route.params.id);

      // reset in order to trigger recalculation in carousel - carousel UI breaks without this
      this.relatedProducts = null;
      this.getRelatedProducts();

      this.recordProductViewed(this.$route.query.feature, this.$route.query.exp);
    },
    async getRelatedProducts() {
      const response = await RecommendationsRepository.getRelatedProducts(
        this.personalizeUserID ?? '',
        this.product.id,
        MAX_RECOMMENDATIONS,
        EXPERIMENT_FEATURE,
      );

      if (response.headers) {
        const experimentName = response.headers['x-experiment-name'];
        const personalizeRecipe = response.headers['x-personalize-recipe'];

        if (experimentName || personalizeRecipe) {
          const explanation = experimentName
            ? `Active experiment: ${experimentName}`
            : `Personalize recipe: ${personalizeRecipe}`;

          this.explainRecommended = {
            activeExperiment: !!experimentName,
            personalized: !!personalizeRecipe,
            explanation,
          };
        }
      }

      this.relatedProducts = response.data;

      if (this.relatedProducts.length > 0 && 'experiment' in this.relatedProducts[0]) {
        AnalyticsHandler.identifyExperiment(this.user, this.relatedProducts[0].experiment);
      }
    },
    renderAddedToCartConfirmation() {
      swal({
        title: 'Added to Cart',
        icon: 'success',
        buttons: {
          cancel: 'Continue Shopping',
          cart: 'View Cart',
        },
      }).then((value) => {
        switch (value) {
          case 'cancel':
            break;
          case 'cart':
            this.$router.push('/cart');
        }
      });
    },
  },
};
</script>

<style scoped>
.product-container {
  display: grid;
  grid-gap: 15px;
  grid-template-columns: 1fr;
  grid-template-rows: auto;
  grid-template-areas:
    'TitleAndRating'
    'ProductImage'
    'AddToCardAndDescription';
}

@media (min-width: 768px) {
  .product-container {
    grid-template-columns: 1fr 1fr;
    grid-column-gap: 30px;
    grid-template-rows: auto;
    grid-row-gap: 00px;
    grid-template-areas:
      'ProductImage TitleAndRating'
      'ProductImage AddToCardAndDescription'
      'ProductImage .';
  }
}

.title-and-rating {
  grid-area: TitleAndRating;
}

.product-name {
  font-size: 1.5rem;
}

.add-to-cart-and-description {
  grid-area: AddToCardAndDescription;
}

.quantity-dropdown {
  border-color: var(--grey-600);
}

.quantity-dropdown:hover,
.quantity-dropdown:focus {
  background: var(--grey-900);
  border-color: var(--grey-900);
}

.add-to-cart-btn {
  background: var(--grey-600);
  color: var(--white);
}

.add-to-cart-btn:hover,
.add-to-cart-btn:focus {
  background: var(--grey-900);
}

.product-img {
  grid-area: ProductImage;
}
</style>
