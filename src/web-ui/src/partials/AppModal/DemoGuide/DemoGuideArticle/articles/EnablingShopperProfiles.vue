<template>
  <ArticleLayout>
    <template #heading>Enabling Shopper Profiles</template>

    <p>
      With Amazon Personalize Solutions and Campaigns created based on the generated users, items, and interactions
      datasets, we can emulate (or assume) user profiles for different personas in the web user interface to see
      recommendations that should be consistent with the persona. In order to emulate a profile, you must first sign in
      to the user account you created for yourself. Once signed in, you'll see the shopper assigned to you on the top
      right corner. You can switch the shopper at any time by clicking the name of the user and selecting the "Switch
      shoppers" option.
    </p>

    <div><img src="/shopper-profile-select.png" alt="" class="img-fluid" /></div>
  </ArticleLayout>
</template>

<script>
import ArticleLayout from '../ArticleLayout';

export default {
  name: 'EnablingShopperProfiles',
  components: { ArticleLayout },
};
</script>
