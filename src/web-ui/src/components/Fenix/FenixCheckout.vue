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
    </div>
  </div>
<div v-else class="d-flex">
 <LoadingFallback v-if="fenixLoader" />
</div>
</template>

<script>
import axios from 'axios';
import Cookies from 'js-cookie';
import LoadingFallback from '@/components/LoadingFallback/LoadingFallback';

export default {
  name: 'FenixCheckout',
  props: {
    lineItems: [Object, Number, String],
  },
  components: {
    LoadingFallback,
  },
  data() {
    return {
      fenixDataReceived: false,
      fenixLoader: true,
      fenixResponse: "Getting Delivery estimates...",
      fenixCartItems : this.lineItems.items,
      tenantId: process.env.VUE_APP_FENIX_TENANT_ID,
      fenixSSIDCookie: Cookies.get('fenixSSID'),
      endPointUrl: process.env.VUE_APP_FENIX_EDD_ENDPOINT,
      requestData: {
        sessionTrackId: this.fenixSSIDCookie || '',
        fenixSSID: this.fenixSSIDCookie || '',
        buyerZipCode: Cookies.get('fenixlocation') || 1000,
        monetaryValue: process.env.VUE_APP_FENIX_MONETARY_VALUE,
        pageType: 'COP',
        responseFormat: 'json',
        skus: [],
      },
    };
  },
  methods: {
    // Get IP address and zip code from IPAPI.
    getlocation() {
      axios.get(this.ipinfoUrl)
        .then((data) => {
          if (data.data.postal) {
            Cookies.set('fenixlocation', data.data.postal, { expires: 14 });
            this.requestData.buyerZipCode = data.data.postal;
            this.getEstimates();
          }
        });
    },
    // Fenix delivery estimates call.
    getEstimates() {
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
        'Content-Type': 'application/json',
      };

      axios.post(this.endPointUrl, this.requestData, {
        headers,
      })
        .then((response) => response)
        .then((result) => {
          this.fenixdata = result.data;
          this.invalidZip = false;
          if (result.data[0].response !== undefined && result.data[0].response !== '') {
            this.fenixResponse = result.data;
            console.log(this.fenixResponse);
            this.fenixDataReceived = true;
          }
        })
        .catch(() => {
          this.fenixDataReceived = false;
          this.fenixLoader = false;
        });
    },
  },
  beforeMount() {
    if (this.requestData.buyerZipCode === undefined
        || this.requestData.buyerZipCode === null
        || this.requestData.buyerZipCode === '') {
      this.getlocation();
    }else{
      this.getEstimates()
    }
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