
  
# Related Items Recommendations


Amazon Personalize Recipe:
[Similar-Items](https://docs.aws.amazon.com/personalize/latest/dg/native-recipe-similar-items.html)
with
[Personalized-Ranking](https://docs.aws.amazon.com/personalize/latest/dg/personalized-ranking-recipes.html)



Related item recommendations help users discover new products or compare existing items in your catalog. Amazon
Personalize recommends related items in real-time, based on user behavior and thematically similar item attributes to create unique, relevant experiences
for your customers.



This user experience is implemented using the Similar-Items algorithm that considers co-occurrence in interactions data (how often these items appear together across user histories)
and thematic similarity (what is similar about the items in your catalog) when making recommendations to better quantify similarity for less popular or new items in
your catalog. The product detail page in this demo takes it a step further by using the Personalized-Ranking recipe to rerank related items recommendations for each user. This adds a level of
personalization to the user experience.



You can read more about the Similar-Items recipe on the .



The similar item recommendations use case is implemented in all the product detail pages under the “Compare similar items”
carousel widget. The order of items is personalized to each user by leveraging the Personalized-Ranking recipe to reorder
related items based on the current user's interest.



AWS Machine Learning Blog


  


“StockX is a Detroit startup company revolutionizing ecommerce with a unique Bid/Ask marketplace—our
platform models the New York Stock Exchange and treats goods like sneakers and streetwear as high-value,
tradable commodities. With a transparent market experience, StockX provides access to authentic, highly
sought-after products at true market price.”

  

  

“Recommended for You was a massive win for both our team and StockX as a whole. We’re quickly learning the
potency of integrating ML into all facets of the company. Our success led to key decision-makers requesting
we integrate Amazon Personalize into more of the StockX experience and expand our ML endeavors. It’s safe to
say that personalization is now a first-class citizen here.”



Sam Bean and Nic Roberts II at StockX.

  

  
Read full AWS Machine Learning Blog:
[Pioneering personalized user experiences at StockX with Amazon Personalize](https://aws.amazon.com/blogs/machine-learning/pioneering-personalized-user-experiences-at-stockx-with-amazon-personalize/)
  


  


