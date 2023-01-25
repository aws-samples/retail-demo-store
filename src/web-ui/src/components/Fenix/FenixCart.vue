<template id="js-fenix-template">
  <div id="fenix-div" v-if="fenixDataReceived">
    <div class="fenix-product-delivery-estimates">
      <span class="fenix-truck">
        <svg class="card-truck" width="24" height="18" viewBox="0 0 24 18" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M22.4394 5.69627C22.2092 5.20095 21.8533 4.78434 21.4122 4.49369C20.971 4.20304 20.4623 4.05 19.9437 4.05193H15.9807V0.872088C15.9807 0.801317 15.9676 0.731238 15.9422 0.665856C15.9168 0.600474 15.8795 0.541068 15.8326 0.491031C15.7856 0.440994 15.7299 0.401307 15.6685 0.374235C15.6072 0.347163 15.5414 0.333238 15.475 0.333253H3.16636C3.09988 0.333091 3.03402 0.346908 2.97255 0.373914C2.91109 0.40092 2.85522 0.440585 2.80816 0.490637C2.76109 0.540689 2.72375 0.600144 2.69828 0.6656C2.6728 0.731055 2.65969 0.801225 2.65969 0.87209C2.65969 0.942955 2.6728 1.01312 2.69828 1.07858C2.72375 1.14404 2.76109 1.20349 2.80816 1.25354C2.85522 1.30359 2.91109 1.34326 2.97255 1.37027C3.03402 1.39727 3.09988 1.41109 3.16636 1.41093H14.9694V14.3095H9.77285C9.65579 13.6676 9.33291 13.0892 8.85957 12.6733C8.38623 12.2574 7.79191 12.0299 7.17849 12.0299C6.56506 12.0299 5.97074 12.2574 5.4974 12.6733C5.02406 13.0892 4.70119 13.6676 4.58412 14.3095H2.90029C2.83381 14.3093 2.76795 14.3231 2.70648 14.3501C2.64502 14.3772 2.58915 14.4168 2.54209 14.4669C2.49502 14.5169 2.45768 14.5764 2.43221 14.6418C2.40673 14.7073 2.39362 14.7775 2.39362 14.8483C2.39362 14.9192 2.40673 14.9894 2.43221 15.0548C2.45768 15.1203 2.49502 15.1797 2.54209 15.2298C2.58915 15.2798 2.64502 15.3195 2.70648 15.3465C2.76795 15.3735 2.83381 15.3873 2.90029 15.3872H4.58412C4.70122 16.029 5.0241 16.6074 5.49744 17.0233C5.97077 17.4392 6.56508 17.6666 7.17849 17.6666C7.79189 17.6666 8.3862 17.4392 8.85953 17.0233C9.33287 16.6074 9.65576 16.029 9.77285 15.3872H16.6218C16.7389 16.029 17.0618 16.6074 17.5351 17.0233C18.0085 17.4392 18.6028 17.6666 19.2162 17.6666C19.8296 17.6666 20.4239 17.4392 20.8972 17.0233C21.3705 16.6074 21.6934 16.029 21.8105 15.3872H23.4944C23.5608 15.3872 23.6265 15.3732 23.6878 15.3462C23.7492 15.3191 23.8049 15.2794 23.8519 15.2294C23.8988 15.1793 23.9361 15.1199 23.9615 15.0546C23.9869 14.9892 24 14.9191 24 14.8483V9.14962C23.9999 9.06596 23.9816 8.98346 23.9465 8.90866L22.4394 5.69627ZM7.17849 16.5889C6.8555 16.589 6.53975 16.4869 6.27118 16.2957C6.0026 16.1044 5.79326 15.8326 5.66964 15.5145C5.54601 15.1964 5.51365 14.8464 5.57664 14.5088C5.63963 14.1711 5.79515 13.8609 6.02353 13.6175C6.2519 13.374 6.54288 13.2082 6.85966 13.141C7.17645 13.0739 7.5048 13.1083 7.8032 13.2401C8.10161 13.3718 8.35666 13.595 8.53609 13.8812C8.71553 14.1675 8.8113 14.504 8.81129 14.8483C8.8108 15.3098 8.63862 15.7522 8.33252 16.0785C8.02642 16.4048 7.61139 16.5884 7.17849 16.5889ZM19.9437 5.12962C20.2744 5.12839 20.5988 5.22596 20.8801 5.41128C21.1614 5.59659 21.3883 5.86223 21.5352 6.17805L22.9887 9.27688V9.64732H15.9807V5.12962H19.9437ZM19.2162 16.5889C18.8932 16.589 18.5774 16.4869 18.3089 16.2957C18.0403 16.1044 17.8309 15.8326 17.7073 15.5145C17.5837 15.1964 17.5513 14.8464 17.6143 14.5088C17.6773 14.1711 17.8328 13.8609 18.0612 13.6175C18.2896 13.374 18.5806 13.2082 18.8973 13.141C19.2141 13.0739 19.5425 13.1083 19.8409 13.2401C20.1393 13.3718 20.3943 13.595 20.5738 13.8812C20.7532 14.1675 20.849 14.504 20.849 14.8483C20.8485 15.3098 20.6763 15.7522 20.3702 16.0785C20.0641 16.4048 19.6491 16.5884 19.2162 16.5889ZM21.8105 14.3095C21.6935 13.6676 21.3706 13.0892 20.8973 12.6733C20.4239 12.2574 19.8296 12.0299 19.2162 12.0299C18.6027 12.0299 18.0084 12.2574 17.5351 12.6733C17.0617 13.0892 16.7389 13.6676 16.6218 14.3095H15.9807V10.725H22.9887V14.3095H21.8105ZM1.92902 4.44411H9.16389C9.23037 4.44395 9.29623 4.45777 9.3577 4.48477C9.41916 4.51178 9.47503 4.55144 9.52209 4.6015C9.56916 4.65155 9.6065 4.711 9.63197 4.77646C9.65745 4.84191 9.67056 4.91208 9.67056 4.98295C9.67056 5.05382 9.65745 5.12398 9.63197 5.18944C9.6065 5.2549 9.56916 5.31435 9.52209 5.3644C9.47503 5.41445 9.41916 5.45412 9.3577 5.48113C9.29623 5.50813 9.23037 5.52195 9.16389 5.52179H1.92902C1.86254 5.52195 1.79668 5.50813 1.73521 5.48113C1.67375 5.45412 1.61788 5.41445 1.57082 5.3644C1.52376 5.31435 1.48642 5.2549 1.46094 5.18944C1.43546 5.12398 1.42235 5.05382 1.42235 4.98295C1.42235 4.91208 1.43546 4.84191 1.46094 4.77646C1.48642 4.711 1.52376 4.65155 1.57082 4.6015C1.61788 4.55144 1.67375 4.51178 1.73521 4.48477C1.79668 4.45777 1.86254 4.44395 1.92902 4.44411ZM0 8.79289C2.80023e-06 8.72212 0.0130845 8.65204 0.0384979 8.58666C0.0639113 8.52127 0.101159 8.46187 0.148113 8.41183C0.195067 8.3618 0.250808 8.32211 0.312153 8.29504C0.373498 8.26797 0.439246 8.25404 0.50564 8.25406H6.76925C6.83573 8.25389 6.90159 8.26771 6.96305 8.29472C7.02452 8.32172 7.08038 8.36139 7.12745 8.41144C7.17451 8.46149 7.21185 8.52095 7.23733 8.5864C7.2628 8.65186 7.27592 8.72203 7.27592 8.79289C7.27592 8.86376 7.2628 8.93393 7.23733 8.99938C7.21185 9.06484 7.17451 9.12429 7.12745 9.17435C7.08038 9.2244 7.02452 9.26406 6.96305 9.29107C6.90159 9.31807 6.83573 9.33189 6.76925 9.33173H0.50564C0.439245 9.33175 0.373497 9.31782 0.312151 9.29075C0.250806 9.26367 0.195064 9.22399 0.14811 9.17395C0.101156 9.12391 0.0639085 9.0645 0.0384955 8.99912C0.0130826 8.93374 1.74955e-06 8.86366 0 8.79289Z" fill="black"/></svg>
        <span v-html="fenixResponse"></span>
      </span>
      <FenixBranding v-if="fenixDataReceived_other" :fenixutm="fenixutm" />
    </div>
  </div>
<div v-else>
  <div class="fenix-product-delivery-estimates" v-if="fenixDataReceived_other">
    <LoadingFallback/>
  </div>
</div>
</template>
<script>
import axios from 'axios';
import Cookies from 'js-cookie';
import LoadingFallback from '@/components/LoadingFallback/LoadingFallback.vue';
import FenixBranding from '@/components/Fenix/FenixBranding.vue';

export default {
  name: 'FenixCart',
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
      fenixutm: '?utm_source=AWS&utm_medium=Demo_store&utm_campaign=cart_Page',
      fenixResponse: "Getting Delivery estimates...",
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
        pageType: 'CART',
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
          this.fenixDataReceived = true;
          this.fenixDataReceived_other = true;
          this.fenixdata = result.data;
          this.invalidZip = false;
          if (result.data[0].response !== undefined && result.data[0].response !== '') {
            this.fenixResponse = result.data[0].response;
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
.fenix-product-delivery-estimates{
  padding: 2rem;
  border: 1px solid var(--grey-300);
  border-radius: 2px;
  margin-bottom: 1rem;
}
</style>