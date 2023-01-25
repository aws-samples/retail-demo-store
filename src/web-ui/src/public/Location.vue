<template>
  <Layout>
    <div class="content">
      <location-demo-navigation/>
      <div class="container">
        <div class="row">
          <div class="col-2">
            <button type="button" class="btn btn-primary mb-2 mx-2" v-on:click="this.triggerPurchaseJourney" :disabled="this.journeyInProgress">Purchase Journey</button>
            <button type="button" class="btn btn-primary m-2" v-on:click="this.triggerCollectionJourney" :disabled="this.journeyInProgress">Collection Journey</button>
          </div>
          <div class="col-10">
            <div style="height: 500px; width: 100%">
              <amplify-map
                  :device-positions="this.customerPosition ? [this.customerPosition] : [1, 1]"
                  :routes="[this.customerRoute]"
                  :store-position="this.storeLocation"
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  </Layout>
</template>

<script>
import AmplifyMap from "@/public/components/AmplifyMap.vue";
import Location from "@/location/Location";
import { Auth } from 'aws-amplify';
import {RepositoryFactory} from "@/repositories/RepositoryFactory";
import AmplifyStore from "@/store/store";
import swal from 'sweetalert';
import LocationDemoNavigation from "@/public/LocationDemoNavigation.vue";
import Layout from "@/components/Layout/Layout.vue";

const locationApi = new Location();
const LocationRepository = RepositoryFactory.get('location');
const OrdersRepository = RepositoryFactory.get('orders');

export default {
  name: "Location",
  components: {
    AmplifyMap,
    LocationDemoNavigation,
    Layout
  },
  data () {
    return {
      customerPosition: null,
      customerRoute: null,
      storeLocation: null,
      cognitoUser: null,
      orders: null,
      journeyInProgress: false
    }
  },
  async created () {
    this.getIncompleteCollectionOrders();
    this.fetchStoreLocation();
    await this.getCognitoUser();
    this.fetchCustomerRoute()
        .then(() => {
          this.customerPosition = this.customerRoute[0];
          locationApi.updateDevicePositions([{
            'DeviceId': this.cognitoUser.username,
            'Position': this.customerRoute[0]
          }])
        });
  },
  methods: {
    async fetchCustomerRoute() {
      const customerRouteGeojson = (await LocationRepository.get_customer_route()).data
      if (customerRouteGeojson.type === "FeatureCollection") {
        if (customerRouteGeojson.features.length > 1) {
          console.log("Found more than one route in response. Only the first route will be used")
        }
        this.customerRoute = customerRouteGeojson.features[0].geometry.coordinates
      } else {
        this.customerRoute = customerRouteGeojson.geometry.coordinates
      }
    },
    async fetchStoreLocation() {
      const storeLocationGeojson = (await LocationRepository.get_store_location()).data
      if (storeLocationGeojson.type === "FeatureCollection") {
        if (storeLocationGeojson.features.length > 1) {
          console.log("Found more than one location in response. Only the first route will be used")
        }
        this.storeLocation = storeLocationGeojson.features[0].geometry.coordinates
      } else {
        this.storeLocation = storeLocationGeojson.geometry.coordinates
      }
    },
    async getCognitoUser() {
      this.cognitoUser = await Auth.currentAuthenticatedUser()
    },
    async setCollectionDemoJourney() {
      await Auth.updateUserAttributes(this.cognitoUser, {
        'custom:demo_journey': 'COLLECTION',
      })
    },
    async setPurchaseDemoJourney() {
      await Auth.updateUserAttributes(this.cognitoUser, {
        'custom:demo_journey': 'PURCHASE',
      })
    },
    async getIncompleteCollectionOrders() {
      const { data } = await OrdersRepository.getOrdersByUsername(this.user.username)
      this.orders = data.filter(order => order.delivery_type === "COLLECTION" && order.delivery_status !== "COMPLETE")
    },
    async createOrder(collectionPhone) {
      let defaultOrder = {
        items: [{
          product_id: "e1669081-8ffc-4dec-97a6-e9176d7f6651",
          quantity: 1,
          price: 124.99
        }],
        collection_phone: collectionPhone,
        total: 124.99,
        delivery_type: 'COLLECTION'
      }
      defaultOrder.username = this.user.username
      defaultOrder.email = this.user.email
      if (this.user.addresses && this.user.addresses.length > 0) {
        defaultOrder.billing_address = this.user.addresses[0]
        defaultOrder.shipping_address = this.user.addresses[0]
      }
      console.log('Inserting order')
      console.log(defaultOrder)
      await OrdersRepository.createOrder(defaultOrder)
    },
    async triggerPurchaseJourney() {
      this.journeyInProgress = true;
      await this.setPurchaseDemoJourney();
      this.animateJourney();
    },
    async triggerCollectionJourney() {
      await Promise.all([this.getIncompleteCollectionOrders(), this.setCollectionDemoJourney()]);

      if (this.orders.length) {
        this.journeyInProgress = true;
        this.animateJourney();
      } else {
        swal({
          title: "No orders awaiting collection",
          icon: "warning",
          buttons: {
            cancel: "Cancel",
            populate: "Create order automatically"
          }
        }).then((value) => {
          console.log(value)
          switch (value) {
            case "cancel":
              break;
            case "populate":
              swal({
                title: "Input the collection phone number on the order",
                content: "input",
              }).then((value)=> {
                console.log(value)
                this.createOrder(value.replace(/\s+/g, ''))
                    .then(() => {
                      this.journeyInProgress = true;
                      this.animateJourney()
                    });
                })
          }
        });
      }
    },
    animateJourney() {
      const journeySteps = this.customerRoute.length;
      this.customerRoute.forEach((location, index) => {
        setTimeout(() => {
          this.customerPosition = location;
          locationApi.updateDevicePositions([{
            'DeviceId': this.cognitoUser.username,
            'Position': location
          }]);
          if (journeySteps === index + 1) {
            this.journeyInProgress = false;
          }
        }, 1000 * index)

      })
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