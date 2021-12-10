<template>
  <ModalLayout :name="name" :show-close-button="false" @closeModal="this.closeClientelingModal">
    <h2 class="mb-4">
      Share with customer
    </h2>
    <div class="row">
      <div class="col-6">
        <Product :product="product" feature="dogs"/>
      </div>
      <div class="col-6 d-flex">
        <div class="my-auto pb-5">
          <div class="mb-4">
            Would you like to push this product to the customer's device?
          </div>
          <button class="btn btn-outline-primary" @click="pushProduct">
            Yes
          </button>
        </div>
      </div>
    </div>
  </ModalLayout>
</template>

<script>
import {mapActions, mapState} from "vuex";
import Product from "@/components/Product/Product";
import ModalLayout from "@/partials/ModalLayout/ModalLayout";
import {Auth} from "aws-amplify";


export default {
  name: "ShareProduct",
  components: {ModalLayout, Product},
  data() {
    return {
      cognitoUser: null
    }
  },
  created() {
    this.getCognitoUser()
  },
  methods: {
    ...mapActions(['closeClientelingModal']),
    async getCognitoUser() {
      this.cognitoUser = await Auth.currentAuthenticatedUser()
    },
    pushProduct() {
      let connection = new WebSocket(`${process.env.VUE_APP_LOCATION_NOTIFICATION_URL}?userId=customerAssistant`)
      connection.onopen = () => {
        let data = {
          action: 'pushproduct',
          data: {
            userId: this.cognitoUser.username,
            productId: `${this.product.id}`
          }
        }
        connection.send(JSON.stringify(data))
        connection.close()
      }
    }
  },
  computed: {
    ...mapState({
      name: (state) => state.clientelingModal.name,
      product: (state) => state.clientelingModal.product,
    }),
  },
}
</script>
