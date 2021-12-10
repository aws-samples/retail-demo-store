<template>
  <Layout :show-demo-guide="false">
    <div class="container">
      <div class="row">
        <div class="col">
          <h2>
            Scan a product
          </h2>
        </div>
      </div>
      <div class="row">
        <div class="col">
          <qrcode-stream @decode="onQrDecode"/>
        </div>
      </div>
    </div>
  </Layout>
</template>

<script>
import Layout from "@/components/Layout/Layout";
import {QrcodeStream} from 'vue-qrcode-reader'
import {mapActions} from "vuex";
import {RepositoryFactory} from "@/repositories/RepositoryFactory";

const ProductsRepository = RepositoryFactory.get('products');

export default {
  name: "ProductScan",
  components: {Layout, QrcodeStream},
  data() {
    return {
      productId: null,
      product: null
    }
  },
  methods: {
    ...mapActions(['openClientelingModal']),
    async onQrDecode(decodedContent) {
      let decodedJson = JSON.parse(decodedContent)

      if (decodedJson.product_id) {
        // The following lines can be used if the QR code only contains the productId
        let decodedJson = JSON.parse(decodedContent)
        this.productId = decodedJson.product_id
        let {data: product} = await ProductsRepository.getProduct(this.productId)
        this.product = product
      } else {
        // If the QR code contains the full product JSON (ie. enough to render the product component: name, price, style
        // and id) then we can use the product directly, without hitting the products service
        // util/getProductImageUrl.js will accept reconstruct the image link if provided in the following format. This
        // allows us to avoid encoding the full image URL into the QR code
        this.product = {...decodedJson, image: `${decodedJson.id}.jpg`}
      }

      this.openClientelingModal({name: 'scanned-product', product: this.product})

    },
  }
}
</script>

<style scoped>

</style>