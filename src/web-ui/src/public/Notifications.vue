<template>
  <div>

  </div>
</template>

<script>
import {Auth} from "aws-amplify";
import swal from "sweetalert";
import AmplifyStore from "@/store/store";
import {RepositoryFactory} from "@/repositories/RepositoryFactory";

const RecommendationsRepository = RepositoryFactory.get('recommendations');
const ProductsRepository = RepositoryFactory.get('products')

export default {
  name: "Notifications",
  data() {
    return {
      connection: null,
      cognitoUser: null
    }
  },
  created () {
    this.getCognitoUser()
      .then(() => this.openWebsocketConnection())
      .catch(err => console.log(err));
  },
  methods: {
    async getCognitoUser() {
      this.cognitoUser = await Auth.currentAuthenticatedUser()
    },
    openWebsocketConnection() {

      if (!this.notificationsEnabled) {
        return
      }

      this.connection = new WebSocket(`${import.meta.env.VITE_LOCATION_NOTIFICATION_URL}?userId=${this.cognitoUser.username}`)

      this.connection.onopen = (e) => {
        console.log(e)
        console.log("Websocket connection open for notifcations.")
      }

      this.connection.onmessage = (e) => {
        console.log("Received notification message:")
        const messageData = JSON.parse(e.data)
        console.log(messageData)
        if (this.isInstoreView) {
          if (messageData.EventType === "COLLECTION") {
            const customerName = `${messageData.Orders[0].billing_address.first_name} ${messageData.Orders[0].billing_address.last_name}`
            let orderDetail;
            const orders = messageData.Orders;
            if (orders.length > 1) {
              const orderIds = orders.map((order => `#${order.id}`))
              orderDetail = `orders ${orderIds.join(', ')}`;
            } else {
              orderDetail = `order #${orders[0].id}`;
            }
            let pickupTime = new Date();
            pickupTime.setMinutes(pickupTime.getMinutes() + 20);
            const formattedPickupTime = pickupTime.toLocaleString('en-US');
            swal({
              title: 'New Collection',
              text: `${customerName} will be at level 3 at ${formattedPickupTime} to collect ${orderDetail}`
            });
          }
        } else if (!this.isLocationView) {
          if (messageData.EventType === "PURCHASE") {
            RecommendationsRepository.getCouponOffer(this.user.id)
                .then((offer_recommendation) => {
                  const offer = offer_recommendation.data.offer;

                  let offerDiv = document.createElement("div");
                  offerDiv.innerHTML = `
                                <div class='row'>
                                    <div class='col'>
                                        <b>${offer.codes[0]}:</b> ${offer.description}
                                    </div>
                                </div>`
                  swal({
                    title: 'Store nearby',
                    text: `We noticed that you are close to your Local AWS Retail Demo Store. Pop into our store near you, check our newest collection, and use the code: ${offer.codes[0]} for any purchase and get ${offer.description}.`,
                    content: offerDiv
                  });
                });
          } else if (messageData.EventType === "COLLECTION") {
            const orders = messageData.Orders;
            const orderListDiv = document.createElement("div");

            const ordersHtml = orders.slice(0, 3).map((order) => {
              const orderHtml = order.items.slice(0, 3).map(async (product) => {
                const { data } = await ProductsRepository.getProduct(product.product_id)
                const productImageUrl = this.getProductImageURL(data)
                return `<div class="col-4"><img src="${productImageUrl}" style="width: 100%"><small>${data.name}</small></div>`
              })

              return Promise.all(orderHtml).then((productHtml) => {
                 return `<div>Order #${order.id}</div><div class="row">${productHtml.join('')}</div>`
              })
            })

            Promise.all(ordersHtml).then((responses) => {
              orderListDiv.innerHTML = responses.join('')
              swal({
                title: 'Collection available',
                text: `Welcome! We are waiting for you at Level 3, Door 2 of your Local Retail Demo Store, and Steve from our team will be greeting you with your following order(s):`,
                content: orderListDiv
              });
            })
          }
        }
      }
    },
    getProductImageURL (product) {
      if (product.image.includes('://')) {
        return product.image
      } else {
        let root_url = import.meta.env.VITE_IMAGE_ROOT_URL
        return root_url + product.category + '/' + product.image
      }
    }
  },
  computed: {
    isInstoreView() {
      return this.$route.name.toLowerCase() === 'collections';
    },
    isLocationView() {
      return this.$route.name.toLowerCase() === 'location';
    },
    user() {
      return AmplifyStore.state.user
    },
    notificationsEnabled() {
      const enabled = import.meta.env.VITE_LOCATION_NOTIFICATION_URL && import.meta.env.VITE_LOCATION_NOTIFICATION_URL !== ''
      if (enabled) {
        console.log('Websocket notifications are enabled')
      }
      return enabled
    }
  },
  watch: {
    user () {
      if (this.connection) {
        this.connection.close();
      }
      this.getCognitoUser().then(() => this.openWebsocketConnection());
    }
  }
}
</script>

<style scoped>

</style>