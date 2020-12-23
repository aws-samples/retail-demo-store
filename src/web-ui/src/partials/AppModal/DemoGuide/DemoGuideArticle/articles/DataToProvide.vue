<template>
  <ArticleLayout>
    <template #heading>What data should I provide?</template>

    <p>Amazon Personalize recognizes three types of historical data:</p>

    <ul class="data-types">
      <li class="type">
        Users – This data is intended to provide information about your users such as age, gender, or loyalty membership
        which can be important signals in personalization systems.
      </li>
      <li class="type">
        Items – This data is intended to provide information about your items, such as price, SKU type, or availability.
      </li>
      <li class="type">
        Interactions – This data is historical interactions between users and items. It can also provide information on
        your user's browsing context, such as their location or device (mobile, tablet, desktop, and so on).
      </li>
    </ul>

    <p>
      The user and item data are metadata types and only used in certain use cases. Please see
      <a
        href="https://docs.aws.amazon.com/personalize/latest/dg/how-it-works-dataset-schema.html"
        target="_blank"
        rel="noreferrer noopener"
        >the documentation</a
      >
      for further technical details.
    </p>

    <p>
      Each type of data that Amazon Personalize recognizes has required fields, reserved keywords and datatypes. Please
      see table below for details.
    </p>

    <div class="personalize-data my-4">
      <img src="/personalize-data.png" alt="Example personlize schema" class="img-fluid" />
    </div>

    <p>
      Amazon Personalize will train and deploy a model based on this data. Developers can then use a simple inference
      API to get individualized recommendations at run-time and generate a personalized experience for the end users
      according to the type of personalization model (e.g. user personalization, similar items or personalized
      rankings). Amazon Personalize works best for large datasets that have over 50 users, 50 items, and 1500
      interactions.
    </p>
  </ArticleLayout>
</template>

<script>
import ArticleLayout from '../ArticleLayout';

export default {
  name: 'DataToProvide',
  components: { ArticleLayout },
};
</script>

<style scoped>
.data-types {
  padding-left: 20px;
}

.type {
  margin-bottom: 10px;
}

.type:last-of-type {
  margin-bottom: 0;
}

.personalize-data {
  margin: auto;
  max-width: 300px;
}
</style>
