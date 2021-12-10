<template>
  <ModalLayout :name="name" :show-close-button="false" @closeModal="this.closeClientelingModal">
    <h2 class="mb-4">
      Product shared
    </h2>
    <div class="row">
      <div class="col-6">
        <Product :product="product" feature="clienteling_push" @click="onProductClick"/>
      </div>
      <div class="col-6 d-flex flex-column">
        <div v-if="isOutfitBuilderProduct">
          <div class="mt-5 mb-3">
            A customer assistant has shared a product with you. Would you like use it to build an outfit to try on?
          </div>
          <div>
            <button class="btn btn-primary" @click="onClickTryOn">
              Try on
            </button>
          </div>
        </div>
        <div v-else>
          <div class="mt-5 mb-3">
            A customer assistant has shared a product with you. Click below to discover more about it.
          </div>
          <div>
            <button class="btn btn-primary" @click="onProductClick">
              Discover
            </button>
          </div>
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
    onClickTryOn() {
      this.$router.push({ name: 'OutfitBuilder', params: { productId: this.product.id }})
      this.closeClientelingModal()
    },
    onProductClick() {
      this.$router.push({ name: 'ProductDetail', params: { id: this.product.id }})
      this.closeClientelingModal()
    }
  },
  computed: {
    ...mapState({
      name: (state) => state.clientelingModal.name,
      product: (state) => state.clientelingModal.product,
    }),
    isOutfitBuilderProduct() {
      let categories = ['accessories', 'footwear']
      let styles = ['jacket', 'shirt']
      return categories.includes(this.product.category) || styles.includes(this.product.style)
    }
  },
}
</script>

<style scoped>

</style>