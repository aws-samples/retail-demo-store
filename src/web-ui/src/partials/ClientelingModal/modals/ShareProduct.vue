<template>
  <div class="modal fade" tabindex="-1" role="dialog" aria-hidden="true" ref="modal">
    <div class="modal-dialog" role="document">
      <div class="modal-content">
        <div class="modal-header">
          <button type="button" class="close" data-dismiss="modal" aria-label="Close">
            <i class="fa fa-times"></i>
          </button>
        </div>

        <div class="modal-body px-5 pb-5">
          <h2>
            Share with customer
          </h2>
          <div class="row">
            <div class="col-6">
              <Product :product="product" feature="dogs"/>
            </div>
            <div class="col-6">
              <div>
                Would you like to push this product to the customer's device?
              </div>
              <button class="btn btn-outline-primary" >
                Yes
              </button>
<!--              <button class="close-modal btn btn-outline-secondary" @click="closeClientelingModal">-->
<!--                Close-->
<!--              </button>-->
            </div>
          </div>
          <slot></slot>


        </div>
      </div>
    </div>
  </div>
</template>

<script>
import {mapActions, mapState} from "vuex";
import Product from "@/components/Product/Product";


export default {
  name: "ShareProduct",
  components: {Product},
  methods: {
    ...mapActions(['closeClientelingModal']),
  },
  computed: {
    ...mapState({
      name: (state) => state.clientelingModal.name,
      product: (state) => state.clientelingModal.product,
    }),
  },
  mounted() {
    // eslint-disable-next-line no-undef
    $(this.$refs.modal).modal('show');

    // eslint-disable-next-line no-undef
    $(this.$refs.modal).on('hidden.bs.modal', this.closeClientelingModal);
  },
  beforeDestroy() {
    // eslint-disable-next-line no-undef
    $(this.$refs.modal).modal('hide');
  },
  watch: {
    async name(newName) {
      // eslint-disable-next-line no-undef
      $(this.$refs.modal).modal(newName ? 'show' : 'hide');
    },
  }
}
</script>

<style scoped>
.modal-header {
  border-bottom: none;
}

.close-modal {
  width: 100%;
  max-width: 200px;
  border-color: var(--blue-500);
  color: var(--blue-500);
}

.close-modal:hover,
.close-modal:focus {
  background: var(--blue-600);
  border-color: var(--blue-600);
  color: var(--white);
}

.modal-dialog {
  max-width: 800px;
}
</style>