<template>
  <div class="search">

    <!-- Search -->
    <div class="nav">
        <form class="form-inline d-flex dropdown ml-auto mr-4" autocomplete="off">
            <div class="input-group">
              <input class="form-control" type="text" placeholder="Search" id="search" data-toggle="dropdown" v-model="searchTerm">
              <button class="btn bg-transparent text-secondary" style="margin-left: -40px; z-index: 100;" v-on:click="clearSearchTerm">
                <i class="fa fa-times"></i>
              </button>
              <ul class="search-results dropdown-menu dropdown-menu-right" role="menu" aria-labelledby="search">
                <li class="presentation text-center text-secondary" v-if="!results"> No Results </li>
                <li class="presentation text-center text-secondary" v-if="results && results.length < 1"> No Results </li>
                <SearchItem v-for="result in results" 
                  v-bind:key="result.itemId"
                  :product_id="result.itemId"
                />            
              </ul>
            </div>
        </form>
    </div> 
    <hr/>
  </div>
</template>

<script>
import AmplifyStore from '@/store/store'
import { RepositoryFactory } from '@/repositories/RepositoryFactory'
import { AnalyticsHandler } from '@/analytics/AnalyticsHandler'

const SearchRepository = RepositoryFactory.get('search')

import SearchItem from './components/SearchItem.vue'

export default {
  name: 'Search',
  components: {
    SearchItem
  },
  props: {
  },
  data () {
   return {  
      errors: [],
      results: [],
      searchTerm: ''
    }
  },
  methods: {
    async search(val) {
      const { data } = await SearchRepository.searchProducts(val)
      this.results = data

      AnalyticsHandler.productSearched(this.user, val.toString(), data.length)
    },
    clearSearchTerm() {
      this.searchTerm = "";
    }
  },
  computed: {
    user() { 
      return AmplifyStore.state.user
    },
    userID() { 
      return AmplifyStore.state.userID
    }
  },
  watch: {
    searchTerm: function (val) {
      if (val.length > 0) {
        this.search(val)
      } else {
        this.results = []
      }
    },
  }
}
</script>

<style scoped>
  .search-results {
    min-width: 300px;
    width: 300px;
  }
</style>