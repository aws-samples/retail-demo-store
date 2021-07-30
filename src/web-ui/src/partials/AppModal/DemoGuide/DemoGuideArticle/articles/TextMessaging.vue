<template>
  <ArticleLayout>
    <template #heading>Text Messaging (SMS): Personalized Alerts and Promotions</template>

    <p>
      Amazon Pinpoint has deep configuration options for SMS (text) messaging and can deliver messages to every country
      in the world. Retail / eCommerce organizations have many use cases for text messaging - including transactional
      uses like purchase confirmations and marketing uses like promotions. These messages can be augmented with data
      output from ML services like Amazon Personalize for Personalization, Recommendations, Next-Best-Actions, among
      other use cases. User attributes from Amazon Personalize can be selected within the Amazon Pinpoint console or API
      in order to personalize the content of templates in real-time. Importantly, this enables organizations to deliver
      a unified, omni-channel personalization experience.
    </p>

    <p>
      This demo showcases personalized product recommendation via text message. Try this feature by opting-in to receive
      text alerts.
    </p>

    <p>
      The home page, shopping cart page and every product page in the store include a field to opt-in. Enter the mobile
      phone number where you’d like to receive the one-time automated marketing message.
    </p>

    <div class="text-alerts"><img src="/text-alerts.png" alt="text alerts section" class="img-fluid" /></div>

    <p>
      You will receive a text message to confirm the subscription. Reply “Y” to confirm. Upon confirmation, you’ll
      receive a 20% discount code.
    </p>

    <p>
      Next, you’ll receive one text message with one personalized product recommendation. The message will include a URL
      that will redirect you to the Retail Demo Store
    </p>
  </ArticleLayout>
</template>

<script>
import ArticleLayout from '../ArticleLayout';

export default {
  name: 'TextMessaging',
  components: { ArticleLayout },
};
</script>

<style scoped>
.text-alerts {
  margin: auto;
  width: 100%;
  max-width: 600px;
}
</style>
