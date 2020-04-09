<template>
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

      <div class="alert alert-secondary" v-if="!orders || orders.length == 0">You currently do not have any orders</div>

    </div>
  </div>
</template>

<script>
import AmplifyStore from '@/store/store'

import { RepositoryFactory } from '@/repositories/RepositoryFactory'

const OrdersRepository = RepositoryFactory.get('orders')

export default {
  name: 'Orders',
  components: {
  },
  props: {
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
      const { data } = await OrdersRepository.getOrdersByUsername(this.user.username)
      this.orders = data
    },    
  },
  computed: {
    user() { 
      return AmplifyStore.state.user
    },
  }
}
</script>

<style scoped>
</style>