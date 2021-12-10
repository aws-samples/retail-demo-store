<template>
  <ModalLayout :name="name" :show-close-button="false" @closeModal="this.closeClientelingModal">
    <h2 class="mb-4">
      Product shared
    </h2>
    <div class="row">
      <div class="col-6">
        <Product :product="product" feature="clienteling_push"/>
      </div>
      <div class="col-6 d-flex">
        <div class="mt-5">
          A customer assistant has shared a product with you. Would you like to try it on?
        </div>
      </div>
    </div>
  </ModalLayout>
</template>

<script>
import ModalLayout from "@/partials/ModalLayout/ModalLayout";
import Product from "@/components/Product/Product";
import {mapActions, mapState} from "vuex";

export default {
  name: "PushedProduct",
  components: {
    ModalLayout,
    Product,
  },
  methods: {
    ...mapActions(['closeClientelingModal']),
  },
  computed: {
    ...mapState({
      name: (state) => state.clientelingModal.name,
      product: (state) => state.clientelingModal.product,
    }),
  },
}
</script>

<style scoped>

</style>