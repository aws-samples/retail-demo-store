import { mapState } from 'vuex';
import { RepositoryFactory } from '@/repositories/RepositoryFactory';
import { AnalyticsHandler } from '@/analytics/AnalyticsHandler';
import AmplifyStore from '@/store/store';
import swal from 'sweetalert';
import { user } from './user';
import { formatPrice } from '@/util/formatPrice';

const CartsRepository = RepositoryFactory.get('carts');

const parseCart = (cart) =>
  cart.items !== null
    ? cart
    : {
        ...cart,
        items: [],
      };

const TAX_RATE = 0.05;
const SHIPPING_RATE = 10;

export const cart = {
  mixnins: [user],
  data() {
    return {
      cart: null,
    };
  },
  computed: {
    ...mapState(['cartID']),
    cartSubTotal() {
      if (!this.cart) return null;

      return this.cart.items.reduce((subtotal, item) => subtotal + item.quantity * item.price, 0);
    },
    cartTaxRate() {
      if (!this.cart) return null;

      return this.cartSubTotal * TAX_RATE;
    },
    cartShippingRate() {
      if (!this.cart) return null;

      return this.cartSubtotal > 100 ? 0 : SHIPPING_RATE;
    },
    cartTotal() {
      if (!this.cart) return null;

      return this.cartSubTotal + this.cartTaxRate + this.cartShippingRate;
    },
    cartQuantity() {
      if (!this.cart) return null;

      return this.cart.items.reduce((total, item) => total + item.quantity, 0);
    },
    formattedCartTotal() {
      if (!this.cart) return null;

      return formatPrice(this.cartTotal);
    },
  },
  methods: {
    // CRUD
    async createCart() {
      const { data } = await CartsRepository.createCart(this.username);

      const cart = parseCart(data);

      this.cart = cart;

      AmplifyStore.commit('setCartID', cart.id);
    },
    async getCart() {
      // Since cart service holds carts in memory, they can be lost on restarts.
      // Make sure our cart was returned. Otherwise create a new one.
      if (this.cartID === null) return this.createCart();

      const { data } = await CartsRepository.getCartByID(this.cartID);

      if (data.id !== this.cartID) {
        console.warn(`Cart ${this.cartID} not found. Creating new cart. Was cart service restarted?`);
        return this.createCart();
      }

      this.cart = parseCart(data);
    },
    async updateCart() {
      const { data } = await CartsRepository.updateCart(this.cart);
      this.cart = parseCart(data);
    },
    async addToCart(product, quantity, feature, exp) {
      const existingProduct = this.cart.items.find((item) => item.product_id === product.id);

      if (existingProduct) {
        existingProduct.quantity += quantity;
      } else {
        this.cart.items.push({ product_id: product.id, price: product.price, quantity });
      }

      await this.updateCart();

      this.recordAddedToCart(product, existingProduct?.quantity ?? quantity, feature, exp);

      this.renderAddedToCartConfirmation();
    },
    async removeFromCart(product_id) {
      const productIndex = this.cart.items.findIndex((item) => item.product_id === product_id);

      if (productIndex === -1) return;

      const removedItem = this.cart.items.splice(productIndex, 1);

      await this.updateCart();

      AnalyticsHandler.productRemovedFromCart(this.user, this.cart, removedItem, removedItem.quantity);
    },
    async increaseQuantity(product_id) {
      const item = this.cart.items.find((item) => item.product_id === product_id);

      if (!item) return;

      item.quantity++;

      await this.updateCart();

      AnalyticsHandler.productQuantityUpdatedInCart(this.user, this.cart, item, 1);
    },
    async decreaseQuantity(product_id) {
      const itemIndex = this.cart.items.findIndex((item) => item.product_id === product_id);

      if (itemIndex === -1) return;

      const item = this.cart.items[itemIndex];

      if (item.quantity === 1) {
        this.cart.items.splice(itemIndex, 1);
        await this.updateCart();
        AnalyticsHandler.productRemovedFromCart(this.user, this.cart, item, item.quantity);
      } else {
        item.quantity--;
        await this.updateCart();
        AnalyticsHandler.productQuantityUpdatedInCart(this.user, this.cart, item, -1);
      }
    },

    // analytics
    recordAddedToCart(product, quantity, feature, exp) {
      AnalyticsHandler.productAddedToCart(this.user, this.cart, product, quantity, feature, exp);
    },

    recordCartViewed() {
      AnalyticsHandler.cartViewed(this.user, this.cart, this.cartQuantity, this.cartSubTotal, this.cartTotal);
    },

    // other side effects
    renderAddedToCartConfirmation() {
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
  },
};
