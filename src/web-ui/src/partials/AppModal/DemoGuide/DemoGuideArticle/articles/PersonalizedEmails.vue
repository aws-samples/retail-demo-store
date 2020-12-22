<template>
  <ArticleLayout>
    <template #heading>Personalized Emails: Welcome and Abandoned Cart</template>

    <p>
      Amazon Pinpoint enables organizations to deliver messages across email, text, mobile push, voice, and custom
      channels like messenger apps and retail apps. These messages can be augmented with data output from ML services
      like Amazon Personalize for Personalization, Recommendations, Next-Best-Actions, among other use cases. User
      attributes from Amazon Personalize can be selected within the Amazon Pinpoint console or API in order to
      personalize the content of email templates in real-time. Importantly, this enables organizations to deliver a
      unified, omni-channel personalization experience.
    </p>

    <div class="bullet-container">
      Here,
      <ol class="bullets">
        <li class="bullet-point">
          Pinpoint sends new users a welcome email after they sign up for a Retail Demo Store account. Check the email
          entered during account creation and look for the Retail Demo Store welcome email. If you’d like to send the
          email to a different email address, go to the Account settings page and enter the new one.
        </li>

        <li class="bullet-point">
          When Retail Demo Store users add items to their shopping cart but do not complete an order, Amazon Pinpoint
          send an email with a coupon code encouraging them to finish their order. To see this feature, add a few items
          to your shopping cart. In the shopping cart page, click on the button that says ”Trigger Abandoned Cart
          email”. This action will emulate a signed out event and will trigger the abandoned cart email sent by Amazon
          Pinpoint. Next, check the email account provided during account creation. The Abandoned Shopping Cart email will be in your
          inbox.
        </li>
      </ol>
    </div>

    <ArticleFeature>
      <template #default>
        <div :class="{ 'd-flex align-items-center': true, 'logo-and-quote--mobile': isMobile }">
          <div class="netflix mr-4"><img src="/netflix.png" alt="netflix" class="img-fluid" /></div>
          <div class="netflix-text">
            <div>Migrated 100% of email sending activities to Amazon SES</div>
            <div>100M+ emails sent per day in 190n countries</div>
            <div>Inbox placement rate > 99%</div>
            <div>Reputation score 97/100</div>
          </div>
        </div>

        <Quote>
          <template #quote>
            “Amazon SES helped us be elastic, we could pay as we went along, and we could stop worrying about optimizing
            settings for each ISP.”
          </template>

          <template #attribution>
            <div>Devika Chawla</div>
            <div>Director of Messaging and Platform Engineering. Netflix</div>
          </template>
        </Quote>
      </template>
    </ArticleFeature>
  </ArticleLayout>
</template>

<script>
import { mapState } from 'vuex';

import ArticleLayout from '../ArticleLayout';
import ArticleFeature from '../ArticleFeature/ArticleFeature';
import Quote from '../Quote/Quote';

export default {
  name: 'Personalized',
  components: { ArticleLayout, ArticleFeature, Quote },
  computed: { ...mapState({ isMobile: (state) => state.modal.isMobile }) },
};
</script>

<style scoped>
.bullet-container {
  margin-bottom: 9rem;
}

.bullets {
  padding-left: 20px;
}

.bullet-point {
  margin-bottom: 10px;
}

.bullet-point:last-of-type {
  margin-bottom: 0;
}

.logo-and-quote--mobile {
  margin-bottom: 20px;
  flex-direction: column;
}

.logo-and-quote--mobile .netflix {
  width: auto;
  max-width: 300px;
}

.netflix {
  width: 220px;
}

.netflix-text {
  flex: 1;
}
</style>
