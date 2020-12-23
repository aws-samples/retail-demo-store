<template>
  <ArticleLayout>
    <template #heading>Find out why Amazon Personalize is right for your business</template>

    <ol class="reasons">
      <li class="reason">
        Experience from Amazon: Over 20 years of personalization research and experience at
        <a href="https://amazon.com" target="_blank" rel="noreferrer noopener">Amazon.com</a>.
      </li>
      <li class="reason">
        Machine learning based personalization: Delivers higher quality product and content recommendations as well as
        targeted marketing promotions using machine learning and customer’s data set.
      </li>
      <li class="reason">
        No machine learning experience required: All of the complicated and time consuming steps required to build,
        train, and deploy a machine learning personalization solution are automated.
      </li>
      <li class="reason">
        Personalization in days, not months: Easily integrates into your existing websites, apps, SMS, and email
        marketing systems so you can implement a sophisticated and scalable personalization solution in days, rather
        than months.
      </li>

      <li class="reason">
        Proven success in improving customer engagement and conversion: *Lotte Mart*, a leading South Korean retailer
        with over 600K coupon mobile app users, has seen a 40% increase in the number of products a consumer has not
        previously purchased. *StockX,* a Detroit startup company revolutionizing ecommerce with a unique Bid/Ask
        marketplace, added a Recommended For You product row to the homepage using
        <a href="https://aws.amazon.com/personalize" target="_blank" rel="noreferrer noopener">Amazon Personalize</a>,
        which ultimately became the top-performing homepage row. *Mecca, *a beauty retailer in Australia and New
        Zealand, realized a 65% increase in e-mail click-through rates and a corresponding increase in email revenue
        relating to the products recommended by Amazon Personalize. To personalize their customer experience further,
        they are now extending the use of Amazon Personalize to additional areas including our website.
      </li>
    </ol>

    <ArticleFeature>
      <template #default>
        <div>
          <div class="mecca float-left mr-3"><img src="/mecca.png" alt="" class="img-fluid" /></div>
          <p>
            MECCA brings our customers the best in global beauty across our retail stores and online channels in Australia and New Zealand. We’ve created a unique shopping experience for our customers in our 100+ stores, with an extensive collection of products from over 100 beauty brands, and exceptional service and beauty expertise.
          </p>
        </div>

        <Quote>
          <template #quote>
            “At MECCA it’s about earning and keeping customer trust. We have challenged ourselves to translate our
            highly personalized in-store service to our online experience. A fast and effective PoC with Amazon
            Personalize, led by the MECCA technology and CRM teams, in collaboration with our partner Servian,
            demonstrated how much we could achieve without developing our own recommendation engine. Since integrating
            Personalize, we are seeing our customers respond positively to the new recommendations with a 65% increase
            in e-mail click-through rates and a corresponding increase in email revenue relating to the products
            recommended by Personalize. To personalize our customer experience further, we are now extending the use of
            Personalize to additional areas including our website.“
          </template>

          <template #attribution>
            <div>Sam Bain</div>
            <div>MECCA eCommerce & CRM Director</div>
          </template>
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
  name: 'RightForYou',
  components: { ArticleLayout, ArticleFeature, Quote },
};
</script>

<style scoped>
.reasons {
  margin-bottom: 9rem;
  padding-left: 20px;
}

.reason {
  margin-bottom: 10px;
}

.reason:last-of-type {
  margin-bottom: 0;
}

.mecca {
  width: 200px;
}
</style>
