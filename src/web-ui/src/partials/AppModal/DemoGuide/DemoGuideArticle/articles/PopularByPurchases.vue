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

    <p>
      You may notice some items are annotated with a "Promoted" banner across the top of the product image. This banner indicates
      products that match a promotional filter that is optionally applied when retrieving recommendations. Promotional filters are
      a great way to ensure that a user-defined percentage of recommended items match a specific filter expression but are also
      relevant to the user. This can be used to highlight products on sale or new products recently added to the catalog.
    </p>

    <p>
      You can read more about promotional filters on the <a href="https://aws.amazon.com/blogs/machine-learning/customize-your-recommendations-by-promoting-specific-items-using-business-rules-with-amazon-personalize/">Amazon Personalize blog</a>.
    </p>

  </ArticleLayout>
</template>

<script>
import ArticleLayout from '../ArticleLayout.vue';

export default {
  name: 'PopularByPurchases',
  components: { ArticleLayout },
};
</script>

