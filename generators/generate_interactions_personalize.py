"""
This script exists so that when developing or internal deployment of public commits
the new Personalize training files can be generated, picked up, and uploaded.

This script generates interactions for Amazon Personalize by heuristic simulation. It is based off the notebook
under workshop/01-Personalization where the logic is explained in more detail.
However, it has been improved in the following ways:
 1. This script is deterministic; random seeds from RANDOM_SEED random variable below.
 2. Logic exists for ensuring balance across categories.
 3. Logic exists for ensuring balance across products.
 4. Discount events are also generated according to 3 different types of users: discount-likers discount-indifferent,
    and price-sensitive-discount-likers.
Item 1 allows us to re-generate data during staging and item 2 and 3 helps recommendations look appropriate in
the final demo. If there is poor balance across products and categories then one may not get recommendations
for products in the same category. This is a hotfix for the logic whereby we generate profiles and probabilistically
sample product categories according to the sample user profile. Item 4 is necessary for training the discounts
personalizeation campaign.
"""
import json
import pandas as pd
import numpy as np
import time
import csv
from pathlib import Path
import gzip
import random
import yaml
import logging
from collections import defaultdict

# Keep things deterministic
RANDOM_SEED = 0

# Where to put the generated data so that it is picked up by stage.sh
GENERATED_DATA_ROOT = "src/aws-lambda/personalize-pre-create-campaigns/data"

# Interactions will be generated between these dates
FIRST_TIMESTAMP = 1591803782  # 2020-06-10, 18:43:02
LAST_TIMESTAMP = 1599579782  # 2020-09-08, 18:43:02

# Users are set up with 3 product categories on their personas. If [0.6, 0.25, 0.15] it means
# 60% of the time they'll choose a product from the first category, etc.
CATEGORY_AFFINITY_PROBS = [0.6, 0.25, 0.15]

# After a product, there are this many products within the category that a user is likely to jump on next.
# The purpose of this is to keep recommendations focused within the category if there are too many products
# in a category, because at present the user profiles approach samples products from a category.
PRODUCT_AFFINITY_N = 4

# from 0 to 1. If 0 then products in busy categories get represented less. If 1 then all products same amount.
NORMALISE_PER_PRODUCT_WEIGHT = 1.0

# With this probability a product interaction will be with the product discounted
# Here we go the other way - what is the probability that a product that a user is already interacting
# with is discounted - depending on whether user likes discounts or not
DISCOUNT_PROBABILITY = 0.2
DISCOUNT_PROBABILITY_WITH_PREFERENCE = 0.5

IN_PRODUCTS_FILENAME = "src/products/src/products-service/data/products.yaml"
IN_USERS_FILENAME = "src/users/src/users-service/data/users.json.gz"

PROGRESS_MONITOR_SECONDS_UPDATE = 30

# This is where stage.sh will pick them up from
out_items_filename = f"{GENERATED_DATA_ROOT}/items.csv"
out_users_filename = f"{GENERATED_DATA_ROOT}/users.csv"
out_interactions_filename = f"{GENERATED_DATA_ROOT}/interactions.csv"

# The meaning of the below constants is described in the relevant notebook.

# Minimum number of interactions to generate
min_interactions = 675000
# min_interactions = 50000

# Percentages of each event type to generate
product_added_percent = .08
cart_viewed_percent = .05
checkout_started_percent = .02
order_completed_percent = .01


def generate_user_items(out_users_filename, out_items_filename, in_users_filename, in_products_filename):

    Path(out_items_filename).parents[0].mkdir(parents=True, exist_ok=True)
    Path(out_users_filename).parents[0].mkdir(parents=True, exist_ok=True)

    # Product info is stored in the repository
    with open(in_products_filename, 'r') as f:
        products = yaml.safe_load(f)

    products_df = pd.DataFrame(products)

    # User info is stored in the repository - it was automatically generated
    with gzip.open(in_users_filename, 'r') as f:
        users = json.load(f)

    users_df = pd.DataFrame(users)

    products_dataset_df = products_df[['id', 'category', 'style', 'description']]
    products_dataset_df = products_dataset_df.rename(columns={'id': 'ITEM_ID',
                                                              'category': 'CATEGORY',
                                                              'style': 'STYLE',
                                                              'description': 'DESCRIPTION'})
    products_dataset_df.to_csv(out_items_filename, index=False)

    users_dataset_df = users_df[['id', 'age', 'gender']]
    users_dataset_df = users_dataset_df.rename(columns={'id': 'USER_ID',
                                                        'age': 'AGE',
                                                        'gender': 'GENDER'})

    users_dataset_df.to_csv(out_users_filename, index=False)

    return users_df, products_df


def generate_interactions(out_interactions_filename, users_df, products_df):
    """Generate items.csv, users.csv from users and product dataframes makes interactions.csv by simulating some
    shopping behaviour."""

    # Count of interactions generated for each event type
    product_viewed_count = 0
    discounted_product_viewed_count = 0
    product_added_count = 0
    discounted_product_added_count = 0
    cart_viewed_count = 0
    discounted_cart_viewed_count = 0
    checkout_started_count = 0
    discounted_checkout_started_count = 0
    order_completed_count = 0
    discounted_order_completed_count = 0

    Path(out_interactions_filename).parents[0].mkdir(parents=True, exist_ok=True)

    # ensure determinism
    random.seed(RANDOM_SEED)
    np.random.seed(RANDOM_SEED)

    start_time_progress = int(time.time())
    next_timestamp = FIRST_TIMESTAMP
    seconds_increment = int((LAST_TIMESTAMP - FIRST_TIMESTAMP) / min_interactions)
    next_update_progress = start_time_progress + PROGRESS_MONITOR_SECONDS_UPDATE/2

    average_product_price = int(products_df.price.mean())
    print('Average product price: ${:.2f}'.format(average_product_price))

    if seconds_increment <= 0: raise AssertionError(f"Should never happen: {seconds_increment} <= 0")

    print('Minimum interactions to generate: {}'.format(min_interactions))
    print('Starting timestamp: {} ({})'.format(next_timestamp,
                                               time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(next_timestamp))))
    print('Seconds increment: {}'.format(seconds_increment))

    print("Generating interactions... (this may take a few minutes)")
    interactions = 0

    subsets_cache = {}

    user_to_product = defaultdict(set)

    category_affinity_probs = np.array(CATEGORY_AFFINITY_PROBS)

    print("Writing interactions to: {}".format(out_interactions_filename))

    with open(out_interactions_filename, 'w') as outfile:
        f = csv.writer(outfile)
        f.writerow(["ITEM_ID", "USER_ID", "EVENT_TYPE", "TIMESTAMP", "DISCOUNT"])

        category_frequencies = products_df.category.value_counts()
        category_frequencies /= sum(category_frequencies.values)

        interaction_product_counts = defaultdict(int)

        # Here we build up a list for each category/gender, of product
        # affinities. The product affinity is keyed by one product,
        # so we do not end up with exactly PRODUCT_AFFINITY_N sized
        # cliques. They overlap a little over multiple users
        # - that is why PRODUCT_AFFINITY_N
        # can be a little bit lower than a desired clique size.
        all_categories = products_df.category.unique()
        product_affinities_bycatgender = {}
        for category in all_categories:
            for gender in ['M', 'F']:
                products_cat = products_df.loc[products_df.category==category]
                products_cat = products_cat.loc[
                    products_cat.gender_affinity.isnull()|(products_cat.gender_affinity==gender)].id.values
                # We ensure that all products have PRODUCT_AFFINITY_N products that lead into it
                # and PRODUCT_AFFINITY_N products it leads to
                affinity_matrix = sum([np.roll(np.identity(len(products_cat)), [0, i], [0, 1])
                                       for i in range(PRODUCT_AFFINITY_N)])
                np.random.shuffle(affinity_matrix)
                affinity_matrix = affinity_matrix.T
                np.random.shuffle(affinity_matrix)
                affinity_matrix = affinity_matrix.astype(bool)  # use as boolean index
                affinity_matrix = affinity_matrix | np.identity(len(products_cat), dtype=bool)

                product_infinities = [products_cat[row] for row in affinity_matrix]
                product_affinities_bycatgender[(category, gender)] = {
                    products_cat[i]: products_df.loc[products_df.id.isin(product_infinities[i])]
                    for i in range(len(products_cat))}

        user_category_to_first_prod = {}

        while interactions < min_interactions:
            if (time.time() > next_update_progress):
                rate = interactions / (time.time() - start_time_progress)
                to_go = (min_interactions - interactions) / rate
                print('Generated {} interactions so far (about {} seconds to go)'.format(interactions, int(to_go)))
                next_update_progress += PROGRESS_MONITOR_SECONDS_UPDATE

            # Pick a random user
            user = users_df.loc[random.randint(0, users_df.shape[0] - 1)]

            # Determine category affinity from user's persona
            persona = user['persona']
            preferred_categories = persona.split('_')

            p_normalised = (category_affinity_probs * category_frequencies[preferred_categories].values)
            p_normalised /= p_normalised.sum()
            p = NORMALISE_PER_PRODUCT_WEIGHT * p_normalised + (1-NORMALISE_PER_PRODUCT_WEIGHT) * category_affinity_probs

            # Select category based on weighted preference of category order.
            category = np.random.choice(preferred_categories, 1, p=p)[0]
            discount_persona = user['discount_persona']

            gender = user['gender']

            # Here, in order to keep the number of products that are related to a product,
            # we restrict the size of the set of products that are recommended to an individual
            # user - in effect, the available subset for a particular category/gender
            # depends on the first product selected, which is selected as per previous logic
            # (looking at category affinities and gender)
            usercat_key = (user['id'], category)  # has this user already selected a "first" product?
            if usercat_key in user_category_to_first_prod:
                # If a first product is already selected, we use the product affinities for that product
                # To provide the list of products to select from
                first_prod = user_category_to_first_prod[usercat_key]
                prods_subset_df = product_affinities_bycatgender[(category, gender)][first_prod]

            if not usercat_key in user_category_to_first_prod:
                # If the user has not yet selected a first product for this category
                # we do it according to the old logic of choosing between all products for gender
                # Check if subset data frame is already cached for category & gender
                prods_subset_df = subsets_cache.get(category + gender)
                if prods_subset_df is None:
                    # Select products from selected category without gender affinity or that match user's gender
                    prods_subset_df = products_df.loc[(products_df['category'] == category) & (
                                (products_df['gender_affinity'] == gender) | (products_df['gender_affinity'].isnull()))]
                    # Update cache
                    subsets_cache[category + gender] = prods_subset_df

            # Pick a random product from gender filtered subset
            product = prods_subset_df.sample().iloc[0]

            interaction_product_counts[product.id] += 1

            user_to_product[user['id']].add(product['id'])
            # if len(user_to_product[user['id']])>8:
            #     import pdb;pdb.set_trace()

            if not usercat_key in user_category_to_first_prod:
                user_category_to_first_prod[usercat_key] = product['id']

            # Decide if the product the user is interacting with is discounted
            if discount_persona == 'discount_indifferent':
                discounted = random.random() < DISCOUNT_PROBABILITY
            elif discount_persona == 'all_discounts':
                discounted = random.random() < DISCOUNT_PROBABILITY_WITH_PREFERENCE
            elif discount_persona == 'lower_priced_products':
                if product.price < average_product_price:
                    discounted = random.random() < DISCOUNT_PROBABILITY_WITH_PREFERENCE
                else:
                    discounted = random.random() < DISCOUNT_PROBABILITY
            else:
                raise ValueError(f'Unable to handle discount persona: {discount_persona}')

            this_timestamp = next_timestamp + random.randint(0, seconds_increment)

            num_interaction_sets_to_insert = 1
            prodcnts = list(interaction_product_counts.values())
            prodcnts_max = max(prodcnts) if len(prodcnts)>0 else 0
            prodcnts_min = min(prodcnts) if len(prodcnts) > 0 else 0
            prodcnts_avg = sum(prodcnts)/len(prodcnts) if len(prodcnts)>0 else 0
            if interaction_product_counts[product.id] * 2 < prodcnts_max:
                num_interaction_sets_to_insert += 1
            if interaction_product_counts[product.id] < prodcnts_avg:
                num_interaction_sets_to_insert += 1
            if interaction_product_counts[product.id] == prodcnts_min:
                num_interaction_sets_to_insert += 1

            for _ in range(num_interaction_sets_to_insert):

                discount_context = 'Yes' if discounted else 'No'

                f.writerow([product['id'],
                            user['id'],
                            'ProductViewed',
                            this_timestamp,
                            discount_context])
                next_timestamp += seconds_increment
                product_viewed_count += 1
                interactions += 1

                if discounted:
                    discounted_product_viewed_count += 1

                if product_added_count < int(product_viewed_count * product_added_percent):
                    this_timestamp += random.randint(0, int(seconds_increment / 2))
                    f.writerow([product['id'],
                                user['id'],
                                'ProductAdded',
                                this_timestamp,
                                discount_context])
                    interactions += 1
                    product_added_count += 1

                    if discounted:
                        discounted_product_added_count += 1

                if cart_viewed_count < int(product_viewed_count * cart_viewed_percent):
                    this_timestamp += random.randint(0, int(seconds_increment / 2))
                    f.writerow([product['id'],
                                user['id'],
                                'CartViewed',
                                this_timestamp,
                                discount_context])
                    interactions += 1
                    cart_viewed_count += 1
                    if discounted:
                        discounted_cart_viewed_count += 1

                if checkout_started_count < int(product_viewed_count * checkout_started_percent):
                    this_timestamp += random.randint(0, int(seconds_increment / 2))
                    f.writerow([product['id'],
                                user['id'],
                                'CheckoutStarted',
                                this_timestamp,
                                discount_context])
                    interactions += 1
                    checkout_started_count += 1
                    if discounted:
                           discounted_checkout_started_count += 1

                if order_completed_count < int(product_viewed_count * order_completed_percent):
                    this_timestamp += random.randint(0, int(seconds_increment / 2))
                    f.writerow([product['id'],
                                user['id'],
                                'OrderCompleted',
                                this_timestamp,
                                discount_context])
                    interactions += 1
                    order_completed_count += 1
                    if discounted:
                        discounted_order_completed_count += 1

    print("Interactions generation done.")
    print(f"Total interactions: {interactions}")
    print(f"Total product viewed: {product_viewed_count} ({discounted_product_viewed_count})")
    print(f"Total product added: {product_added_count} ({discounted_product_added_count})")
    print(f"Total cart viewed: {cart_viewed_count} ({discounted_cart_viewed_count})")
    print(f"Total checkout started: {checkout_started_count} ({discounted_checkout_started_count})")
    print(f"Total order completed: {order_completed_count} ({discounted_order_completed_count})")

    globals().update(locals())   # This can be used for inspecting in console after script ran or if run with ipython.
    print('Generation script finished')


if __name__ == '__main__':

    logging.basicConfig(level=logging.INFO)
    users_df, products_df = generate_user_items(out_users_filename, out_items_filename, IN_USERS_FILENAME, IN_PRODUCTS_FILENAME)
    generate_interactions(out_interactions_filename, users_df, products_df)
