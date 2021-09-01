<template>
  <Layout>
    <div class="content">

      <!-- Loading Indicator -->
      <div class="container mb-4" v-if="!orders">
        <i class="fas fa-spinner fa-spin fa-3x"></i>
      </div>

      <div class="container">
        <h1>Your Orders</h1>

        <table class="table" v-if="orders">
          <tr>
            <th>ID</th>
            <th>Username</th>
            <th># Items</th>
            <th>Total</th>
          </tr>
          <tr v-for="order in orders" v-bind:key="order.id">
            <td>{{ order.id }}</td>
            <td>{{ order.username}}
            <td>
              <div v-for="item in order.items" v-bind:key="item.product_id">
                Product {{ item.product_id }}: {{ item.quantity }} @ ${{ item.price }}
              </div>
            </td>
            <td>${{ order.total.toFixed(2) }}</td>
          </tr>
        </table>

        <div class="alert alert-secondary no-orders" v-if="!orders || orders.length == 0">You currently do not have any orders</div>

      </div>
    </div>
  </Layout>
</template>

<script>
import { mapState } from 'vuex'

import { RepositoryFactory } from '@/repositories/RepositoryFactory'

import Layout from '@/components/Layout/Layout'

const OrdersRepository = RepositoryFactory.get('orders')

export default {
  name: 'Orders',
  components: {
    Layout,
  },
  data () {
    return {  
      errors: [],
      orders: null
    }
  },
  created () {
    this.getOrders()
  },
  methods: {
    async getOrders (){
      this.orders = null;

      const { data } = await OrdersRepository.getOrdersByUsername(this.user.username)
      
      this.orders = data
    },    
  },
  computed: {
    ...mapState({user: state => state.user})
  },
  watch: {
    user() {
      this.getOrders()
    }
  }
}
</script>

<style scoped>
.no-orders {
  margin-bottom: 150px;
}
</style>