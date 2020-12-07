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
        :product_id="result.itemId"
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

const EXPERIMENT_FEATURE = 'search_results';

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
    ...mapGetters(['personalizeUserID']),
  },
  methods: {
    onInputFocus() {
      this.inputFocused = true;
    },
    onInputBlur() {
      this.inputFocused = false;
    },
    async search(val) {
      const { data } = await SearchRepository.searchProducts(val);

      await this.rerank(data);

      AnalyticsHandler.productSearched(this.user, val, data.length);
    },
    async rerank(items) {
      if (this.personalizeUserID && items && items.length > 0) {
        const { data } = await RecommendationsRepository.getRerankedItems(this.personalizeUserID, items, EXPERIMENT_FEATURE);
        this.isReranked = JSON.stringify(items) !== JSON.stringify(data);
        this.results = data;
      } else {
        this.isReranked = false;
        this.results = items;
      }
    },
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
}

.fa-search--focused {
  color: var(--grey-600);
}

.input {
  width: 175px;
  border-style: solid;
  border-width: 2px;
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
