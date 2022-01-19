<template>
  <Layout :isLoading="isLoading" :previousPageLinkProps="previousPageLinkProps">
    <template #default>
      <h1 style="padding-bottom:1em;" v-if="haveFavorites">Your favorites</h1>
      <h1 style="padding-bottom:1em;" v-else-if="user">You have not done any favoriting</h1>
      <h1 style="padding-bottom:1em;" v-else>You are not logged in</h1>

        <div class="container"  v-if="user && haveFavorites">
          <div class="row">

              <div
                  v-for="(favorite, index) in favorites"
                  :key="index"
                  class="col-6 col-sm-4 col-md-3 px-1 text-left align-self-stretch d-flex align-items-stretch text-decoration-none"
              >
                <Product :product="favorite" feature="favorites"></Product>
              </div>
          </div>
        </div>
    </template>
  </Layout>
</template>

<script>

import {RepositoryFactory} from "@/repositories/RepositoryFactory";
const FavoritingRepository = RepositoryFactory.get('favoriting')
const ProductsRepository = RepositoryFactory.get('products')
import Layout from "@/components/Layout/Layout";
import AmplifyStore from "@/store/store";
import Product from '@/components/Product/Product';

export default {
  name: 'Favorites',
  components: {
    Layout,
    Product
  },
  data() {
    return {
      favoriteIds: null,
      favorites: null
    }
  },
  created () {
    if (this.user) {
      FavoritingRepository.getUserFavorites(this.user.username).then(
          (result) => {this.favoriteIds = result.data.favorites.favorites;
                       //this.favoriteIds = result.data.products.map(item=>item.id);
                       if (this.favoriteIds.length > 0) {
                         ProductsRepository.getProduct(this.favoriteIds).then(
                              (result) => {this.favorites = result.data.length?result.data:[result.data]}
                          );
                       } else {
                         this.favorites = []
                       }
                      }
      )
    }
  },
  computed: {
    isLoading() {
      return !this.favorites && !!this.user;
    },
    user() {
      return AmplifyStore.state.user
    },
    previousPageLinkProps() {
      if (!this.lastVisitedPage) return null;
      return { text: 'Continue Shopping', to: this.lastVisitedPage };
    },
    haveFavorites() {
      return this.favorites && this.favorites.length > 0
    }
  },
};
</script>

<style scoped>


</style>
