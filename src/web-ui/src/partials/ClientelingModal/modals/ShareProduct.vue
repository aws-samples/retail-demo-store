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
        <div class="my-auto pb-3">
          <div>
            Would you like to send this product to the customer's device?
          </div>
          <div class="font-weight-bold font-small mt-2" v-if="!isOutfitBuilderProduct">
            Note: This product is not available for outfit builder.
          </div>
          <button class="btn btn-primary mt-3" @click="pushProduct">
            Send
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
    isOutfitBuilderProduct () {
      let categories = ['accessories', 'footwear']
      let styles = ['jacket', 'shirt']
      return categories.includes(this.product.category) || styles.includes(this.product.style)
    }
  },
}
</script>
