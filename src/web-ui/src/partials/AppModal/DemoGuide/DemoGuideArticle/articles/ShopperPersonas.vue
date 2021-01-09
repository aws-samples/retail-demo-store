<template>
  <ArticleLayout>
    <template #heading>Shopper Personas</template>

    <p>
      To provide a more compelling and intuitive demo experience, each fictitious user in the Retail Demo Store is
      assigned a shopper persona. The persona is represented by three categories from the Retail Demo Store’s catalog
      which the user has an affinity. The affinity for each category is also weighted such that the first category is is
      highest weighted and the third category is the lowest. There are sixteen combinations of categories that represent
      the personas used across all users.
    </p>

    <ul class="personas">
      <li>
        furniture_homedecor_housewares
      </li>
      <li>
        apparel_footwear_accessories
      </li>
      <li>
        instruments_books_electronics
      </li>
      <li>
        floral_beauty_jewelry
      </li>
      <li>
        grocery_seasonal_wedding
      </li>
      <li>
        outdoors_instruments_grocery
      </li>
      <li>
        housewares_floral_seasonal
      </li>
      <li>
        tools_housewares_apparel
      </li>
      <li>
        electronics_outdoors_footwear
      </li>
      <li>
        seasonal_furniture_floral
      </li>
      <li>
        homedecor_electronics_outdoors
      </li>
      <li>
        accessories_grocery_books
      </li>

      <li>
        footwear_jewelry_furniture
      </li>
      <li>
        beauty_accessories_instruments
      </li>
      <li>
        housewares_tools_beauty
      </li>
      <li>
        books_apparel_homedecor
      </li>
    </ul>

    <p>
      For example, a user assigned with a persona of "footwear_outdoors_apparel" indicates that the user, at least
      historically, has been primarily interested in products from the Footwear category and to decreasing degrees of
      interest in products from the Outdoors and Apparel categories. That initial weighted interest is codified in the
      generation of the historical interaction dataset which is used to train Solutions in Amazon Personalize. So, for
      our "footwear_outdoors_apparel" user, interaction events are generated across products in all three of those
      categories to create a synthetic history of engaging in products matching that persona. Additionally, some
      products are tagged with an gender affinity. This is used when generating historical events to filter products
      against the gender of each user to further add realism to the recommendations.
    </p>

    <p>
      Events for multiple event types are generated to mimic shopping behavior. For example, most generated event types
      are 'ProductViewed' to mimic users browsing the site. Occasional checkouts are simulated with 'ProductAdded'
      followed by 'CartViewed', 'CheckoutStarted', and 'OrderCompleted' events. The Personalize solutions/models are
      trained on the 'ProductViewed' event type.
    </p>
  </ArticleLayout>
</template>

<script>
import ArticleLayout from '../ArticleLayout';

export default {
  name: 'ShopperPersonas',
  components: { ArticleLayout },
};
</script>

<style scoped>
.personas {
  padding-left: 16px;
}
</style>
