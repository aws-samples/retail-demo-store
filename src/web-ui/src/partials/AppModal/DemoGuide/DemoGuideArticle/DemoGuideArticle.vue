<template>
  <component :is="articleComponent"></component>
</template>

<script>
import { Articles } from '../config';
import UserPersonalization from './articles/UserPersonalization';
import SIMSRecommendations from './articles/SIMSRecommendations';
import SimilarItemsRecommendations from './articles/SimilarItemsRecommendations';
import PersonalizedRanking from './articles/PersonalizedRanking';
import CustomersWhoViewedXAlsoViewed from './articles/CustomersWhoViewedXAlsoViewed';
import FrequentlyBoughtTogether from './articles/FrequentlyBoughtTogether';
import PopularByPurchases from './articles/PopularByPurchases';
import PopularByViews from './articles/PopularByViews';
import RecommendedForYou from './articles/RecommendedForYou';
import MachineLearningUserSegmentation from './articles/MachineLearningUserSegmentation';
import PersonalizedEmails from './articles/PersonalizedEmails';
import TextMessaging from './articles/TextMessaging';
import OmniChannel from './articles/OmniChannel';
import UserSegmentation from './articles/UserSegmentation';
import RightForYou from './articles/RightForYou';
import DataToProvide from './articles/DataToProvide';
import MetricsAndImpact from './articles/MetricsAndImpact';
import RealTimePersonalization from './articles/RealTimePersonalization';
import BatchRecommendations from './articles/BatchRecommendations';
import AboutThisDemo from './articles/AboutThisDemo';
import Datasets from './articles/Datasets';
import ShopperPersonas from './articles/ShopperPersonas';
import EnablingShopperProfiles from './articles/EnablingShopperProfiles';
import LocationServices from './articles/LocationServices';

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
      }

      throw new Error(`Invalid article id: ${this.article}`);
    },
  },
};
</script>

<style></style>
