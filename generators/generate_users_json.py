# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

""" Generates list of random users using python's Faker

The random users are written to a gzipped JSON file which, when copied 
into place, will be loaded by the Users microservice during initialization.

This script only needs to be run once to produce a random users data 
file that is bundled with all Retail Demo Store deployments. Therefore there
are no deployment or run-time dependencies on this script.
"""

import json
import csv
import uuid
import random
import gzip
from scipy.stats import truncnorm
from faker import Faker

fake = Faker()
num_users = 5000
users = []

# Normally distribute ages between 18 and 100 with a mean age of 32.
age_min = 18
age_max = 100
age_mean = 32
age_sd = 15

age_dist = truncnorm((age_min - age_mean) / age_sd, (age_max - age_mean) / age_sd, loc=age_mean, scale=age_sd)

# Persona combinations ordered from strongest affinity to latent interest.
personas = [
    'apparel_housewares_accessories', 'housewares_apparel_electronics',
    'footwear_outdoors_apparel', 'outdoors_footwear_housewares',
    'electronics_beauty_outdoors', 'beauty_electronics_accessories',
    'jewelry_accessories_beauty', 'accessories_jewelry_apparel'
]

print('Generating {} random users...'.format(num_users))

for x in range(0, num_users):

    gender = random.choice(['M', 'F'])

    if gender == 'F':
        first_name = fake.first_name_female()
        last_name = fake.last_name_female()
    else:
        first_name = fake.first_name_male()
        last_name = fake.last_name_male()

    address_state = fake.state_abbr(include_territories=True)

    person = {
        'id': str(x),
        'first_name': first_name,
        'last_name': last_name,
        'gender': gender,
        'email': '{}.{}@example.com'.format(first_name.replace(' ', '').lower(), last_name.replace(' ', '').lower()),
        'username': 'user{}'.format(x),
        'age': int(age_dist.rvs()),
        'persona': random.choice(personas),
        'addresses': [
            {
                'first_name': first_name,
                'last_name': last_name,
                'address1': fake.street_address(),
                'address2': '',
                'country': 'US',
                'city': fake.city(),
                'state': address_state,
                'zipcode': fake.postcode_in_state(state_abbr=address_state),
                'default': True
            }
        ],
    }

    users.append(person)

# Write users array as a compressed JSON file.
print('Writing users to compressed JSON file...')
with gzip.GzipFile('users.json.gz', 'w') as fout:
    fout.write(json.dumps(users, indent=2).encode('utf-8')) 

print('Done')