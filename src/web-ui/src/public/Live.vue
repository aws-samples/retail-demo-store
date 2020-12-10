<template>
  <Layout>
    <div class="container">
      <div class="gridwrapper">
        <h2 class="m-0 text-left">Shop Livestreams </h2>
        <div class="d-flex align-items-end">
          <h5 class="m-0 text-left featured-heading d-none d-md-block">Featured </h5>
        </div>
        <div class="video-container">
          <video id="video-player" class="video-elem" playsInline muted></video>
        </div>

        <div class="position-relative featured-product-column d-none d-md-block">
          <div class="featured-products">
            <router-link
              v-for="product in productDetails[activeStreamId]"
              v-bind:key="`featured-prod-${product.id}`"
              :to="{
                  name: 'ProductDetail',
                  params: { id: product.id },
                  query: { exp: productActiveExperiment, feature, di: product.discounted},
                }"
              class="featured-product pt-1 pb-2 px-2 d-flex flex-column justify-content-between mb-2 mr-1"
              v-bind:class="{'active-product': product.id === activeProductId.toString()}"
            >
              <div>
                <img :src="product.image" alt="" class="mb-2 img-fluid w-100" />
                <div class="product-name">
                  {{ product.name }}
                </div>
                <div class="container">
                  <div class="row">
                    <div class="col" v-bind:class="{'discounted': product.discounted}">{{ formatPrice(product.price) }}</div>
                    <div class="col font-weight-bold" v-if="product.discounted">{{ formatPrice(discountProductPrice(product.price)) }}</div>
                  </div>
                </div>
              </div>
            </router-link>
          </div>
        </div>

        <div class="stream-selector">
          <div class="row">
            <div v-for="(_, index) in streamDetails"
                 class="col-3"
                 v-bind:id="`thumb-${index}`"
                 v-bind:key="`stream-${index}`"
                 v-bind:class="{'d-none': index === activeStreamId}"
            >
              <div class="thumb-wrapper" v-on:click="activeStreamId = index; activeProductId = 0;">
                <div class="thumb-overlay"></div>
                <img
                    class="channel-thumb"
                    v-bind:src="streamDetails[index]['thumb_url']"
                />
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="container d-md-none" >
        <div class="row mt-2">
          <div class="col pl-0 text-left">
            <h3>Featured</h3>
          </div>

        </div>
        <div class="row">
          <div class="col-6 p-0"
               v-for="product in productDetails[activeStreamId]"
               v-bind:key="`featured-prod-${product.id}`"
          >
            <router-link

                :to="{
                    name: 'ProductDetail',
                    params: { id: product.id },
                    query: { exp: productActiveExperiment, feature},
                  }"
                class="featured-product pt-1 pb-2 px-2 d-flex flex-column justify-content-between mb-2 mr-1"
                v-bind:class="{'active-product': product.id === activeProductId.toString()}"
            >
              <div>
                <img :src="product.image" alt="" class="mb-2 img-fluid w-100" />
                <div class="product-name">
                  {{ product.name }}
                </div>
                <div class="container">
                  <div class="row">
                    <div class="col" v-bind:class="{'discounted': product.discounted}">{{ formatPrice(product.price) }}</div>
                    <div class="col font-weight-bold" v-if="product.discounted">{{ formatPrice(discountProductPrice(product.price)) }}</div>
                  </div>
                </div>
              </div>
            </router-link>
          </div>
        </div>
      </div>

      <RecommendedProductsSection
          :key="`rec-products-${(new Date()).getTime()}`"
          :explainRecommended="explainRecommended"
          :recommendedProducts="productRecommended"
          :feature="feature"
          class="mt-4"
      >
        <template #heading>Compare similar items</template>
      </RecommendedProductsSection>

    </div>
  </Layout>
</template>

<script>
import AmplifyStore from "@/store/store";
import {RepositoryFactory} from "@/repositories/RepositoryFactory";

import Layout from "@/components/Layout/Layout";
import RecommendedProductsSection from "@/components/RecommendedProductsSection/RecommendedProductsSection";
import {AnalyticsHandler} from "@/analytics/AnalyticsHandler";
import {formatPrice} from "@/util/formatPrice";
import {discountProductPrice} from "@/util/discountProductPrice";

const ProductsRepository = RepositoryFactory.get('products');
const RecommendationsRepository = RepositoryFactory.get('recommendations');
const VideosRepository = RepositoryFactory.get('videos');

const MAX_RECOMMENDATIONS = 6;
const PRODUCT_EXPERIMENT_FEATURE = 'live_stream_prod_recommendation';
const ProductDiscountFeature = 'live_stream_prod_discounts';

let player = null

export default {
  name: "Live",
  components: {
    Layout,
    RecommendedProductsSection,
  },
  data() {
    return {
      streamDetails: [],
      activeStreamId: 0,
      productDetails: [],
      activeProductId: 0,
      productRecommended: null,
      explainRecommended: null,
      productActiveExperiment: false,
      feature: PRODUCT_EXPERIMENT_FEATURE,
      metadata: [],
      productDiscounts: [],
    }
  },
  created: async function () {
     this.loadPlayer();
  },
  methods: {
    async getProducts (productIds) {
      let products = [];
      for (const product of productIds) {
        try {
          let {data} = await ProductsRepository.getProduct(product);
          data["itemId"] = data["id"];
          products.push(data);
        } catch (e) {
          console.log(e)
        }
      }
      return products;
    },
    async getDiscounts (products) {
      let { data } = await RecommendationsRepository.chooseDiscounts(this.user ? this.user.id : '', products, ProductDiscountFeature);
      return data;
    },
    async getRelatedProducts() {
      this.explainRecommended = null;
      this.productRecommended = null;

      const response = await RecommendationsRepository.getRelatedProducts(
          this.personalizeUserID ?? '',
          this.activeProductId,
          MAX_RECOMMENDATIONS,
          PRODUCT_EXPERIMENT_FEATURE,
      );

      if (response.headers) {
        const experimentName = response.headers['x-experiment-name'];
        const personalizeRecipe = response.headers['x-personalize-recipe'];

        if (experimentName || personalizeRecipe) {
          const explanation = experimentName
              ? `Active experiment: ${experimentName}`
              : `Personalize recipe: ${personalizeRecipe}`;

          this.explainRecommended = {
            activeExperiment: !!experimentName,
            personalized: !!personalizeRecipe,
            explanation,
          };
        }
      }

      this.productRecommended = response.data;

      if (this.productRecommended.length > 0 && 'experiment' in this.productRecommended[0]) {
        AnalyticsHandler.identifyExperiment(this.user, this.productRecommended[0].experiment);
      }
    },
    async loadPlayer () {
      const mediaPlayerScript = document.createElement("script");
      mediaPlayerScript.src = "https://player.live-video.net/1.0.0/amazon-ivs-player.min.js";
      mediaPlayerScript.async = true;
      document.body.appendChild(mediaPlayerScript);
      mediaPlayerScript.onload = () => this.mediaPlayerScriptLoaded();
    },
    async mediaPlayerScriptLoaded () {
      const MediaPlayerPackage = window.IVSPlayer;

      // First, check if the browser supports the Amazon IVS player.
      if (!MediaPlayerPackage.isPlayerSupported) {
        console.warn("The current browser does not support the Amazon IVS player.");
        return;
      }

      const PlayerState = MediaPlayerPackage.PlayerState;
      const PlayerEventType = MediaPlayerPackage.PlayerEventType;

      // Initialize player
      player = MediaPlayerPackage.create();
      player.attachHTMLVideoElement(document.getElementById("video-player"));

      // Attach event listeners
      player.addEventListener(PlayerState.PLAYING, () => {
        console.log("Player State - PLAYING");
      });
      player.addEventListener(PlayerState.ENDED, () => {
        console.log("Player State - ENDED");
      });
      player.addEventListener(PlayerState.READY, () => {
        console.log("Player State - READY");
      });
      player.addEventListener(PlayerEventType.ERROR, (err) => {
        console.warn("Player Event - ERROR:", err);
      });
      player.addEventListener(PlayerEventType.TEXT_METADATA_CUE, (cue) => {
        console.log(cue)
        this.handleMetadata(cue.text);
      });

      // Setup stream and play
      let videoResponse = await VideosRepository.get();
      this.streamDetails = videoResponse.data.streams;
      this.activeProductId = this.streamDetails[this.activeStreamId].products[0]
      player.setAutoplay(true);
      player.setVolume(0.5);
      player.load(this.streamDetails[this.activeStreamId].playback_url);

      const productDetails = this.streamDetails.map((detail) => {
        return this.getProducts(detail.products);
      })
      this.productDetails = await Promise.all(productDetails);

      const discounts = this.productDetails.map((detail) => {
        return this.getDiscounts(detail);
      })
      const discountDetails = await Promise.all(discounts)

      this.productDiscounts = discountDetails.flat().filter(discount => discount.discounted).map(disc => disc.itemId);
      if (this.productDiscounts.length > 0) {
        this.productDetails = discountDetails;
      }
      else {
        console.log("No discount info.");
      }
    },
    handleMetadata (metadata) {
      this.activeProductId = JSON.parse(metadata).productId;

      let maxMetadata = 10;
      if (this.metadata.length >= maxMetadata) {
        this.metadata.length = maxMetadata;
      }
      this.metadata.unshift(metadata);
    },
    formatPrice,
    discountProductPrice
  },
  computed: {
    user() {
      return AmplifyStore.state.user;
    },
  },
  watch: {
    activeStreamId: function (id) {
      player.load(this.streamDetails[id].playback_url);
      this.activeProductId = this.streamDetails[this.activeStreamId].products[0]
    },
    activeProductId: function (id) {
      this.getRelatedProducts();
      const featuredProductElement = document.getElementById(`featured-prod-${id}`);
      if (featuredProductElement) {
        document.getElementById('featured-products-scrollable').scrollTop = featuredProductElement.offsetTop;
      }
    },
    personalizeUserID() {
      this.getRelatedProducts()
    }
  }
}
</script>

<style scoped>
.gridwrapper {
  display: grid;
  grid-template-columns: 1.6fr 0.4fr;
  grid-auto-rows: auto auto 1fr;
  grid-gap: 10px;
}

.featured-product-column {
  grid-area: 2 / 2 / 4 / 3;
}

.featured-products {
  position:absolute;
  overflow-y: auto;
  top:0;
  bottom:0;
  left:0;
  right:0;
}

.video-container {
  width: 100%;
  position: relative;
  padding-top: 56.25%;
  height: 0;
  grid-area: 2 / 1 / 3 / 3;
}

.stream-selector {
  grid-area: 3 / 1 / 4 / 3;
}

@media (min-width: 768px) {
  .video-container {
    grid-area: 2 / 1 / 3 / 2;
  }

  .stream-selector {
    grid-area: 3 / 1 / 4 / 2;
  }
}

.video-elem {
  width: 100%;
  height: 100%;
  position: absolute;
  top: 0;
  left: 0;
}

.channel-thumb {
  width: 100%;
}

.thumb-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(196, 194, 194, 0.5);
}

.thumb-wrapper {
  cursor: pointer;
  position: relative;
  width: 100%;
  font-size: 0;
}

.active-product {
  background-color: #00a1c991;
}

.featured-product {
  border: 1px solid var(--grey-500);
  text-decoration: none;
  color: inherit;
}

.discounted {
  text-decoration: line-through;
  color: red;
}

</style>