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
          <qrcode-stream :camera="camera" @init="onInit" @decode="onQrDecode">
            <LoadingFallback class="mt-3" v-if="loading"/>
            <div v-if="product" class="scan-confirmation d-flex">
              <div class="my-auto">
                <h4>
                  Product scanned
                </h4>
                <button class="btn btn-primary" @click="clickScanAnother">
                  Scan another
                </button>
              </div>
            </div>
          </qrcode-stream>
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
import LoadingFallback from "@/components/LoadingFallback/LoadingFallback";


const ProductsRepository = RepositoryFactory.get('products');

export default {
  name: "ProductScan",
  components: {LoadingFallback, Layout, QrcodeStream},
  data() {
    return {
      camera: 'auto',
      loading: false,
      productId: null,
      product: null
    }
  },
  methods: {
    ...mapActions(['openClientelingModal']),
    async onInit(promise) {
      this.loading = true
      try {
        await promise
      } catch (error) {
        console.error(error)
      } finally {
        this.loading = false
      }
    },
    unpause() {
      this.camera = 'auto'
    },
    pause() {
      this.camera = 'off'
    },
    async onQrDecode(decodedContent) {
      this.pause()
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
    clickScanAnother() {
      this.product = null
      this.unpause()
    }
  }
}
</script>

<style scoped>
.scan-confirmation {
  position: absolute;
  width: 100%;
  height: 100%;

  background-color: rgba(255, 255, 255, .8);

  display: flex;
  flex-flow: row nowrap;
  justify-content: center;
}
</style>