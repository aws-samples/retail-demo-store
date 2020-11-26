import { RepositoryFactory } from '@/repositories/RepositoryFactory';
import { capitalize } from '@/util/capitalize';

const ProductsRepository = RepositoryFactory.get('products');

export const categories = {
  state: () => ({ categories: null }),
  getters: {
    formattedCategories: (state) => state.categories?.map(({ name }) => capitalize(name)),
  },
  mutations: {
    setCategories: (state, newCategories) => (state.categories = newCategories),
  },
  actions: {
    getCategories: async ({ commit }) => {
      commit('setCategories', null);

      const { data: categories } = await ProductsRepository.getCategories();

      commit('setCategories', categories);
    },
  },
};
