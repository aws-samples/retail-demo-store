<template>
  <div class="container mb-4">
    <div class="container mb-4" v-if="!categories.length">
      <i class="fas fa-spinner fa-spin fa-3x"></i>
    </div>
    <div class="row col-sm-12 col-md-12 col-lg-12 d-none d-sm-block">
      <ul class="nav nav-pills nav-fill mx-auto">
        <li class="nav-item">
          <router-link class="nav-link" :to="{name:'CategoryDetail', params: {id: 'featured'}}" v-bind:class="{ active: display == 'featured' }">Featured</router-link>
        </li>
        <li class="nav-item" v-for="category in categories" v-bind:key=category.id>
          <router-link class="nav-link" :to="{name:'CategoryDetail', params: {id: category.name}}" v-bind:class="{ active: display == category.name }">{{ category.name | capitalize }}</router-link>
        </li>
        <li class="nav-item">
          <router-link class="nav-link" :to="{name:'Live'}" v-bind:class="{ active: display == 'live' }">Live <i class="fas fa-tv"/></router-link>
        </li>
      </ul>
    </div>
    <div class="dropdown show d-block d-sm-none">
      <a class="btn dropdown-toggle btn-primary" href="#" role="button" id="dropdownMenuLink" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
        Select Category
      </a>
      <div class="dropdown-menu" aria-labelledby="dropdownMenuLink">
        <router-link class="dropdown-item" :to="{name:'CategoryDetail', params: {id: 'featured'}}" v-bind:class="{ active: display == 'featured' }">Featured</router-link>
        <router-link class="dropdown-item" v-for="category in categories" v-bind:key="`nav-${category.name}`" :to="{name:'CategoryDetail', params: {id: category.name}}" v-bind:class="{ active: display == category.name }">
          {{ category.name | capitalize }}
        </router-link>
        <router-link class="dropdown-item" :to="{name:'Live'}" v-bind:class="{ active: display == 'live' }">Live  <i class="fas fa-tv"/></router-link>
      </div>
    </div>
  </div>
</template>

<script>
import {RepositoryFactory} from "@/repositories/RepositoryFactory";

const ProductsRepository = RepositoryFactory.get('products');

export default {
  name: "Navigation",
  props: [
    'display',
    'categories'
  ],
  methods: {
    async getCategories () {
      const { data } = await ProductsRepository.getCategories();
      this.categories = data;
    }
  },
}
</script>

<style scoped>

</style>