# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import random
import uuid

class RDSUserSelectionState:
  def __init__(self, catalog, user):
    if user.persona != '':  # Added to support RDS personas from the catalog
      self.search_results = catalog.subcategory_sample(user.persona.split('_'))
    else:
      self.search_results = random.sample(catalog, 10)
    self.subsample = random.sample(self.search_results, 5)
    self.cart = random.sample(self.subsample, 3)
    self.cart_id = str(uuid.uuid4())
    self.search_terms = []
    for item in self.search_results:
      self.search_terms.extend(item['name'].split(' '))

  def search(self):
    return self.search_results

  def user_search(self):
    separator = ' '
    query = separator.join(random.sample(self.search_terms, 2))
    return query

  def recommendations(self):
    return random.sample(self.subsample, 3)

  def cart_items(self):
    return self.cart

  def num_results(self):
    return len(self.search_results)

  def cart_value(self):
    total = 0.0
    for item in self.cart:
      total += item['price']
    return total

  def item(self):
    return random.choice(self.cart)

  # These are specific to RDS event properties
  def item_added_event_props(self):
    item = self.item()
    return {
      'productId': item['id'],
      'cartId': self.cart_id,
      'name': item['name'],
      'category': item['category'],
      'image': item['image'],
      'price': item['price'],
      'quantity': 1
    }

  def item_viewed_event_props(self):
    item = self.item()
    return {
      'productId': item['id'],
      'name': item['name'],
      'category': item['category'],
      'image': item['image'],
      'price': item['price']
    }

  def cart_viewed_event_props(self):
    return {
      'cartId': self.cart_id,
      'cartSubTotal': self.cart_value(),
      'cartTotal': self.cart_value(),
      'cartQuantity': len(self.cart)
    }