<template>
  <ModalLayout :name="name" :show-close-button="true" @closeModal="closeClientelingModal">
    <h2 class="mb-4">
      Product scanned
    </h2>
    <div class="row">
      <div class="col">
        <Product class="mb-4" :product="product" feature="dogs" @click="onClickProduct"/>
      </div>
    </div>
  </ModalLayout>
</template>

<script>
import {mapActions, mapState} from "vuex";
import Product from "@/components/Product/Product";
import ModalLayout from "@/partials/ModalLayout/ModalLayout";


export default {
  name: "ScannedProduct",
  components: {ModalLayout, Product},
  methods: {
    ...mapActions(['closeClientelingModal']),
    onClickProduct (e) {
      e.preventDefault()
      // This is a workaround to account for the fact we can't use the video camera on HTTP
      window.location = `http://${window.location.host}/#/product/${this.product.id}`
      // this.$router.push(`product/${this.product.id}`)
      this.closeClientelingModal()
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
