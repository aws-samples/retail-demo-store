<template>
  <ArticleLayout>
    <template #heading>User Personalization</template>

    <template #recipe>
      Amazon Personalize Recipe:
      <a
        href="https://docs.aws.amazon.com/personalize/latest/dg/native-recipe-new-item-USER_PERSONALIZATION.html"
        target="_blank"
        rel="noreferrer noopener"
        >User-Personalization</a
      >
    </template>

    <p>
      Product and content recommendations tailored to a user’s profile and habits are more likely to drive higher
      conversion. Amazon Personalize helps tailor recommendations to users behavior, preferences, and history, boosting
      their engagement and satisfaction in real-time, instead of providing a uniform experience. User personalization
      also handles the “cold-start” challenge where limited or no historical information is known about an item or user.
      User personalization in Amazon Personalize balances recommending fresh items with the most relevant based on a
      user’s unique preferences and behaviors.
    </p>

    <p>
      User personalization is implemented in the “Inspired by your shopping trends” section. Try using different
      shoppers to experience the difference in personalized product recommendations offered.
    </p>

    <p>If you’re not signed in, featured products will be displayed instead.</p>
  </ArticleLayout>
</template>

<script>
import ArticleLayout from '../ArticleLayout';

export default {
  name: 'UserPersonalization',
  components: { ArticleLayout },
};
</script>

