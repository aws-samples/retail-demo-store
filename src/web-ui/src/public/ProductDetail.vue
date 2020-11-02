<template>
  <Layout :isLoading="isLoading" :previousPageLinkProps="previousPageLinkProps">
    <template #default>
      <div class="container">
        <!-- Product Detail-->
        <main class="product-container text-left">
          <div class="title-and-rating mb-md-3">
            <h1 class="product-name">{{ product.name }}</h1>
            <div>
              <i v-for="i in 5" :key="i" class="fas fa-star"></i>
            </div>
          </div>

          <div class="add-to-cart-and-description">
            <ProductPrice :price="product.price" class="mb-1"></ProductPrice>

            <div class="mb-5 mb-md-4 d-flex">
              <button
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
                <button v-for="i in 9" :key="i" class="dropdown-item" @click="quantity = i">{{ i }}</button>
              </div>
              <button class="add-to-cart-btn btn" @click="addProductToCart">Add to Cart</button>
            </div>

            <p>{{ product.description }}</p>
          </div>

          <div class="product-img">
            <img :src="productImageUrl" class="img-fluid" :alt="product.name" />
          </div>
        </main>

        <!-- Recommendations -->
        <hr />

        <h5>What other items do customers view related to this product?</h5>
        <div v-if="explain_recommended" class="text-muted text-center">
          <small>
            <em>
              <i v-if="active_experiment" class="fa fa-balance-scale"></i>
              <i v-if="personalized" class="fa fa-user-check"></i> {{ explain_recommended }}
            </em>
          </small>
        </div>

        <div class="related-products row">
          <LoadingFallback v-if="!related_products.length" class="col my-4 text-center"></LoadingFallback>

          <div class="card-deck col-sm-12 col-md-12 col-lg-12 mt-4">
            <Product
              v-for="recommendation in related_products"
              v-bind:key="recommendation.product.id"
              :product="recommendation.product"
              :experiment="recommendation.experiment"
              :feature="feature"
            />
          </div>
        </div>
      </div>
    </template>
  </Layout>
</template>

<script>
import { RepositoryFactory } from '@/repositories/RepositoryFactory';
import { AnalyticsHandler } from '@/analytics/AnalyticsHandler';

import { user } from '@/mixins/user';
import { product } from '@/mixins/product';
import { cart } from '@/mixins/cart';

const RecommendationsRepository = RepositoryFactory.get('recommendations');
const MAX_RECOMMENDATIONS = 6;
const ExperimentFeature = 'product_detail_related';

import Product from './components/Product.vue';
import Layout from '@/components/Layout/Layout';
import LoadingFallback from '@/components/LoadingFallback/LoadingFallback';
import ProductPrice from '@/components/ProductPrice/ProductPrice';

export default {
  name: 'ProductDetail',
  components: {
    Layout,
    LoadingFallback,
    Product,
    ProductPrice,
  },
  mixins: [user, product, cart],
  data() {
    return {
      quantity: 1,
      feature: ExperimentFeature,
      related_products: [],
      explain_recommended: '',
      active_experiment: false,
      personalized: false,
    };
  },
  computed: {
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
    // call again the method if the route changes
    $route: {
      immediate: true,
      handler() {
        this.fetchData();
      },
    },
  },
  methods: {
    resetQuantity() {
      this.quantity = 1;
    },
    async addProductToCart() {
      await this.addToCart(this.product, this.quantity, this.$route.query.feature, this.$route.query.exp);
      this.resetQuantity();
    },
    async fetchData() {
      await this.getProductByID(this.$route.params.id);
      this.getRelatedProducts();
      this.getCart();
      this.recordProductViewed(this.$route.query.feature, this.$route.query.exp);
    },
    async getRelatedProducts() {
      const response = await RecommendationsRepository.getRelatedProducts(
        this.user?.id ?? '',
        this.product.id,
        MAX_RECOMMENDATIONS,
        ExperimentFeature,
      );

      if (response.headers) {
        if (response.headers['x-personalize-recipe']) {
          this.personalized = true;
          this.explain_recommended = `Personalize recipe: ${response.headers['x-personalize-recipe']}`;
        }
        if (response.headers['x-experiment-name']) {
          this.active_experiment = true;
          this.explain_recommended = `Active experiment: ${response.headers['x-experiment-name']}`;
        }
      }

      this.related_products = response.data;

      if (this.related_products.length > 0 && 'experiment' in this.related_products[0]) {
        AnalyticsHandler.identifyExperiment(this.user, this.related_products[0].experiment);
      }
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

.fa-star {
  color: var(--amazon-orange);
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
