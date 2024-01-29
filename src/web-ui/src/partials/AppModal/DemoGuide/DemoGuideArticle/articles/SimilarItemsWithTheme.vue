<template>
    <ArticleLayout>
      <template #heading>Related Items Recommendations with Generative AI Theme</template>

      <template #recipe>
        Amazon Personalize Recipe:
        <a
          href="https://docs.aws.amazon.com/personalize/latest/dg/native-recipe-similar-items.html"
          target="_blank"
          rel="noreferrer noopener"
          >Similar-Items</a
        >
        with
        <a
          href="https://docs.aws.amazon.com/personalize/latest/dg/personalize-with-gen-ai.html#gen-ai-themed-rec"
          target="_blank"
          rel="noreferrer noopener"
          >Content Generator</a
        >
      </template>

      <p>
        Related item recommendations help users discover new products or compare existing items in your catalog. Amazon
        Personalize recommends related items based on user behavior and thematically similar item attributes to create unique, relevant experiences
        for your customers.
      </p>

      <p>
        This user experience is implemented using the Similar-Items algorithm that considers co-occurrence in interactions data (how often these items appear together across user histories)
        and thematic similarity (what is similar about the items in your catalog) when making recommendations to better quantify similarity for less popular or new items in
        your catalog. For this product detail page, the <a href="https://docs.aws.amazon.com/personalize/latest/dg/personalize-with-gen-ai.html#gen-ai-themed-rec">Personalize Content Generator</a> was
        used to create a descriptive theme for the set of similar items. This descriptive theme is being used as the title/label over the related items on this page. Explore the product detail
        page for other featured products in the Retail Demo Store catalog to see additional generated themes.
      </p>

      <p>
        You can read more about the <a href="https://aws.amazon.com/blogs/machine-learning/amazon-personalize-can-now-unlock-intrinsic-signals-in-your-catalog-to-recommend-similar-items/">Similar-Items recipe</a> and
        <a href="https://aws.amazon.com/about-aws/whats-new/2023/11/amazon-personalize-themes-generative-ai/">Content Generator</a> on the Amazon Personalize blog.
      </p>

    </ArticleLayout>
  </template>

  <script>
  import ArticleLayout from '../ArticleLayout.vue';

  export default {
    name: 'SimilarItemsWithTheme',
    components: { ArticleLayout },
  };
  </script>
