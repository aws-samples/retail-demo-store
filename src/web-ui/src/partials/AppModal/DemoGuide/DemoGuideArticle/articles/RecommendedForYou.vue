<template>
  <ArticleLayout>
    <template #heading>Recommended For You</template>

    <template #recipe>
      Amazon Personalize Recipe:
      <a
        href="https://docs.aws.amazon.com/personalize/latest/dg/ECOMMERCE-use-cases.html#recommended-for-you-use-case"
        target="_blank"
        rel="noreferrer noopener"
        >Recommended-For-You</a
      >
    </template>

    <p>
      Product and content recommendations tailored to a user's profile and habits are more likely to drive higher
      engagement and conversion. Amazon Personalize helps tailor recommendations to users behavior, preferences, and history, boosting
      their engagement and satisfaction in real-time, instead of providing a uniform experience. The Recommended For You recipe
      also handles the “cold-start” challenge where limited or no historical information is known about an item or user.
      Recommended For You in Amazon Personalize balances recommending fresh items with the most relevant based on a
      user's unique preferences and behaviors while also automatically excluding products that have been recently purchased for
      each user.
    </p>

    <p>
      Recommended For You is implemented in the “Inspired by your shopping trends” section of the homepage. Try using different
      shoppers to experience the difference in personalized product recommendations offered.
    </p>
  </ArticleLayout>
</template>

<script>
import ArticleLayout from '../ArticleLayout';

export default {
  name: 'RecommendedForYou',
  components: { ArticleLayout },
};
</script>

