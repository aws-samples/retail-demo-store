import { RepositoryFactory } from '@/repositories/RepositoryFactory';
import { AnalyticsHandler } from '@/analytics/AnalyticsHandler';
import { capitalize } from '@/util/capitalize';
import { user } from './user';

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

      if (this.product.image.includes('://')) return this.product.image;

      return `${process.env.VUE_APP_IMAGE_ROOT_URL}${this.product.category}/${this.product.image}`;
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
