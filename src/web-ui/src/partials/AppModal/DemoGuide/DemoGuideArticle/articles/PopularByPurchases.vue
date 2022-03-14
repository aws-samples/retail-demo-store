<template>
  <ArticleLayout>
    <template #heading>Best Sellers: Popular by Purchases</template>

    <template #recipe>
      Amazon Personalize Recipe:
      <a
        href="https://docs.aws.amazon.com/personalize/latest/dg/ECOMMERCE-use-cases.html#best-sellers-use-case"
        target="_blank"
        rel="noreferrer noopener"
        >Popular-by-Purchases</a
      >
    </template>

    <p>
      Recommends best selling products based on how many times customers have purchased an item. The best selling items have the most
      "Purchase" interactions with unique users. The recipe returns the same best selling items for all users. Therefore, recommendations are
      not personalized to the individual user and are useful when you want a system-wide representation of what's selling across the site.
    </p>

  </ArticleLayout>
</template>

<script>
import ArticleLayout from '../ArticleLayout';

export default {
  name: 'PopularByPurchases',
  components: { ArticleLayout },
};
</script>

