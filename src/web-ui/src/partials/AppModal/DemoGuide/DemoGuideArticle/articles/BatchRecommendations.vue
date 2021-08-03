<template>
  <ArticleLayout>
    <template #heading>Batch recommendations</template>

    <p>
      While real-time recommendations are highly recommended, Amazon Personalize does support batch recommendations.
      Batch recommendations let you generate personalized recommendations for a large number of users, or similar items
      for a large number of items, in one go, and then use them in batch processes, such as sending emails or
      notifications.
    </p>

    <div class="architecture">
      <img src="/batch-recommendations-architecture.png" alt="batch recommendations architecture" class="img-fluid" />
    </div>

    <ArticleFeature>
      <template #title>AWS News Blog</template>

      <template #default>
        <h1 class="blog-post-title mb-0">
          <a
            href="https://aws.amazon.com/blogs/aws/now-available-batch-recommendations-in-amazon-personalize/"
            target="_blank"
            rel="noreferrer noopener"
            >Batch Recommendations in Amazon Personalize</a
          >
        </h1>
        <div class="author mb-2">by Julien Simon | on <time>15 NOV 2019</time></div>

        <Quote>
          <template #quote>
            Using batch recommendations with Amazon Personalize is an easy and cost-effective way to add personalization
            to your applications. You can start using this feature today in all regions where Personalize is available…
          </template>
          <template #default
            ><a
              href="https://aws.amazon.com/blogs/aws/now-available-batch-recommendations-in-amazon-personalize/"
              target="_blank"
              rel="noreferrer noopener"
              >Read more</a
            ></template
          >
        </Quote>
      </template>
    </ArticleFeature>
  </ArticleLayout>
</template>

<script>
import ArticleLayout from '../ArticleLayout';
import ArticleFeature from '../ArticleFeature/ArticleFeature';
import Quote from '../Quote/Quote';

export default {
  name: 'BatchRecommendations',
  components: { ArticleLayout, ArticleFeature, Quote },
};
</script>

<style scoped>
.blog-post-title {
  font-size: 1rem;
}

.author {
  font-size: 0.8rem;
}

.architecture {
  margin-bottom: 9rem;
}
</style>
