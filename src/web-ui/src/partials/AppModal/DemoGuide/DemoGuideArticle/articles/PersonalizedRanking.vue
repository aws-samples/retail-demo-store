<template>
  <ArticleLayout>
    <template #heading>Personalized Ranking</template>

    <template #recipe>
      Amazon Personalize Recipe:
      <a
        href="https://docs.aws.amazon.com/personalize/latest/dg/personalized-ranking-recipes.html"
        target="_blank"
        rel="noreferrer noopener"
        >Personalized-Ranking</a
      >
    </template>

    <p>
      Regularly your business priorities require you to promote specific content or products, such as trending news, a
      hit new TV show, seasonal merchandise, or a time bound promotional offer. Whether the source is a person, business
      rules around product lifecycle management, or a line of code, Amazon Personalize enables you to re-rank your
      product catalog to achieve your business priorities and best customer experience.
    </p>

    <p>
      Uses the same HRNN algorithm underneath User-Personalization but takes in a user AND a collection of items. This
      will then look at the collection of items and rank them in order of most relevant to least for the user. This is
      great for promoting a pre-selected collection of items and knowing what is the right thing to promote for a
      particular user.
    </p>

    <p>
      You can see the personalized ranking use-case on the on the “Featured” products view. The products are re-ranked
      based on the fictitious shopper's historical and real-time activity.
    </p>
  </ArticleLayout>
</template>

<script>
import ArticleLayout from '../ArticleLayout';

export default {
  name: 'PersonalizedRanking',
  components: { ArticleLayout },
};
</script>
