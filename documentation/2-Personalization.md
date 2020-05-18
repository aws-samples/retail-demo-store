# Personalization

[Overview](./) > [1 - Creating the Account](1-Creating-account.md) > 2 - Personalization

Personalized user experiences are implemented across several features within the Retail Demo Store web user interface that demonstrate three core use-cases of Amazon Personalize as well as real-time recommendations.

> In order to demonstrate the personalization capabilities of the Retail Demo Store, the required Amazon Personalize Solutions and Campaigns must already be created and enabled via Amazon SSM Parameters. These Solutions and Campaigns can be created as part of the [Personalization workshop](../workshop/1-Personalization/1.1-Personalize.ipynb) bundled with the Retail Demo Store or automatically when the Retail Demo Store is deployed via CloudFormation. If you’re demonstrating with the Retail Demo Store this should already be done for you but still good to be aware if personalization features are not working as expected.

## Datasets

The Retail Demo Store uses all three supported dataset types for Amazon Personalize: users, items, and interactions. Additionally, an Amazon Personalize Event Tracker is utilized to capture real-time events in the web user interface which populate the Personalize-managed event interactions dataset. AWS Amplify is used to send events to the Retail Demo Store’s Personalize Event Tracker.

With the exception of the real-time event data which is created as a result of your browsing behavior in the web user interface, the data in the users, items, and interactions datasets are composed of fictitious, or in the case of interactions history, synthetically generated data.

## Shopper Personas

To provide a more compelling and intuitive demo experience, each fictitious user in the Retail Demo Store is assigned a shopper persona. The persona is represented by a pair of categories from the Retail Demo Store’s catalog. There are four combinations of categories.

* apparel_housewares
* footwear_outdoors
* electronics_beauty
* jewelry_accessories

For example, a user assigned with a persona of "footwear_outdoors" indicates that the user is, at least historically, interested in products from the Footwear and Outdoors categories. That initial interest is codified in the generation of the historical interaction dataset which is used to train Solutions in Amazon Personalize. So, for our "footwear_outdoors" user, interaction events are generated across products in both of those categories to create a synthetic history of engaging in products matching that persona. Events for multiple event types are also generated to mimic shopping behavior. For example, most generated event types are 'ProductViewed' to mimic a user browsing the site. Occasional checkouts are simulated with 'ProductAdded' followed by 'OrderCompleted' events. The Personalize solutions/models are trained on the 'ProductViewed' event type.

## Emulating Shopper Profiles

With Amazon Personalize Solutions and Campaigns created based on the generated users, items, and interactions datasets, we can emulate (or assume) user profiles for different personas in the web user interface to see recommendations that should be consistent with the persona. In order to emulate a profile, you must first sign in to the user account you created for yourself as described in [Creating a Retail Demo Store account](1-Creating-account.md). Once signed in, you can click on your user name in the navigation bar and select “Profile” from the dropdown.

![image.png](../workshop/images/retaildemostore-user-menu.png)

Figure 7. Access Profile Page.

From the Profile page, you can select a user from the “User” dropdown and then press “Save Changes” to link that profile to your browser session.

> It is recommended to open a new Incognito (Chrome) or Private (Firefox) browser window when testing personalization features of the web UI. The reason for this is because Amplify keeps all of your events tied to the same logical session. Signing out and back in as a different account does not change this behavior. You must close and reopen Private/Incognito windows to switch between profiles.

![image.png](../workshop/images/retaildemostore-emulate.png)

Figure 8. Emulate Shopper persona.

Once you’ve saved a profile connection, you can return to the Retail Demo Store home view by clicking on "Retail Demo Store" in the navigation and then interact with features where personalization is implemented as described below.

## Use-Case 1: Personalized Product Recommendations

**Amazon Personalize Recipe:** [HRNN-Metadata](https://docs.aws.amazon.com/personalize/latest/dg/native-recipe-hrnn-metadata.html)

The user personalization use-case is implemented on the bottom half of the Retail Demo Store home view **when you are signed in to a Retail Demo Store user** account. Be sure to emulate a shopper profile as described above so that a persona is linked to your session. Product recommendations in the “Inspired by your shopping trends” section are being powered by Amazon Personalize. If you’re not signed in, featured products will be displayed here instead.

> Since the Retail Demo Store is using a Personalize Event Tracker to record real-time interaction events, it is important to keep in mind that recommendations will change as a result of your clicking and browsing activity in the web application. Therefore, the recommendations may not match up to the original shopper persona used to train the model. This is a powerful demo feature, though, since it shows how Personalize adapts to evolving user intent.

![image.png](../workshop/1-Personalization/images/retaildemostore-product-recs.png)

Figure 9. User recommendation use-case.

## Use-Case 2: Related Products Recommendations

**Amazon Personalize Recipe**: [SIMS](https://docs.aws.amazon.com/personalize/latest/dg/native-recipe-sims.html)

The related products use-case is implemented on the product detail page in the Retail Demo Store. Since inference calls to campaigns built with the SIMS recipe do not require a user, we are able to display related products using SIMS whether you are signed in as a user or anonymous.

![image.png](../workshop/1-Personalization/images/retaildemostore-related-products.png)

Figure 10. Related products use-case.

## Use-Case 3: Personalized Product Ranking

**Amazon Personalize Recipe**: [Personalized-Ranking](https://docs.aws.amazon.com/personalize/latest/dg/native-recipe-search.html)

When you are signed in as a Retail Demo Store user, the personalized ranking use-case is implemented on the category view in the Retail Demo Store. When you are an anonymous user, products are displayed in their natural order (i.e. not ranked). The most effective view to demonstrate this use-case is on the “Featured” product view. The reason for this is that this is the one category view that includes products from multiple categories. Therefore, the ranking should be more impactful.

![image.png](../workshop/1-Personalization/images/retaildemostore-personalized-ranking.png)

Figure 11. Personalized Ranking use-case.

You can also see personalized ranking in product search results. That is, if you are signed in as a user, search results are reranked based on the user's historical and real-time activity.

![image.png](../workshop/1-Personalization/images/retaildemostore-personalized-search.png)

## Event Tracking

The following semantic interaction event types are instrumented in the Retail Demo Store web user interface. Each time a user (anonymous or known) performs one the following actions, an [event is sent](https://github.com/aws-samples/retail-demo-store/blob/master/src/web-ui/src/analytics/AnalyticsHandler.js) to both Amazon Pinpoint (signed in only) and an Amazon Personalize Event Tracker (if configured).

* ProductSearched – the user performed a product search
* ProductViewed – the user viewed details for a product
* ProductAdded – the user added a product to their shopping cart
* ProductRemoved – the user removed a product from their shopping cart
* ProductQuantityUpdated – the user changed the quantity of a product in their shopping cart
* CartViewed – the user viewed their shopping cart
* CheckoutStarted – the user initiated the checkout process
* OrderCompleted – the user completed an order by completing the checkout process

To assess the impact of real-time event tracking in recommendations made by the user recommendations on the home page, follow these steps.

1. Sign in as (or create) a storefront user.
2. View the product recommendations displayed on the home page under the "Inspired by your shopping trends" header. Take note of the products being recommended.
3. View products from categories that are not being recommended by clicking on their "Details" button. When you view the details for a product, an event is fired and sent to the Personalize event tracker.
4. Return to the home page and you should see products being recommended that are the same or similar to the ones you just viewed.

### Event Instrumentation

If you are demonstrating the Retail Demo Store to a more technical audience, you can illustrate how the events are sent to Pinpoint and Personalize in the background. To do so, open up the Developer Tools in the web browser you’re using (i.e. Chrome), select the Network view, and find the calls to “events” (Personalize) and “legacy” (Pinpoint). The screenshot below illustrates how to display the network call to the Personalize Event Tracker for the “put\_events” endpoint. This is implemented using AWS Amplify to instrument events in the web user interface.

![image.png](../workshop/images/Eventinstrumentationcalls.png)

Figure 12. Event instrumentation calls