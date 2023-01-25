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
            // This is a truncated demo: instead of continuing the session, we route to the Amazon Pay instructions.
            // To enable the full process we need to handle the order review and downstream processing and
            // a full HTTPS service on the Retail Demo Store.
            "checkoutReviewReturnUrl": 'https://developer.amazon.com/docs/amazon-pay-checkout/introduction.html'
          },
          "storeId": import.meta.env.VITE_AMAZON_PAY_STORE_ID,
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
            // Load Amazon Pay script - we can do it here so we don't have to load it at start
            if (!document.getElementById("amazon-pay-checkout-javascript")) {
              let payscript = document.createElement('script')
              payscript.setAttribute('src', 'https://static-na.payments-amazon.com/checkout.js')
              payscript.setAttribute('id', 'amazon-pay-checkout-javascript')
              document.head.appendChild(payscript)
            }

            // Sign the payload for starting a checkout session
            await this.signPayload();

            // eslint-disable-next-line no-undef
            amazon.Pay.renderButton('#AmazonPayButton', {
                merchantId: import.meta.env.VITE_AMAZON_PAY_MERCHANT_ID,
                ledgerCurrency: 'USD',
                sandbox: true,
                checkoutLanguage: 'en_US',
                productType: 'PayOnly',
                placement: 'Checkout',
                buttonColor: 'Gold',
                createCheckoutSessionConfig: {
                    payloadJSON: JSON.stringify(this.payload),
                    signature: this.payloadSignature,
                    publicKeyId: import.meta.env.VITE_AMAZON_PAY_PUBLIC_KEY_ID
                }
            });
        },
        async signPayload () {
          const signatureResponse = await CartsRepository.signAmazonPayPayload(this.payload);
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