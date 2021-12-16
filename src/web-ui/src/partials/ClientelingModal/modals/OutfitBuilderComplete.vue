<template>
  <ModalLayout :name="name" :show-close-button="false" @closeModal="closeClientelingModal">
    <h2 class="mb-4">
      Try it on!
    </h2>
    <p>
      The products you selected will be delivered to the nearest fitting room by a customer assistant.
    </p>
    <p>
      If another product catches your eye along the way, you can use the built-in QR code scanner to find out more about it.
    </p>
    <ScanLink/>
  </ModalLayout>
</template>

<script>
import {mapActions, mapState} from "vuex";
import ModalLayout from "@/partials/ModalLayout/ModalLayout";
import ScanLink from "@/partials/Navigation/ScanLink/ScanLink";

export default {
  name: "OutfitBuilderComplete",
  components: {ScanLink, ModalLayout},
  methods: {
    ...mapActions(['closeClientelingModal']),
  },
  computed: {
    ...mapState({
      name: (state) => state.clientelingModal.name,
    }),
  },
}
</script>

<style scoped>

</style>