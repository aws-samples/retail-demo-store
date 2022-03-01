export const DEMO_GUIDE_TITLE_ID = 'demo-guide-title';

export const Sections = {
  USE_CASES: 'use-cases',
  PERSONALIZE_USEFUL_TOPICS: 'personalize-useful-topics',
  ABOUT_THIS_DEMO: 'about-this-demo',
};

export const sectionHeadings = {
  [Sections.USE_CASES]: 'Use cases enabled in this demo',
  [Sections.PERSONALIZE_USEFUL_TOPICS]: 'Amazon Personalize Useful Topics',
  [Sections.ABOUT_THIS_DEMO]: 'About This Demo',
};

export const Articles = {
  USER_PERSONALIZATION: 'user-personalization',
  SIMS_RECOMMENDATIONS: 'sims-recommendations',
  SIMILAR_ITEMS_RECOMMENDATIONS: 'similar-items-recommendations',
  PERSONALIZED_RANKING: 'personalized-ranking',
  USER_SEGMENTATION: 'user-segmentation',
  ECOMM_CUSTOMERS_WHO_VIEWED_X: 'customers-who-viewed-x-also-viewed',
  ECOMM_FBT: 'frequently-bought-together',
  ECOMM_POPULAR_BY_PURCHASES: 'popular-items-by-purchases',
  ECOMM_POPULAR_BY_VIEWS: 'popular-items-by-views',
  ECOMM_RFY: 'recommended-for-you',
  ML_USER_SEGMENTATION: 'ml-user-segmentation',
  PERSONALIZED_EMAILS: 'personalized-emails',
  SMS_MESSAGING: 'text-messaging',
  OMNI_CHANNEL: 'omni-channel',
  RIGHT_FOR_YOU: 'right-for-you',
  DATA_TO_PROVIDE: 'data-to-provide',
  METRICS_AND_IMPACT: 'metrics-and-impact',
  REAL_TIME_PERSONALIZATION: 'real-time-personalization',
  BATCH_RECOMMENDATIONS: 'batch-recommendations',
  ABOUT_THIS_DEMO: 'about-this-demo-article',
  DATASETS: 'datasets',
  SHOPPER_PERSONAS: 'shopper-personas',
  ENABLING_SHOPPER_PROFILES: 'enabling-shopper-profiles',
  LOCATION_SERVICES: 'location-services'
};

export const articleTitles = {
  [Articles.USER_PERSONALIZATION]: 'User Personalization',
  [Articles.SIMS_RECOMMENDATIONS]: 'Similar Item (SIMS) Recommendations',
  [Articles.SIMILAR_ITEMS_RECOMMENDATIONS]: 'Similar Items Recommendations',
  [Articles.PERSONALIZED_RANKING]: 'Personalized Ranking',
  [Articles.ECOMM_CUSTOMERS_WHO_VIEWED_X]: 'Customers Who Viewed X Also Viewed',
  [Articles.ECOMM_FBT]: 'Frequently Bought Together',
  [Articles.ECOMM_POPULAR_BY_PURCHASES]: 'Best Sellers',
  [Articles.ECOMM_POPULAR_BY_VIEWS]: 'Most Viewed',
  [Articles.ECOMM_RFY]: 'Recommended For You',
  [Articles.ML_USER_SEGMENTATION]: 'Machine-Learning User Segmentation',
  [Articles.USER_SEGMENTATION]: 'Real-Time User Segmentation',
  [Articles.PERSONALIZED_EMAILS]: 'Personalize Emails: Welcome and Abandoned Cart',
  [Articles.SMS_MESSAGING]: 'Text Messaging (SMS): Personalized Alerts and Promotions',
  [Articles.OMNI_CHANNEL]: 'Omni-Channel Personalization & ML Model Retraining',
  [Articles.LOCATION_SERVICES]: 'Retail Geofencing and Location-aware Personalization',
  [Articles.RIGHT_FOR_YOU]: 'Find out why Amazon Personalize is right for your business',
  [Articles.DATA_TO_PROVIDE]: 'What data should I provide?',
  [Articles.METRICS_AND_IMPACT]: 'Metrics and understanding impact',
  [Articles.REAL_TIME_PERSONALIZATION]: 'Real time personalization based on real time user activity',
  [Articles.BATCH_RECOMMENDATIONS]: 'Batch recommendations',
  [Articles.ABOUT_THIS_DEMO]: 'About this demo',
  [Articles.DATASETS]: 'Datasets',
  [Articles.SHOPPER_PERSONAS]: 'Shopper Personas',
  [Articles.ENABLING_SHOPPER_PROFILES]: 'Enabling Shopper Profiles',
};

export const sections = [
  {
    id: Sections.USE_CASES,
    articles: [
      Articles.ECOMM_RFY,
      Articles.ECOMM_POPULAR_BY_VIEWS,
      Articles.PERSONALIZED_RANKING,
      Articles.SIMILAR_ITEMS_RECOMMENDATIONS,
      Articles.USER_SEGMENTATION,
      Articles.PERSONALIZED_EMAILS,
      Articles.SMS_MESSAGING,
      Articles.OMNI_CHANNEL,
      Articles.LOCATION_SERVICES,
    ],
  },
  {
    id: Sections.PERSONALIZE_USEFUL_TOPICS,
    articles: [
      Articles.RIGHT_FOR_YOU,
      Articles.DATA_TO_PROVIDE,
      Articles.METRICS_AND_IMPACT,
      Articles.REAL_TIME_PERSONALIZATION,
      Articles.BATCH_RECOMMENDATIONS,
      Articles.ECOMM_FBT,
      Articles.ECOMM_POPULAR_BY_PURCHASES,
      Articles.ECOMM_CUSTOMERS_WHO_VIEWED_X,
      Articles.USER_PERSONALIZATION,
      Articles.SIMS_RECOMMENDATIONS,
      Articles.ML_USER_SEGMENTATION,
    ],
  },
  {
    id: Sections.ABOUT_THIS_DEMO,
    articles: [
      Articles.ABOUT_THIS_DEMO,
      Articles.DATASETS,
      Articles.SHOPPER_PERSONAS,
      Articles.ENABLING_SHOPPER_PROFILES,
    ],
  },
];

const articleIdToSectionIdMap = {};
sections.forEach((section) => {
  section.articles.forEach((article) => (articleIdToSectionIdMap[article] = section.id));
});

export const getSectionIdFromArticleId = (articleId) => articleIdToSectionIdMap[articleId];

const personalizeARNToDemoGuideArticleMap = {
  'arn:aws:personalize:::recipe/aws-sims': Articles.SIMS_RECOMMENDATIONS,
  'arn:aws:personalize:::recipe/aws-similar-items': Articles.SIMILAR_ITEMS_RECOMMENDATIONS,
  'arn:aws:personalize:::recipe/aws-personalized-ranking': Articles.PERSONALIZED_RANKING,
  'arn:aws:personalize:::recipe/aws-user-personalization': Articles.USER_PERSONALIZATION,
  'arn:aws:personalize:::recipe/aws-ecomm-customers-who-viewed-x-also-viewed': Articles.ECOMM_CUSTOMERS_WHO_VIEWED_X,
  'arn:aws:personalize:::recipe/aws-ecomm-frequently-bought-together': Articles.ECOMM_FBT,
  'arn:aws:personalize:::recipe/aws-ecomm-popular-items-by-purchases': Articles.ECOMM_POPULAR_BY_PURCHASES,
  'arn:aws:personalize:::recipe/aws-ecomm-popular-items-by-views': Articles.ECOMM_POPULAR_BY_VIEWS,
  'arn:aws:personalize:::recipe/aws-ecomm-recommended-for-you': Articles.ECOMM_RFY
};

export const getDemoGuideArticleFromPersonalizeARN = (arn) => personalizeARNToDemoGuideArticleMap[arn];
