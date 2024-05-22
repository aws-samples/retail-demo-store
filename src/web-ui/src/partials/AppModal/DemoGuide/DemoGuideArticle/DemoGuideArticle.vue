<template>
  <component :is="articleComponent"></component>
</template>

<script>
import { Articles } from '../config';
import UserPersonalization from './articles/UserPersonalization.vue';
import SIMSRecommendations from './articles/SIMSRecommendations.vue';
import SimilarItemsRecommendations from './articles/SimilarItemsRecommendations.vue';
import SimilarItemsWithTheme from './articles/SimilarItemsWithTheme.vue';
import PersonalizedRanking from './articles/PersonalizedRanking.vue';
import CustomersWhoViewedXAlsoViewed from './articles/CustomersWhoViewedXAlsoViewed.vue';
import FrequentlyBoughtTogether from './articles/FrequentlyBoughtTogether.vue';
import PopularByPurchases from './articles/PopularByPurchases.vue';
import PopularByViews from './articles/PopularByViews.vue';
import RecommendedForYou from './articles/RecommendedForYou.vue';
import MachineLearningUserSegmentation from './articles/MachineLearningUserSegmentation.vue';
import PersonalizedEmails from './articles/PersonalizedEmails.vue';
import TextMessaging from './articles/TextMessaging.vue';
import OmniChannel from './articles/OmniChannel.vue';
import UserSegmentation from './articles/UserSegmentation.vue';
import RightForYou from './articles/RightForYou.vue';
import DataToProvide from './articles/DataToProvide.vue';
import MetricsAndImpact from './articles/MetricsAndImpact.vue';
import RealTimePersonalization from './articles/RealTimePersonalization.vue';
import BatchRecommendations from './articles/BatchRecommendations.vue';
import AboutThisDemo from './articles/AboutThisDemo.vue';
import Datasets from './articles/Datasets.vue';
import ShopperPersonas from './articles/ShopperPersonas.vue';
import EnablingShopperProfiles from './articles/EnablingShopperProfiles.vue';
import LocationServices from './articles/LocationServices.vue';
import PersonalizedProductDescriptions from './articles/PersonalizedProductDescriptions.vue'
import RoomGenerator from './articles/RoomGenerator.vue'

export default {
  name: 'DemoGuideArticle',
  props: {
    articleId: { type: String, required: true },
  },
  computed: {
    articleComponent() {
      switch (this.articleId) {
        case Articles.USER_PERSONALIZATION:
          return UserPersonalization;
        case Articles.SIMS_RECOMMENDATIONS:
          return SIMSRecommendations;
        case Articles.SIMILAR_ITEMS_RECOMMENDATIONS:
          return SimilarItemsRecommendations;
        case Articles.SIMILAR_ITEMS_WITH_THEME:
          return SimilarItemsWithTheme;
        case Articles.PERSONALIZED_RANKING:
          return PersonalizedRanking;
        case Articles.ECOMM_CUSTOMERS_WHO_VIEWED_X:
          return CustomersWhoViewedXAlsoViewed;
        case Articles.ECOMM_FBT:
          return FrequentlyBoughtTogether;
        case Articles.ECOMM_POPULAR_BY_PURCHASES:
          return PopularByPurchases;
        case Articles.ECOMM_POPULAR_BY_VIEWS:
          return PopularByViews;
        case Articles.ECOMM_RFY:
          return RecommendedForYou;
        case Articles.ML_USER_SEGMENTATION:
          return MachineLearningUserSegmentation;
        case Articles.USER_SEGMENTATION:
          return UserSegmentation;
        case Articles.PERSONALIZED_EMAILS:
          return PersonalizedEmails;
        case Articles.SMS_MESSAGING:
          return TextMessaging;
        case Articles.OMNI_CHANNEL:
          return OmniChannel;
        case Articles.RIGHT_FOR_YOU:
          return RightForYou;
        case Articles.DATA_TO_PROVIDE:
          return DataToProvide;
        case Articles.METRICS_AND_IMPACT:
          return MetricsAndImpact;
        case Articles.REAL_TIME_PERSONALIZATION:
          return RealTimePersonalization;
        case Articles.BATCH_RECOMMENDATIONS:
          return BatchRecommendations;
        case Articles.ABOUT_THIS_DEMO:
          return AboutThisDemo;
        case Articles.DATASETS:
          return Datasets;
        case Articles.SHOPPER_PERSONAS:
          return ShopperPersonas;
        case Articles.ENABLING_SHOPPER_PROFILES:
          return EnablingShopperProfiles
        case Articles.LOCATION_SERVICES:
          return LocationServices
        case Articles.PERSONALIZED_PRODUCT:
          return PersonalizedProductDescriptions
        case Articles.ROOM_GENERATOR:
          return RoomGenerator
      }

      throw new Error(`Invalid article id: ${this.article}`);
    },
  },
};
</script>

<style></style>
