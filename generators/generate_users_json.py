# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

""" 
Generates list of random users using the datagenerator library included in
this directory.

The random users are written to a gzipped JSON file which, when copied 
into place, will be loaded by the Users microservice during initialization.

This script only needs to be run once to produce a random users data 
file that is bundled with all Retail Demo Store deployments. 
"""

from datagenerator.users import UserPool 

num_users = 6000

print('Generating {} random users...'.format(num_users))

pool = UserPool.new_file('users.json.gz', num_users)

print('Done')