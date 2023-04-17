<template>
  <ArticleLayout>
    <template #heading>Frequently Bought Together</template>

    <template #recipe>
      Amazon Personalize Recipe:
      <a
        href="https://docs.aws.amazon.com/personalize/latest/dg/ECOMMERCE-use-cases.html#frequently-bought-together-use-case"
        target="_blank"
        rel="noreferrer noopener"
        >Frequently-Bought-Together</a
      >
    </template>

    <p>
      A common cross-selling technique on e-commerce sites is recommending items that other users have frequently bought together. The idea
      is to encourage users to add more products to their shopping cart and thereby increasing average order value and the bottom line. Amazon
      Personalize implements this use case with the Frequently Bought Together retail recommender. This recommender can be deployed as part of your
      shopping cart or checkout views or when users add new items to their cart.
    </p>
  </ArticleLayout>
</template>

<script>
import ArticleLayout from '../ArticleLayout.vue';

export default {
  name: 'FrequentlyBoughtTogether',
  components: { ArticleLayout },
};
</script>

