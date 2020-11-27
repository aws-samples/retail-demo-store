<template>
  <div class="content">

    <!-- Categories Navigation -->
    <Navigation display="live" :categories="categories"/>

    <div class="container">
      <div class="row" v-if="user&&productDiscounts.length>0">
        <div class="col">
          <div class="alert alert-warning mb-2 py-1" role="alert">
            <div class="row no-gutters">
            <div class="col-11">
              <span>
                {{user ? "This page features discounts based on your past browsing with us!" : "Log in to receive personalized discounts!"}}
              </span>
            </div>
            <div class="col-1 my-auto">
              <button type="button" class="close" data-dismiss="alert" aria-label="Close">
                <span aria-hidden="true">&times;</span>
              </button>
            </div>
            </div>
          </div>
        </div>
      </div>
      <div class="row">
        <div class="col-12 col-md-8">
          <h6><i class="fas fa-circle live-icon"></i> LIVE NOW</h6>
          <div class="video-container">
            <video id="video-player" class="video-elem" playsInline muted></video>
          </div>
        </div>
        <div class="col-4 text-left d-none d-md-block">
          <h6>Featured items</h6>
            <div class="featured-products pr-1" id="featured-products-scrollable">
              <live-product v-for="product in productDetails[activeStreamId]"
                            v-bind:key="`featured-prod-${product.id}`"
                            :discount="product.discounted"
                            :active="product.id == activeProductId"
                            :experiment="product.experiment"
                            :product="product"
                            :id="`featured-prod-${product.id}`"
              />
            </div>
        </div>
      </div>
      <div class="row mt-1">

        <div v-for="(_, index) in streamDetails"
             class="col-2"
             v-bind:id="`thumb-${index}`"
             v-bind:key="`stream-${index}`"
             v-bind:class="{'d-none': index == activeStreamId}"
        >
          <div class="thumb-wrapper" v-on:click="activeStreamId = index; activeProductId = 0;">
            <div class="thumb-overlay"></div>
            <img
                type="button"
                class="channel-thumb"
                v-bind:src="streamDetails[index]['thumb_url']"
            />
          </div>
        </div>
      </div>
    </div>

    <div class="user-items my-2">
      <div class="container d-md-none">
        <div class="row">
          <div class="col text-left my-2">
            <h6>Featured item</h6>
          </div>
        </div>
        <div class="row">
          <div v-for="product in productDetails[activeStreamId]" v-bind:key="`horiz-featured-${product.id}`">
            <live-recommendation v-if="product.id == activeProductId" :product="product"/>
          </div>
        </div>
      </div>
    </div>

    <div class="related-items mb-2" >
      <div class="container py-2">
        <div class="row">
          <div class="col text-left my-2">
            <h6>Related Items</h6>
          </div>
        </div>
        <div class="row" v-if="productRecommended.length">
          <live-recommendation v-for="product in productRecommended"
                               :product="product.product"
                               :experiment="product.experiment"
                               v-bind:key="`user-recommendation-${product.product.id}`"
          />
        </div>
          <div class="row mb-4" v-if="!productRecommended.length">
            <div class="col">
              <i class="fas fa-spinner fa-spin fa-3x"></i>
            </div>
          </div>
      </div>
    </div>

    <div class="user-items">
      <div class="container py-2">
        <div class="row">
          <div class="col text-left my-2">
            <h6>{{ !!userPersonalized ? "Inspired by your shopping trends" : "Explore"}}</h6>
          </div>
        </div>
        <div class="row" v-if="user">
          <live-recommendation v-for="product in userRecommended"
                               :product="product.product"
                               :experiment="product.experiment"
                               v-bind:key="`user-recommendation-${product.product.id}`"
          />
        </div>
        <div class="row" v-if="!user">
          <live-recommendation v-for="product in guestRecommended"
                               :product="product"
                               v-bind:key="`user-recommendation-${product.id}`"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import AmplifyStore from "@/store/store";
import {RepositoryFactory} from "@/repositories/RepositoryFactory";

import Navigation from "@/public/CategoryNavigation";
import LiveProduct from "@/public/components/LiveProduct";
import LiveRecommendation from "@/public/components/LiveRecommendation";
import {AnalyticsHandler} from "@/analytics/AnalyticsHandler";

const ProductsRepository = RepositoryFactory.get('products');
const RecommendationsRepository = RepositoryFactory.get('recommendations');
const VideosRepository = RepositoryFactory.get('videos');

const MaxRecommendations = 6;
const UserExperimentFeature = 'live_stream_user_recommendation';
const ProductExperimentFeature = 'live_stream_prod_recommendation';
const ProductDiscountFeature = 'live_stream_prod_discounts';
let player = null

export default {
  name: "Live",
  components: {
    LiveProduct,
    Navigation,
    LiveRecommendation
  },
  data() {
    return {
      categories: [],
      metadata: [],
      activeStreamId: null,
      activeProductId: 0,
      streamDetails: [],
      productDetails: [],
      productDiscounts: [],
      userActiveExperiment: false,
      userPersonalized: false,
      userRecommended: [],
      guestRecommended: [],
      userExplainRecommended: '',
      productActiveExperiment: false,
      productPersonalized: false,
      productRecommended: [],
      productExplainRecommended: ''
    }
  },
  created: async function () {
     this.getStreamDetails();
     this.loadPlayer();
     this.getCategories();
     this.getRecommendations();
  },
  methods: {
    async getCategories () {
      const { data } = await ProductsRepository.getCategories();
      this.categories = data;
    },
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
      const response = await RecommendationsRepository.getRelatedProducts(this.user ? this.user.id : '', this.activeProductId, MaxRecommendations, ProductExperimentFeature);

      if (response.headers) {
        if (response.headers['x-personalize-recipe']) {
          this.productPersonalized = true;
          this.productExplainRecommended = 'Personalize recipe: ' + response.headers['x-personalize-recipe'];
        }
        if (response.headers['x-experiment-name']) {
          this.productActiveExperiment = true;
          this.productExplainRecommended = 'Active experiment: ' + response.headers['x-experiment-name'];
        }
      }

      this.productRecommended = response.data;

      if (this.productRecommended.length > 0 && 'experiment' in this.productRecommended[0]) {
        AnalyticsHandler.identifyExperiment(this.user, this.productRecommended[0].experiment);
      }
    },
    async getRecommendations() {
      if (this.user) {
        this.getUserRecommendations();
      }
      else {
        const { data } = await ProductsRepository.getFeatured();
        this.guestRecommended = data.slice(0, MaxRecommendations);
      }
    },
    async getUserRecommendations() {
      const response = await RecommendationsRepository.getRecommendationsForUser(this.user.id, '', MaxRecommendations, UserExperimentFeature);
      if (response.headers) {
        if (response.headers['x-personalize-recipe']) {
          this.userPersonalized = true;
          this.userExplainRecommended = 'Personalize recipe: ' + response.headers['x-personalize-recipe'];
        }
        if (response.headers['x-experiment-name']) {
          this.userActiveExperiment = true;
          this.userExplainRecommended = 'Active experiment: ' + response.headers['x-experiment-name'];
        }
      }

      this.userRecommended = response.data;

      if (this.userRecommended.length > 0 && 'experiment' in this.userRecommended[0]) {
        AnalyticsHandler.identifyExperiment(this.user, this.userRecommended[0].experiment);
      }
    },
    async getStreamDetails() {
      let videoResponse = await VideosRepository.get();
      this.streamDetails = videoResponse.data.streams;
      this.activeStreamId = 0;
      this.activeProductId = this.streamDetails[this.activeStreamId].products[0];
      const productDetails = this.streamDetails.map((detail) => {
        return this.getProducts(detail.products);
      })
      this.productDetails = await Promise.all(productDetails);
      const discounts = this.productDetails.map((detail) => {
        return this.getDiscounts(detail);
      })

      const discountDetails = await Promise.all(discounts)
      this.productDiscounts = discountDetails.flat().filter(discount => discount.discounted).map(disc => disc.itemId);
      if (this.productDiscounts.length>0) {
        this.productDetails = discountDetails;
      }
      else{
        console.log("No discount info.");
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
        console.log('Timed metadata: ', cue.text);
        this.handleMetadata(cue.text);
      });

      // Setup stream and play
      player.setAutoplay(true);

      player.setVolume(0.5);
    },
    handleMetadata (metadata) {
      this.activeProductId = JSON.parse(metadata).productId;

      let maxMetadata = 10;
      if (this.metadata.length >= maxMetadata) {
        this.metadata.length = maxMetadata;
      }
      this.metadata.unshift(metadata);
    }
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
  }
}
</script>

<style scoped>
.live-icon {
  color: #12e21e;
}

.related-items {
  background-color: #e5ebff;
}

.user-items {
  background-color: #f1f1f1;
}

.video-container {
  width: 100%;
  position: relative;
  padding-top: 56.25%;
  height: 0;
}

.video-elem {
  width: 100%;
  height: 100%;
  position: absolute;
  top: 0;
  left: 0;
  border-radius: 5px;
}

.featured-products {
  height: calc(100% - 1.6rem);
  overflow-y: auto;
  position: absolute;
  border-radius: 5px;
}

.channel-thumb {
  width: 100%;
  border-radius: 5px;
}

.thumb-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(196, 194, 194, 0.5);
  border-radius: 5px;
}

.thumb-wrapper {
  cursor: pointer;
  position: relative;
  width: 100%;
  font-size: 0;
}

</style>