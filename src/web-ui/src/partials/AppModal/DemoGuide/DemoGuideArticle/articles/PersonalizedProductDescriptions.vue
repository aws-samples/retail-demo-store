<template>
    <ArticleLayout>
      <template #heading>Personalized Product Descriptions</template>
      <p>
        Generative AI can be used to automate the creation of marketing content. This includes generating text for blogs, social media posts, and emails, as well as creating images and videos. 
        This can save marketers a significant amount of time and effort, allowing them to focus on other aspects of their marketing strategy. 
      </p>
      <p>
        Where it really shines is the ability to productionize marketing content creation, reducing the needs for marketers to create multiple copies for different customer segments. 
        Previously, marketers would need to generate many different copies for each granularity of customers (e.g. attriting customers who are between the age of 25-34 and loves food). 
        Generative AI can automate this process, providing the opportunities to dynamically create these contents.
      </p>
      <p>
        This demo integrates the product service with Amazon Bedrock, to retrieve personalized product descriptions based on the logged-in user's age and interests.  
        Amazon Bedrock makes Foundation Models (FMs) accessible via an API, and in this demo,  Anthropic Claude is the underlying FM that is used.

      </p>
    </ArticleLayout>
</template>

<script>
import ArticleLayout from '../ArticleLayout.vue';

export default {
  name: 'PersonalizedRanking',
  components: { ArticleLayout },
};
</script>