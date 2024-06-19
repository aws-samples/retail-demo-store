
  
# Machine Learning User Segmentation


## Amazon Personalize Recipes:
[Item-Affinity](https://docs.aws.amazon.com/personalize/latest/dg/item-affinity-recipe.html)
[Item-Attribute-Affinity](https://docs.aws.amazon.com/personalize/latest/dg/item-attribute-affinity-recipe.html)



Traditionally, user segmentation depends on demographic or psychographic information to sort users into predefined audiences.
More advanced techniques look to identify common behavioral patterns in the customer journey (such as frequent site visits,
recent purchases, or cart abandonment) using business rules to derive users' intent. These techniques rely on assumptions about
the users' preferences and intentions that limit their scalability, don't automatically learn from changing user behaviors, and
don't offer user experiences personalized for each user. User segmentation in Amazon Personalize uses ML techniques, developed
and perfected at Amazon, to learn what is relevant to users. Amazon Personalize automatically identifies high propensity users
without the need to develop and maintain an extensive and brittle catalog of rules. This means you can create more effective user
segments that scale with your catalog and learn from your users' changing behavior to deliver what matters to them.


The Amazon Personalize User Segmentation recipes are simple to use. Provide Amazon Personalize with data about your items and your
users' interactions and Amazon Personalize will learn your users' preferences. When given an item or item-attribute Amazon Personalize
recommends a list of users sorted by their propensity to interact with the item or items that share the attribute.


Some common retail use cases for user segmentation include marketing campaigns to promote excess inventory or new items added to a catalog.
With the Item-Affinity recipe, you can create segments of users with an affinity for existing items with excess or lazy inventory.
With the Item-Attribute-Affinity recipe, you can create segments of users with an affinity for new items based on their bahavior with
existing items with similar attributes.


You can read more about User Segmentation on the .




This project comes with a step-by-step workshop that will guide you through how to build an item attribute affinity custom solution and
run a batch segmentation job that will generate user segments based on affinity for product categories.


