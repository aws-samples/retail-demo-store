<template>
  <ArticleLayout>
    <template #heading>Machine Learning User Segmentation</template>

    <template #recipe>
      Amazon Personalize Recipes:
      <a
        href="https://docs.aws.amazon.com/personalize/latest/dg/item-affinity-recipe.html"
        target="_blank"
        rel="noreferrer noopener"
        >Item-Affinity</a
      >,&nbsp;
      <a
        href="https://docs.aws.amazon.com/personalize/latest/dg/item-attribute-affinity-recipe.html"
        target="_blank"
        rel="noreferrer noopener"
        >Item-Attribute-Affinity</a
      >
    </template>

    <p>
      Traditionally, user segmentation depends on demographic or psychographic information to sort users into predefined audiences.
      More advanced techniques look to identify common behavioral patterns in the customer journey (such as frequent site visits,
      recent purchases, or cart abandonment) using business rules to derive users' intent. These techniques rely on assumptions about
      the users' preferences and intentions that limit their scalability, don't automatically learn from changing user behaviors, and
      don't offer user experiences personalized for each user. User segmentation in Amazon Personalize uses ML techniques, developed
      and perfected at Amazon, to learn what is relevant to users. Amazon Personalize automatically identifies high propensity users
      without the need to develop and maintain an extensive and brittle catalog of rules. This means you can create more effective user
      segments that scale with your catalog and learn from your users' changing behavior to deliver what matters to them.
    </p>
    <p>
      The Amazon Personalize User Segmentation recipes are simple to use. Provide Amazon Personalize with data about your items and your
      users' interactions and Amazon Personalize will learn your users' preferences. When given an item or item-attribute Amazon Personalize
      recommends a list of users sorted by their propensity to interact with the item or items that share the attribute.
    </p>
    <p>
      Some common retail use cases for user segmentation include marketing campaigns to promote excess inventory or new items added to a catalog.
      With the Item-Affinity recipe, you can create segments of users with an affinity for existing items with excess or lazy inventory.
      With the Item-Attribute-Affinity recipe, you can create segments of users with an affinity for new items based on their bahavior with
      existing items with similar attributes.
    </p>
    <p>
      You can read more about User Segmentation on the <a href="https://aws.amazon.com/blogs/machine-learning/improve-the-return-on-your-marketing-investments-with-intelligent-user-segmentation-in-amazon-personalize/">Amazon Personalize blog</a>.
    </p>

    <h2 class="feature-subheading">User Segmentation Workshop</h2>
    <p>
      This project comes with a step-by-step workshop that will guide you through how to build an item attribute affinity custom solution and
      run a batch segmentation job that will generate user segments based on affinity for product categories.
    </p>
  </ArticleLayout>
</template>

<script>
import ArticleLayout from '../ArticleLayout.vue';

export default {
  name: 'MachineLearningUserSegmentation',
  components: { ArticleLayout },
};
</script>

