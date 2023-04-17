<template>
  <Layout>
    <div>
      <location-demo-navigation/>
      <div class="container">
        <div class="row">
          <div class=col>
            <h4>Collections</h4>
            <p>A simple store-side view of upcoming collections.</p>
          </div>
        </div>
        <div class="alert alert-secondary" role="alert" v-if="ordersLoaded && !orders.length">
          No orders awaiting collection.
        </div>
        <div v-for="order in this.orders" v-bind:key="order.id">
          <div class="row">
            <div class="col text-left">
              <h4 class="m-0">
                {{ order.billing_address.first_name }} {{ order.billing_address.last_name }} - #{{ order.id }}
              </h4>
            </div>
            <div class="col text-right">
              <button type="button" class="btn btn-primary" v-on:click="() => completeCollection(order) ">
                Collection complete
              </button>
            </div>
          </div>
          <hr class="mt-2 mb-4"/>
        </div>
      </div>
    </div>
  </Layout>
</template>

<script>
import {RepositoryFactory} from "@/repositories/RepositoryFactory";
import LocationDemoNavigation from "@/public/LocationDemoNavigation.vue";
import Layout from "@/components/Layout/Layout.vue";

const OrdersRepository = RepositoryFactory.get('orders')

export default {
  name: "Collections",
  components: {
    Layout,
    LocationDemoNavigation
  },
  data () {
    return {
      ordersLoaded: false,
      orders: null
    }
  },
  async created () {
    await this.getOrders();
  },
  methods: {
    async getOrders () {
      const allOrders = (await OrdersRepository.get()).data;
      console.log("All your orders:")
      console.log(allOrders)
      this.orders = allOrders.filter(order => order.delivery_type === "COLLECTION" && order.delivery_status !== "COMPLETE");
      this.ordersLoaded = true;
    },
    async completeCollection (order) {
      order.delivery_status = 'COMPLETE';
      OrdersRepository.updateOrder(order)
        .then(() => this.getOrders())
    }
  }
}
</script>

<style scoped>

</style>