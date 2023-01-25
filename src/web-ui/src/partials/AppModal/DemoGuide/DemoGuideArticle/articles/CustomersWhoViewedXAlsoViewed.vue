<template>
  <ArticleLayout>
    <template #heading>Customers Who Viewed X Also Viewed</template>

    <template #recipe>
      Amazon Personalize Recipe:
      <a
        href="https://docs.aws.amazon.com/personalize/latest/dg/ECOMMERCE-use-cases.html#customers-also-viewed-use-case"
        target="_blank"
        rel="noreferrer noopener"
        >Customers-Who-Viewed-X-Also-Viewed</a
      >
    </template>

    <p>
      Related item recommendations help users discover new products or compare existing items in your catalog. Amazon
      Personalize recommends similar items in real-time, based on user behavior to create unique, relevant experiences
      for your customers.
    </p>

    <p>
      Pretty simple idea, implemented via item-item collaborative filtering but basically look at how people are
      interacting with particular products and then determine how similar things are at a global level based on that data.
      Not user specific at all.
    </p>
  </ArticleLayout>
</template>

<script>
import ArticleLayout from '../ArticleLayout.vue';

export default {
  name: 'CustomersWhoViewedXAlsoViewed',
  components: { ArticleLayout },
};
</script>

