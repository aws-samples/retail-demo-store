<template>
  <div class="d-inline-flex dropdown">
    <i :class="{ 'fa fa-search': true, 'fa-search--focused': inputFocused }" aria-hidden></i>
    <input
      type="text"
      autocomplete="off"
      data-toggle="dropdown"
      aria-haspopup="true"
      aria-expanded="false"
      id="search"
      class="input py-2"
      v-model="searchTerm"
      @focus="onInputFocus"
      @blur="onInputBlur"
    />
    <ul v-show="searchTerm !== ''" class="search-results dropdown-menu" role="menu" aria-labelledby="search">
      <li v-if="isSearching" class="text-center">
        <LoadingFallback small></LoadingFallback>
      </li>

      <li class="text-center text-secondary" v-if="results && results.length === 0">No Results</li>

      <li class="text-center text-secondary" v-if="isReranked">
        <small><i class="fa fa-user-check"></i> <em>Personalized Ranking</em></small>
      </li>

      <SearchItem
        v-for="result in results"
        :key="result.itemId"
        :product="result.product"
        :experiment="result.experiment"
        :feature="feature"
      />
    </ul>
  </div>
</template>

<script>
import { mapState, mapGetters } from 'vuex';

import { RepositoryFactory } from '@/repositories/RepositoryFactory';
import { AnalyticsHandler } from '@/analytics/AnalyticsHandler';

import SearchItem from './SearchItem/SearchItem';
import LoadingFallback from '@/components/LoadingFallback/LoadingFallback';

const SearchRepository = RepositoryFactory.get('search');
const RecommendationsRepository = RepositoryFactory.get('recommendations');
const ProductsRepository = RepositoryFactory.get('products')

const EXPERIMENT_FEATURE = 'search_results';

const DISPLAY_SEARCH_PAGE_SIZE = 10;
const EXTENDED_SEARCH_PAGE_SIZE = 25;

export default {
  name: 'Search',
  components: {
    LoadingFallback,
    SearchItem,
  },
  data() {
    return {
      searchTerm: '',
      inputFocused: false,
      results: null,
      isSearching: false,
      isReranked: false,
      feature: EXPERIMENT_FEATURE,
    };
  },
  computed: {
    ...mapState(['user']),
    ...mapGetters(['personalizeUserID', 'personalizeRecommendationsForVisitor']),
  },
  methods: {
    onInputFocus() {
      this.inputFocused = true;
    },
    onInputBlur() {
      this.inputFocused = false;
    },
    async search(val) {
      // If personalized ranking is going to be called, bring back more items than we
      // intend to display so we have a larger set of products to rerank before
      // trimming for final display. Particularly import for short search phrases to
      // improve the relevancy of results.
      const size = this.personalizeRecommendationsForVisitor ? EXTENDED_SEARCH_PAGE_SIZE * Math.max(1, 4 - Math.min(val.length, 3)) : DISPLAY_SEARCH_PAGE_SIZE;
      const { data } = await SearchRepository.searchProducts(val, size);

      await this.rerank(data);
      if (this.results.length > 0) {
        await this.lookupProducts(this.results);
      }

      AnalyticsHandler.productSearched(this.user, val, data.length);
    },
    async rerank(items) {
      if (this.personalizeRecommendationsForVisitor && items && items.length > 0) {
        const { data } = await RecommendationsRepository.getRerankedItems(this.personalizeUserID, items, EXPERIMENT_FEATURE);
        this.isReranked = JSON.stringify(items) !== JSON.stringify(data);
        this.results = data.slice(0, DISPLAY_SEARCH_PAGE_SIZE);
      } else {
        this.isReranked = false;
        this.results = items;
      }
    },
    async lookupProducts(items) {
      const itemIds = items.map(item => item.itemId);

      const { data } = await ProductsRepository.getProduct(itemIds);

      this.results = items.map((item) => ({
        ...item,
        product: data.find(({id}) => id === item.itemId)
      }));
    }
  },
  watch: {
    async searchTerm(val) {
      if (val.length > 0) {
        this.isSearching = true;
        this.results = null;
        try {
          await this.search(val);
        } finally {
          this.isSearching = false;
        }
      } else {
        this.isSearching = false;
        this.isReranked = false;
        this.results = [];
      }
    },
  },
};
</script>

<style scoped>
.search-results {
  width: 250px;
}

.fa-search {
  position: absolute;
  left: 15px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--grey-500);
  transition: color 150ms ease-in-out;
  pointer-events: none;
}

.fa-search--focused {
  color: var(--grey-600);
}

.input {
  width: 175px;
  border-style: solid;
  border-width: 1px;
  border-color: var(--grey-500);
  border-radius: 4px;
  padding-left: 40px;
  padding-right: 30px;
  transition: border-color 150ms ease-in-out;
}

.input:focus {
  outline: none;
  border-color: var(--blue-600);
}

@media (min-width: 992px) {
  .input {
    width: 250px;
  }
}
</style>
