<template id="js-fenix-template">
  <div class="d-flex" v-if="fenixDataReceived">
    <h5 class="p-4 col-lg-4 bg-light font-weight-bold d-flex align-items-center">Shipping Method</h5>
    <div class="col-lg-8">
      <p class="form-check mt-2 mb-0" v-for="item in fenixResponse" :key="item.response">
        <label>
<input class="form-check-input" type="radio" name="fenixcheckout" id="fenixcheckout" :value="false">
          <span class="delivery-name"><b v-html="item.shippingMethodDesc"></b></span> <span class="text-right">$<b v-html="item.shippingCost.amount"></b></span> <br> 
        <small>(Est Delivery by <span v-html="item.guaranteedDeliveryDate"></span>)</small></label>
      </p>
      <FenixBranding v-if="fenixDataReceived_other" :fenixutm="fenixutm" />
    </div>
  </div>
<div v-else class="d-flex">
 <LoadingFallback v-if="fenixDataReceived_other"/>
</div>
</template>

<script>
import axios from 'axios';
import Cookies from 'js-cookie';
import LoadingFallback from '@/components/LoadingFallback/LoadingFallback.vue';
import FenixBranding from '@/components/Fenix/FenixBranding.vue';
export default {
  name: 'FenixCheckout',
  props: {
    lineItems: [Object, Number, String],
  },
  components: {
    LoadingFallback,
    FenixBranding
  },
  data() {
    return {
      fenixCallback: 0,
      fenixDataReceived: false,
      fenixDataReceived_other: true,
      fenixutm: '?utm_source=AWS&utm_medium=Demo_store&utm_campaign=checkout_Page',
      fenixResponse: "",
      fenixCartItems : this.lineItems.items,
      tenantId: import.meta.env.VITE_FENIX_TENANT_ID,
      xapikey: import.meta.env.VITE_FENIX_X_API_KEY,
      fenixSSIDCookie: Cookies.get('fenixSSID'),
      endPointUrl: import.meta.env.VITE_FENIX_EDD_ENDPOINT,
      requestData: {
        sessionTrackId: this.fenixSSIDCookie || '',
        fenixSSID: this.fenixSSIDCookie || '',
        buyerZipCode: Cookies.get('fenixlocation') || '',
        monetaryValue: import.meta.env.VITE_FENIX_MONETARY_VALUE,
        pageType: 'COP',
        responseFormat: 'json',
        skus: [],
      },
    };
  },
  methods: {
    // Fenix delivery estimates call.
    getEstimates() {
      this.fenixCallback++;
      const requiredobject = [];
      this.fenixCartItems.forEach((items) => {
        const onemoreobject = {};
        onemoreobject.sku = items.product_id;
        onemoreobject.quantity = items.quantity;
        onemoreobject.skuInventories = [];

        const secondobj = {};
        secondobj.locationId = 'manual';
        secondobj.quantity = items.quantity;
        onemoreobject.skuInventories.push(secondobj);
        requiredobject.push(onemoreobject); // Push in required object
      });

      this.requestData.skus = requiredobject;
      const headers = {
        tenantId: this.tenantId,
        'x-api-key': this.xapikey,
        'Content-Type': 'application/json',
      };

      axios.post(this.endPointUrl, this.requestData, {
        headers,
      })
        .then((response) => response)
        .then((result) => {
          this.fenixdata = result.data;
          this.invalidZip = false;
          this.fenixDataReceived_other = true;
          if (result.data[0].response !== undefined && result.data[0].response !== '') {
            this.fenixResponse = result.data;
            this.fenixDataReceived = true;
          }
        })
        .catch(() => {
          if(this.fenixCallback<2){
            this.fenixDataReceived_other = true;
            this.requestData.buyerZipCode = 10001;
            Cookies.set('fenixlocation', 10001, { expires: 14 });
            this.getEstimates();
          }
          this.fenixDataReceived_other = false;
          this.fenixDataReceived = false;
        });
    },
  },
  mounted() {
    this.getEstimates();
  },
};
</script>


<style scoped>
.delivery-name{
  display: inline-block;
  width: 200px;
}
.fenix-product-delivery-estimates{
  padding: 2rem;
  border: 1px solid var(--grey-300);
  border-radius: 2px;
  margin-bottom: 1rem;
}

.text-right{
  text-align: right;
}
</style>