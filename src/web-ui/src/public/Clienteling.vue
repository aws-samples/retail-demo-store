<template>
  <Layout>
    <div class="container">
      <div class="row">
        <div class="col">
          <h1>
            Customer Profile: {{ userFullName }}
          </h1>
        </div>
      </div>
      <div class="row alert alert-secondary">
        <div class="col">
          Age: {{ user ? user.age : '' }}
        </div>
        <div class="col">
          Average order value: ${{ averageOrderValue }}
        </div>
        <div class="col">
          Total orders: {{ totalOrders }}
        </div>
      </div>
      <RecommendedProductsSection
          :recommendedProducts="userRecommendations"
          feature="FEATURE"
          class="mt-4"
          @productClick="onProductClick"
      >
        <template #heading>
          Recommended for {{ userFullName }}
        </template>
      </RecommendedProductsSection>
      <RecommendedProductsSection
          :recommendedProducts="orderedProductDetail"
          feature="FEATURE"
          class="mt-4"
      >
        <template #heading>
          Recently ordered products
        </template>
      </RecommendedProductsSection>
      <RecommendedProductsSection
          :recommendedProducts="abandonedCartProductDetail"
          feature="FEATURE"
          class="mt-4"
      >
        <template #heading>
          Abandoned carts
        </template>
      </RecommendedProductsSection>

    </div>
  </Layout>
</template>

<script>
import {mapActions} from "vuex";
import Layout from "@/components/Layout/Layout";
import {RepositoryFactory} from "@/repositories/RepositoryFactory";
import RecommendedProductsSection from "@/components/RecommendedProductsSection/RecommendedProductsSection";

const CartsRepository = RepositoryFactory.get('carts');
const OrdersRepository = RepositoryFactory.get('orders');
const ProductsRepository = RepositoryFactory.get('products');
const RecommendationsRepository = RepositoryFactory.get('recommendations');
const UsersRepository = RepositoryFactory.get('users');

export default {
  name: "Clienteling",
  components: {
    RecommendedProductsSection,
    Layout
  },
  data() {
    return {
      abandonedCartProductDetail: null,
      orderedProductDetail: null,
      user: null,
      userAbandonedCarts: null,
      userOrders: null,
      userRecommendations: null,
    }
  },
  async created() {
    await this.fetchData()
  },
  methods: {
    ...mapActions(['openClientelingModal']),
    async fetchData() {
      this.getUser();
      this.getUserRecommendations()
      this.getUserOrders(this.$route.params.username).then(this.getOrderProductDetails)
      this.getUserAbandonedCarts(this.$route.params.username).then(this.getAbandonedCartProductDetails)
    },
    async getUser() {
      let {data} = await UsersRepository.getUserByUsername(this.$route.params.username)
      this.user = data
    },
    async getUserAbandonedCarts(username) {
      let {data} = await CartsRepository.getCartsByUsername(username)
      this.userAbandonedCarts = data
    },
    async getUserOrders(username) {
      let {data} = await OrdersRepository.getOrdersByUsername(username)
      this.userOrders = data
    },
    async getUserRecommendations() {
      let {data} = await RecommendationsRepository.getRecommendationsForUser(this.$route.params.username)
      this.userRecommendations = data
    },
    async getOrderProductDetails() {
      let detail = await this.getItemDetails(this.userOrders)
      this.orderedProductDetail = detail.map((product) => {
        return {product: product}
      })
    },
    async getAbandonedCartProductDetails() {
      if (this.userAbandonedCarts?.length > 0) {
        let detail = await this.getItemDetails(this.userAbandonedCarts)
        this.abandonedCartProductDetail = detail.map((product) => {
          return {product: product}
        })
      } else {
        this.abandonedCartProductDetail = []
      }
    },
    async getItemDetails(items) {
      let productIds = items.reduce((productIds, order) => {
        if (order.items) {
          let ids = order.items.map(item => item.product_id)
          return [...productIds, ...ids]
        } else {
          return productIds
        }
      }, [])
      let uniqueProducts = Array.from(new Set(productIds))
      let {data} = await ProductsRepository.getProduct(uniqueProducts)
      if (!Array.isArray(data)) {
        data = new Array(data)
      }
      return data
    },
    onProductClick (e, product) {
      e.preventDefault()
      this.openClientelingModal({name: 'share-product', product: product})
    }
  },
  computed: {
    totalOrders() {
      return this.userOrders ? this.userOrders.length : 0
    },
    averageOrderValue() {
      if (this.userOrders?.length > 0) {
        let totalValue = this.userOrders.reduce((total, order) => total + order.total, 0)
        let averageValue = totalValue / this.userOrders.length
        return averageValue.toFixed(2)
      } else {
        return 0
      }
    },
    userFullName() {
      return this.user?.first_name + ' ' + this.user?.last_name
    },
  },
  watch: {
    '$route.params.username': function () {
      this.fetchData();
    }
  },
}
</script>

<style scoped>

</style>
