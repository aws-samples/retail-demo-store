<template>
  <Layout>
    <div class="container">
      <!-- Loading Indicator -->
      <div class="container mb-4" v-if="!product">
        <i class="fas fa-spinner fa-spin fa-3x"></i>
      </div>

      <div v-if="product" class="text-left mb-2">
        <router-link :to="`/category/${product.category}`" class="category-link">
          <i class="fa fa-chevron-left" aria-hidden></i> {{ readableProductCategory }}</router-link
        >
      </div>

      <!-- Product Detail-->
      <main v-if="product" class="product-container text-left">
        <div class="title-and-rating mb-md-3">
          <h1 class="product-name">{{ product.name }}</h1>
          <div>
            <i v-for="i in 5" :key="i" class="fas fa-star"></i>
          </div>
        </div>

        <div class="add-to-cart-and-description">
          <div class="mb-1">
            Price <b>${{ product.price }}</b>
          </div>

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
            <button class="add-to-cart-btn btn" v-on:click="addToCart()">Add to Cart</button>
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
        <small
          ><em
            ><i v-if="active_experiment" class="fa fa-balance-scale"></i
            ><i v-if="personalized" class="fa fa-user-check"></i> {{ explain_recommended }}</em
          ></small
        >
      </div>

      <div class="container related-products">
        <div class="container mb-4" v-if="!related_products.length">
          <i class="fas fa-spinner fa-spin fa-3x"></i>
        </div>
        <div class="row">
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
    </div>
  </Layout>
</template>

<script>
import AmplifyStore from '@/store/store';

import { RepositoryFactory } from '@/repositories/RepositoryFactory';
import { AnalyticsHandler } from '@/analytics/AnalyticsHandler';

const ProductsRepository = RepositoryFactory.get('products');
const CartsRepository = RepositoryFactory.get('carts');
const RecommendationsRepository = RepositoryFactory.get('recommendations');
const MaxRecommendations = 6;
const ExperimentFeature = 'product_detail_related';

import Product from './components/Product.vue';
import Layout from './components/Layout';

import { capitalize } from '@/util/capitalize';

import swal from 'sweetalert';

export default {
  name: 'ProductDetail',
  components: {
    Product,
    Layout,
  },
  data() {
    return {
      feature: ExperimentFeature,
      product: null,
      quantity: 1,
      related_products: [],
      explain_recommended: '',
      active_experiment: false,
      personalized: false,
    };
  },
  computed: {
    user() {
      return AmplifyStore.state.user;
    },
    cartID() {
      return AmplifyStore.state.cartID;
    },
    productImageUrl() {
      if (this.product.image.includes('://')) return this.product.image;

      return `${process.env.VUE_APP_IMAGE_ROOT_URL}${this.product.category}/${this.product.image}`;
    },
    readableProductCategory() {
      if (!this.product) return null;

      return capitalize(this.product.category);
    },
  },
  watch: {
    // call again the method if the route changes
    $route: 'fetchData',
  },
  created() {
    this.fetchData();
  },
  methods: {
    async addToCart() {
      if (this.cart.items === null) this.cart.items = [];

      const existingProduct = this.cart.items.find((item) => item.product_id === this.product.id);

      if (existingProduct) {
        existingProduct.quantity += this.quantity;
      } else {
        const newItem = {
          product_id: this.product.id,
          quantity: this.quantity,
          price: this.product.price,
        };

        this.cart.items.push(newItem);
      }

      await CartsRepository.updateCart(this.cart);

      await this.getCart();

      AnalyticsHandler.productAddedToCart(
        this.user,
        this.cart,
        this.product,
        existingProduct?.quantity ?? this.quantity,
        this.$route.query.feature,
        this.$route.query.exp,
      );

      this.resetQuantity();

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
    async getProductByID(product_id) {
      const { data } = await ProductsRepository.getProduct(product_id);
      this.product = data;
      this.getRelatedProducts();
    },
    async fetchData() {
      await this.getProductByID(this.$route.params.id);
      this.getCart();
      this.recordProductViewed();
    },
    recordProductViewed() {
      if (this.product) {
        AnalyticsHandler.productViewed(this.user, this.product, this.$route.query.feature, this.$route.query.exp);
      }
    },
    async getRelatedProducts() {
      const response = await RecommendationsRepository.getRelatedProducts(
        this.user?.id ?? '',
        this.product.id,
        MaxRecommendations,
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
    async getCart() {
      if (this.cartID) {
        const { data } = await CartsRepository.getCartByID(this.cartID);

        // Since cart service holds carts in memory, they can be lost on restarts.
        // Make sure our cart was returned. Otherwise create a new one.
        if (data.id === this.cartID) {
          this.cart = data;
          return;
        } else {
          console.warn(`Cart ${this.cartID} not found. Creating new cart. Was cart service restarted?`);
        }
      }

      this.createCart();
    },
    async createCart() {
      const username = this.user?.username ?? 'guest';

      const { data } = await CartsRepository.createCart(username);

      this.cart = data;

      AmplifyStore.commit('setCartID', this.cart.id);
    },
    resetQuantity() {
      this.quantity = 1;
    },
  },
};
</script>

<style scoped>
.category-link {
  color: inherit;
}

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

@media screen and (min-width: 768px) {
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
