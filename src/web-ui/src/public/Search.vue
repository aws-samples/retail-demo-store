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
                <li class="presentation text-center text-secondary" v-if="searching"><i class="fas fa-spinner fa-spin fa-lg"></i></li>
                <li class="presentation text-center text-secondary" v-if="!results"> No Results </li>
                <li class="presentation text-center text-secondary" v-if="results && results.length < 1"> No Results </li>
                <li class="presentation text-center text-secondary" v-if="reranked"><small><i class="fa fa-user-check"></i> <em>Personalized Ranking</em></small></li>
                <SearchItem v-for="result in results" 
                  v-bind:key="result.itemId"
                  :product_id="result.itemId"
                  :experiment="result.experiment"
                  :feature="feature"
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
const RecommendationsRepository = RepositoryFactory.get('recommendations')

const ExperimentFeature = 'search_results'

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
      feature: ExperimentFeature,
      errors: [],
      results: [],
      searching: false,
      reranked: false,
      searchTerm: ''
    }
  },
  methods: {
    async search(val) {
      const { data } = await SearchRepository.searchProducts(val)
      this.rerank(data)

      AnalyticsHandler.productSearched(this.user, val.toString(), data.length)
    },
    clearSearchTerm() {
      this.searchTerm = "";
      this.reranked = false
    },
    async rerank(items) {
      if (this.user && items.length > 0) {
        const { data } = await RecommendationsRepository.getRerankedItems(this.user.id, items, ExperimentFeature)
        this.reranked = JSON.stringify(items) != JSON.stringify(data)
        this.results = data
      }
      else {
        this.reranked = false
        this.results = items
      }
    }
  },
  computed: {
    user() { 
      return AmplifyStore.state.user
    }
  },
  watch: {
    searchTerm: function (val) {
      if (val.length > 0) {
        this.searching = true
        try {
          this.search(val)
        }
        finally {
          this.searching = false
        }
      } else {
        this.searching = false
        this.results = []
        this.reranked = false
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