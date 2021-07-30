<template>
  <ArticleLayout>
    <template #heading>Datasets</template>

    <p>
      The Retail Demo Store uses all
      <a
        href="https://docs.aws.amazon.com/personalize/latest/dg/how-it-works-dataset-schema.html"
        target="_blank"
        rel="noreferrer noopener"
        >three supported dataset types</a
      >
      for Amazon Personalize: users, items, and interactions. Additionally, an Amazon Personalize Event Tracker is
      utilized to capture real-time events in the web user interface which populate the Personalize-managed event
      interactions dataset. AWS Amplify is used to send events to the Retail Demo Store’s Personalize Event Tracker.
    </p>

    <p>
      With the exception of the real-time event data which is created as a result of your browsing behavior in the web
      user interface, the data in the users, items, and interactions datasets are composed of fictitious, or in the case
      of interactions history, synthetically generated data.
    </p>
  </ArticleLayout>
</template>

<script>
import ArticleLayout from '../ArticleLayout';

export default {
  name: 'Datasets',
  components: { ArticleLayout },
};
</script>
