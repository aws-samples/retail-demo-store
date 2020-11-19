import { RepositoryFactory } from '@/repositories/RepositoryFactory';
import { AnalyticsHandler } from '@/analytics/AnalyticsHandler';
import { capitalize } from '@/util/capitalize';
import { user } from './user';
import { getProductImageUrl } from '../util/getProductImageUrl';

const ProductsRepository = RepositoryFactory.get('products');

export const product = {
  mixins: [user],
  data() {
    return {
      product: null,
    };
  },
  computed: {
    productImageUrl() {
      if (!this.product) return null;

      return getProductImageUrl(this.product);
    },
    readableProductCategory() {
      if (!this.product) return null;

      return capitalize(this.product.category);
    },
  },
  methods: {
    async getProductByID(product_id) {
      const { data } = await ProductsRepository.getProduct(product_id);
      this.product = data;
    },
    recordProductViewed(feature, exp) {
      AnalyticsHandler.productViewed(this.user, this.product, feature, exp);
    },
  },
};
