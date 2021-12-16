<template>
  <Layout :show-demo-guide="false">
    <div class="container">
      <div class="row">
        <div class="col">
          <h2>
            Outfit Builder
          </h2>
        </div>
      </div>
      <LoadingFallback v-if="!product"/>
      <div v-else class="row mb-4">
        <div class="col-12 col-sm-3">
          <Product :product="this.product" feature="outfit_builder"/>
        </div>
        <div class="col text-left d-flex">
          <div class="my-auto">
            <div v-if="isValidProduct">
              <p>
                Building a personalized outfit based around <span class="font-weight-bold">{{
                  this.product.name
                }}</span>
              </p>
              <p>
                Choose from the suggested products to put together an outfit, then click 'Try on' to have the items
                delivered to the fitting room by a store assistant.
              </p>
            </div>
            <div v-else>
              <p>
                Outfit builder is only available for clothing items.
              </p>
            </div>
          </div>
        </div>
      </div>
      <div v-if="isValidProduct">
        <RecommendedProductsSection
            :recommendedProducts="recommendedJackets"
            feature="FEATURE"
            class="mt-4"
            @productClick="(e, product) => onProductClick(e, product, 'jacket')"
            v-if="!selectedJacket && baseProductType !== 'jacket'"
        >
          <template #heading>
            Select a jacket
          </template>
        </RecommendedProductsSection>
        <RecommendedProductsSection
            :recommendedProducts="recommendedShirts"
            feature="FEATURE"
            class="mt-4"
            @productClick="(e, product) => onProductClick(e, product, 'shirt')"
            v-if="!selectedShirt && baseProductType !== 'shirt'"
        >
          <template #heading>
            Select a shirt
          </template>
        </RecommendedProductsSection>
        <RecommendedProductsSection
            :recommendedProducts="recommendedAccessories"
            feature="FEATURE"
            class="mt-4"
            @productClick="(e, product) => onProductClick(e, product, 'accessories')"
            v-if="!selectedAccessory && baseProductType !== 'accessories'"
        >
          <template #heading>
            Select an accessory
          </template>
        </RecommendedProductsSection>
        <RecommendedProductsSection
            :recommendedProducts="this.recommendedFootwear"
            feature="FEATURE"
            class="mt-4"
            @productClick="(e, product) => onProductClick(e, product, 'footwear')"
            v-if="!selectedFootwear && baseProductType !== 'footwear'"
        >
          <template #heading>
            Select some footwear
          </template>
        </RecommendedProductsSection>
        <div class="row mb-4">
          <div class="col-12">
            <h3>
              Selected outfit
            </h3>
          </div>
          <div v-for="prod in selectedOutfit" class="col-6 col-xs-4 col-md-3" v-bind:key="prod.id">
            <Product class="mb-3" feature="" :product="prod" @click="e => e.preventDefault()"/>
          </div>
        </div>
        <div class="row" v-if="isValidProduct">
          <div class="col">
            <button class="btn btn-primary" @click="onTryOnClick" :disabled="!tryOnReady">
              Try on
            </button>
          </div>
        </div>
      </div>
    </div>
  </Layout>
</template>

<script>
import Layout from "@/components/Layout/Layout";
import {RepositoryFactory} from "@/repositories/RepositoryFactory";
import Product from "@/components/Product/Product";
import {mapActions, mapGetters, mapState} from "vuex";
import RecommendedProductsSection from "@/components/RecommendedProductsSection/RecommendedProductsSection";
import LoadingFallback from "@/components/LoadingFallback/LoadingFallback";

const ProductsRepository = RepositoryFactory.get('products');
const RecommendationsRepository = RepositoryFactory.get('recommendations');

export default {
  name: "OutfitBuilder",
  components: {LoadingFallback, RecommendedProductsSection, Product, Layout},
  data() {
    return {
      allProducts: [],
      product: null,
      recommendedJackets: null,
      selectedJacket: null,
      recommendedShirts: null,
      selectedShirt: null,
      recommendedAccessories: null,
      selectedAccessory: null,
      recommendedFootwear: null,
      selectedFootwear: null,
    }
  },
  created() {
    this.fetchData()
  },
  methods: {
    ...mapActions(['openClientelingModal']),
    fetchData() {
      this.fetchProduct().then(this.fetchRecommendedProducts)
    },
    async fetchProduct() {
      let {data: product} = await ProductsRepository.getProduct(this.productId)
      this.product = product
    },
    onTryOnClick() {
      console.log('click')
      this.openClientelingModal({name: 'outfit-builder-complete'})
    },
    async fetchRecommendedProducts() {
      ProductsRepository.getProductsByCategory('apparel').then(async (response) => {
        let products = response.data

        // Rerank jackets
        let jackets = products.filter(p => p.gender_affinity === this.user.gender && p.style === 'jacket')
        this.rerankProducts(jackets).then((resp) => {
          this.recommendedJackets = resp.map((product) => {
            return {product: product}
          })
        })

        // Rerank shirts
        let shirts = products.filter(p => p.gender_affinity === this.user.gender && p.style === 'shirt')
        this.rerankProducts(shirts).then((resp) => {
          this.recommendedShirts = resp.map((product) => {
            return {product: product}
          })
        })
      })

      ProductsRepository.getProductsByCategory('accessories').then(async (response) => {
        let products = response.data

        // Rerank accessories
        let accessories = products.filter(p => p.gender_affinity === this.user.gender)
        this.rerankProducts(accessories).then((resp) => {
          this.recommendedAccessories = resp.map((product) => {
            return {product: product}
          })
        })
      })

      ProductsRepository.getProductsByCategory('footwear').then(async (response) => {
        let products = response.data
        let footwear = products.filter(p => p.gender_affinity === this.user.gender)
        this.rerankProducts(footwear).then((resp) => {
          this.recommendedFootwear = resp.map((product) => {
            return {product: product}
          })
        })
      })
    },
    async rerankProducts(products) {
      let {data} = await RecommendationsRepository.getRerankedItems(this.personalizeUserID, products, 'outfit_builder')
      return data
    },
    onProductClick(e, product, selectionType) {
      e.preventDefault()
      this.selectProduct(product, selectionType)
    },
    selectProduct(product, selectionType) {
      if (selectionType === 'jacket') {
        this.selectedJacket = product
      } else if (selectionType === 'shirt') {
        this.selectedShirt = product
      } else if (selectionType === 'accessories') {
        this.selectedAccessory = product
      } else if (selectionType === 'footwear') {
        this.selectedFootwear = product
      }
    }
  },
  computed: {
    ...mapState(['user']),
    ...mapGetters(['personalizeUserID']),
    baseProductType() {
      let categories = ['accessories', 'footwear']
      let styles = ['jacket', 'shirt']
      if (categories.includes(this.product?.category)) {
        return this.product.category
      } else if (styles.includes(this.product?.style)) {
        return this.product.style
      }
      return null
    },
    productId() {
      return this.$route.params.productId
    },
    isValidProduct() {
      return !!this.baseProductType
    },
    tryOnReady() {
      return !!this.selectedJacket && !!this.selectedShirt && !!this.selectedAccessory && !!this.selectedFootwear
    },
    selectedOutfit() {
      return [this.selectedJacket, this.selectedShirt, this.selectedAccessory, this.selectedFootwear].filter(x => !!x)
    },
  },
  watch: {
    productId: function () {
      this.fetchData();
    },
    product: function () {
      this.selectProduct(this.product, this.baseProductType)
    }
  }
}
</script>

<style scoped>

</style>