<template>
  <div id="AmazonPayButton"></div>
</template>

<script>
import {RepositoryFactory} from "@/repositories/RepositoryFactory";

const CartsRepository = RepositoryFactory.get('carts')

export default {
    name: "AmazonPayButton",
    data () {
      return {
        payload: {
          "webCheckoutDetails": {
            "checkoutReviewReturnUrl": location.origin.includes('http://localhost:') ? location.origin : location.origin.replace('http://', 'https://')
          },
          "storeId": process.env.VUE_APP_AMAZON_PAY_STORE_ID,
          "chargePermissionType": "OneTime"
        },
        payloadSignature: null
      }
    },
    mounted () {
      this.loadAmazonPayButton()
    },
    methods: {
        async loadAmazonPayButton() {
            let recaptchaScript = document.createElement('script')
            recaptchaScript.setAttribute('src', 'https://www.google.com/recaptcha/api.js')
            document.head.appendChild(recaptchaScript)

            await this.signPayload();
            // eslint-disable-next-line no-undef
            amazon.Pay.renderButton('#AmazonPayButton', {
                merchantId: process.env.VUE_APP_AMAZON_PAY_MERCHANT_ID,
                ledgerCurrency: 'USD',
                sandbox: true,
                checkoutLanguage: 'en_US',
                productType: 'PayOnly',
                placement: 'Cart',
                buttonColor: 'Gold',
                createCheckoutSessionConfig: {
                    payloadJSON: JSON.stringify(this.payload),
                    signature: this.payloadSignature,
                    publicKeyId: process.env.VUE_APP_AMAZON_PAY_PUBLIC_KEY_ID
                }
            });
        },
        async signPayload () {
          const signatureResponse = await CartsRepository.signAmazonPayPayload(this.payload);
          console.log(signatureResponse.data.body)
          this.payloadSignature = signatureResponse.data.body.Signature;
          return this.payloadSignature
        }
    },
    watch: {
      payload () {
        this.signPayload();
      }
    }
}
</script>

<style scoped>

</style>