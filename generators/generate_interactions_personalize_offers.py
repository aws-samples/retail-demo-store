"""
A simple script for generating sample data for learning to give personalised offers.
"""
import json
import pandas as pd
import numpy as np
import gzip
import random
import logging

GENERATE_INBALANCED_DATA = False
NUM_INTERACTIONS_PER_USER = 3

FIRST_TIMESTAMP = 1591803782  # 2020-06-10, 18:43:02
LAST_TIMESTAMP = 1599579782  # 2020-09-08, 18:43:02
RANDOM_SEED = 1

IN_PRODUCTS_FILENAME = "src/products/src/products-service/data/products.yaml"
IN_USERS_FILENAME = "src/users/src/users-service/data/users.json.gz"
IN_OFFERS_FILENAME = "src/offers/src/offers-service/data/offers.json"

# Where to put the generated data so that it is picked up by stage.sh
GENERATED_DATA_ROOT = "src/aws-lambda/personalize-pre-create-resources/data"


def generate_data(interactions_filename, users_df, offers_df):
    """Script for writing to a file simulated user-offer interactions"""

    random.seed(RANDOM_SEED)
    np.random.seed(RANDOM_SEED)

    num_users = users_df.shape[0]
    num_interactions = NUM_INTERACTIONS_PER_USER * num_users

    if GENERATE_INBALANCED_DATA:
        # We may wish to assume probability is proportional to ID to show off how we can add
        # business logic around Personalize
        offer_probs = offers_df.id.values.astype(float)
    else:
        # Or we can work around inbalance at the data munging stage
        offer_probs = np.ones(len(offers_df.id.values), dtype=float)

    # Normalise so that we have probabilities
    offer_probs = offer_probs / offer_probs.sum()

    # generate timestamps
    time_between_events = (LAST_TIMESTAMP - FIRST_TIMESTAMP) / num_interactions
    timestamps = np.arange(FIRST_TIMESTAMP, LAST_TIMESTAMP, time_between_events).astype(int)
    # pre-shuffle them as we will be using them as a randomising key when we sort by timestamp
    np.random.shuffle(timestamps)

    # generate all users Ids
    sample_user_ids = np.tile(users_df['id'].values.astype(int), NUM_INTERACTIONS_PER_USER)
    # only one event type
    event_type = ['OfferConverted'] * num_interactions

    # we sort it to ensure there is a correlation between user ID and offer ID.
    # This correlation is what the personalisation will learn.
    sampled_offers = sorted(np.random.choice(offers_df.id.values, num_interactions, p=offer_probs))

    interactions_df = pd.DataFrame({'ITEM_ID': sampled_offers,
                                    'USER_ID': sample_user_ids,
                                    'EVENT_TYPE': event_type,
                                    'TIMESTAMP': timestamps})

    # by sorting by timestamp, other elements get shuffled
    interactions_df = interactions_df.sort_values('TIMESTAMP')

    with open(interactions_filename, 'w') as outfile:
        interactions_df.to_csv(outfile, index=False)

    globals().update(locals())  # This can be used for inspecting in console after script ran or if run with ipython.
    print('Generation script finished - created offers dataset')


if __name__ == '__main__':

    # User info is stored in the repository - it was automatically generated
    with gzip.open(IN_USERS_FILENAME, 'r') as f:
        users = json.load(f)

    users_df = pd.DataFrame(users)

    # Offers info is stored in repository
    with open(IN_OFFERS_FILENAME, 'r') as f:
        offers = json.load(f)

    offers_df = pd.DataFrame(offers)

    logging.basicConfig(level=logging.INFO)
    generate_data(GENERATED_DATA_ROOT + '/offer_interactions.csv', users_df, offers_df)
