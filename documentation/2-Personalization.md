[Overview](./) > [1 - Creating the Account](1-Creating-account.md) > 2 - Personalization

# Personalization

Personalized user experiences are implemented across several features within the Retail Demo Store web user interface that demonstrate four core use-cases of Amazon Personalize.

> In order to demonstrate the personalization capabilities of the Retail Demo Store, the required Amazon Personalize Solutions and Campaigns must already be created and enabled via Amazon SSM Parameters. These Solutions and Campaigns can be created as part of the Personalization workshop bundled with the Retail Demo Store or automatically when the Retail Demo Store is deployed via CloudFormation. If you’re demonstrating with the Retail Demo Store this should already be done for you but still good to be aware if personalization features are not working as expected.


## Datasets

The Retail Demo Store uses all three supported dataset types for Amazon Personalize: users, items, and interactions. Additionally, an Amazon Personalize Event Tracker is utilized to capture real-time events in the web user interface which populate the Personalize-managed event interactions dataset. AWS Amplify is used to send events to the Retail Demo Store’s Personalize Event Tracker. See Figure 2 for the overall architecture diagram.

With the exception of the real-time event data which is created as a result of your browsing behavior in the web user interface, the data in the users, items, and interactions datasets are composed of fictitious, or in the case of interactions history, synthetically generated data.

## Shopper Personas

To provide a more compelling and intuitive demo experience, each fictitious user in the Retail Demo Store is assigned a shopper persona. The persona is represented by a pair of randomly chosen categories from the Retail Demo Store’s catalog. For example, a user assigned with a persona of “housewares\_beauty” indicates that the user is interested in products from the Housewares and Beauty categories. Where that interest is codified is in the generation of the historical interaction dataset which is used to train Solutions in Amazon Personalize. So, for our “housewares\_beauty” user, random interaction events are generated across products in both of those categories to create a synthetic history of engaging in products matching that persona.

## Emulating Shopper Profiles

With Amazon Personalize Solutions and Campaigns created based on the generated users, items, and interactions datasets, we can emulate (or assume) user profiles for different personas in the web user interface to (hopefully) see recommendations that are consistent with the persona.
In order to emulate a profile, you must first sign in to the user account you created for yourself as described in [Creating a Retail Demo Store account](1-Creating-account.md) earlier in this document. Once signed in, you can click on your user name in the navigation bar and select “Profile” from the dropdown.

![image.png](../workshop/images/retaildemostore-user-menu.png)

Figure 7. Access Profile Page.
From the Profile page, you can select a user from the “User” dropdown and then press “Save Changes” to link that profile to your browser session.

![image.png](../workshop/images/retaildemostore-emulate.png)

Figure 8. Emulate Shopper persona.
Once you’ve saved a profile connection, you can return to the Retail Demo Store home page by clicking on “The Retail Demo Store” in the navigation and then interact with features where personalization is implemented as described below.


## Use-Case 1: Personalized Product Recommendations

**Amazon Personalize Recipe:** [HRNN-Metadata](https://docs.aws.amazon.com/personalize/latest/dg/native-recipe-hrnn-metadata.html)

The user personalization use-case is implemented on the bottom half of the Retail Demo Store homepage **when you are signed in to a Retail Demo Store user** account. Be sure to emulate a shopper profile as described above so that a persona is linked to your session. Product recommendations in the “Inspired by your shopping trends” section are being powered by Amazon Personalize. If you’re not signed in, featured products will be displayed here instead.

> Since the Retail Demo Store is using a Personalize Event Tracker to record real-time interaction events, it is important to keep in mind that recommendations will change as a result of your clicking and browsing activity in the web application. Therefore, the recommendations may not match up to the original shopper persona used to train the model. This is a great demo feature, though, since it shows how Personalize adapts to evolving user intent.

![image.png](../workshop/1-Personalization/images/retaildemostore-product-recs.png)

Figure 9. User recommendation use-case.

## Use-Case 2: Related Products Recommendations

**Amazon Personalize Recipe**: [SIMS](https://docs.aws.amazon.com/personalize/latest/dg/native-recipe-sims.html)
The related products use-case is implemented on the product detail page in the Retail Demo Store. Since inference calls to Solutions built with the SIMS recipe do not require a user, we are able to display related products using SIMS whether you are signed in as a user or anonymous.

![image.png](../workshop/1-Personalization/images/retaildemostore-related-products.png)

Figure 10. Related products use-case.


## Use-Case 3: Personalized Product Ranking

**Amazon Personalize Recipe**: Personalized-Ranking
When you are signed in as a Retail Demo Store user, the personalized ranking use-case is implemented on the category view in the Retail Demo Store. When you are an anonymous user, products are displayed in their natural order (i.e. not ranked). The most effective view to demonstrate this use-case is on the “Featured” product view. The reason for this is that this is the one category view that includes products from multiple categories. Therefore, the ranking should be more impactful.

![image.png](../workshop/1-Personalization/images/retaildemostore-personalized-ranking.png)

Figure 11. Personalized Ranking use-case.

## Use-Case 4: Event Tracking

The following semantic interaction event types are instrumented in the Retail Demo Store web user interface. Each time a user (anonymous or known) performs one the following actions, an event is sent to both Amazon Pinpoint and an Amazon Personalize Event Tracker (if configured).

* ProductSearched – the user performed a product search
* ProductViewed – the user viewed details for a product
* ProductAdded – the user added a product to their shopping cart
* ProductRemoved – the user removed a product from their shopping cart
* ProductQuantityUpdated – the user changed the quantity of a product in their shopping cart
* CartViewed – the user viewed their shopping cart
* CheckoutStarted – the user initiated the checkout process
* OrderCompleted – the user completed an order by completing the checkout process


### Event Instrumentation

If you are demonstrating the Retail Demo Store to a more technical audience, you can illustrate how the events are sent to Pinpoint and Personalize in the background. To do so, open up the Developer Tools in the web browser you’re using, select the Network view, and find the calls to “events” (Personalize) and “legacy” (Pinpoint). The screenshot below illustrates how to display the network call to the Personalize Event Tracker for the “put\_events” endpoint. This is accomplished using AWS Amplify to instrument events in the web user interface.

![image.png](../workshop/images/Eventinstrumentationcalls.png)

Figure 12. Event instrumentation calls