# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
from dynamo_setup import dynamo_resource,ddb_table_personalised_product_descriptions,ddb_table_products
from server import app
import os
import boto3
import requests
import json

class PersonalisedDescriptionGenerator():
    
    users_api_url = os.environ.get("USERS_API_URL")
    users_service_host = os.environ.get('USERS_SERVICE_HOST')
    users_service_port = os.environ.get('USERS_SERVICE_PORT', 80)
    dynamo_client = dynamo_resource.meta.client
    bedrock = None
    
    @classmethod
    def initialise_bedrock(cls):
        if not cls.bedrock:
            session = boto3.Session()
            cls.bedrock = session.client('bedrock-runtime')
    
    @classmethod
    def set_user_service_host_and_port(cls):
        if not cls.users_api_url:
            app.logger.info("USERS_API_URL not found in env variables- if developping locally please check .env")
            if not cls.users_service_host:
                servicediscovery = boto3.client('servicediscovery')
                try:
                    response = servicediscovery.discover_instances(
                    NamespaceName='retaildemostore.local',
                    ServiceName='users',
                    MaxResults=1,
                    HealthStatus='HEALTHY'
                    )
                except Exception as e:
                    app.logger.info(f"Error retrieving users host using servicediscovery: {e}")
                    raise
                cls.users_service_host = response['Instances'][0]['Attributes']['AWS_INSTANCE_IPV4']
            cls.users_api_url = f'http://{cls.users_service_host}:{cls.users_service_port}'
    
    @classmethod
    def setup(cls):
        try:
            cls.initialise_bedrock()
        except Exception as e:
            app.logger.info(f"Error initialising bedrock: {e}")
        try:
            cls.set_user_service_host_and_port()
        except Exception as e:
            app.logger.info(f"Error setting user service host and port: {e}")
            
    @classmethod
    def get_user(cls, user_id):
        url = f"{cls.users_api_url}/users/{user_id}"
        response = requests.get(url)
        if response.ok:
            return response.json()
        app.logger.info(f"Error retrieving user info from {url}")
        return None
    
    @classmethod
    def get_product(cls, product_id):
        product_id = str(product_id.lower())
        app.logger.info(f"Retrieving product with id: {product_id}")
        try:
            response = cls.dynamo_client.get_item(
                TableName=ddb_table_products,
                Key={
                    'id': product_id
                }
            )
            app.logger.info(f"Retrieved product: {response}")
        except Exception as e:
            app.logger.info(f"Error retrieving product with id: {product_id}")
            raise e
        if 'Item' in response:
            return response['Item']
        
    @classmethod
    def generate_prompt(cls, product, user) -> str:
        description = product.get('description', '')
        product_name = product.get('name', '')
        product_category = product.get('category', '')
        product_style = product.get('style', '')
        user_age = user.get('age', '')
        user_persona = user.get('persona', '')
        template = (
            f"Given the following user details:\n"
            f"- User Age: {user_age}\n"
            f"- User Interests: {user_persona}\n"
            f"Given the following product details:\n"
            f"- Original Description: {description}\n"
            f"- Product Name: {product_name}\n"
            f"- Product Category: {product_category}\n"
            f"- Product Style: {product_style}\n"
            f"Please generate an enhanced and product description personalised for the user"  
            f"that incorporates all the above elements while ensuring "
            f"high-quality language and factual coherence. Make the description rich in relevant details "
            f"and present it in a format that includes:\n"
            f"- A compelling opening sentence\n"
            f"- Key features\n"
            f"- Benefits\n"
            f"- Usage instructions\n"
            f"- Pricing information\n\n"
        )
        return template
    
    @staticmethod
    def getAgeRange(age: int) -> str:
        age_ranges = [
            (18, ""),
            (25, "18-24"),
            (35, "25-34"),
            (45, "35-44"),
            (55, "45-54"),
            (70, "55-69"),
            (float('inf'), "70-and-above"),
        ]
    
        for limit, label in age_ranges:
            if age < limit:
                return label

    @classmethod
    def generate_key(cls, user) -> str:
        user_age = int(user.get('age', ''))
        age_range = cls.getAgeRange(user_age)
        user_persona = user.get('persona', '')
        return f"{user_persona}-{age_range}"
    
    @classmethod
    def check_ddb_cache(cls, persona_key):
        try:
            response = cls.dynamo_client.get_item(
                TableName=ddb_table_personalised_product_descriptions,
                Key={
                    'id': persona_key
                }
            )
        except Exception as e:
            app.logger.info(f"Error retrieving personalised product description from DDB: {e}")
            raise e
        if 'Item' in response:
            return response['Item']['generated_description']
    
    @classmethod
    def cache_generated_description(cls, persona_key, generated_description):
        try:
            cls.dynamo_client.put_item(
                TableName=ddb_table_personalised_product_descriptions,
                Item={
                    'id': persona_key,
                    'generated_description': generated_description
                }
            )
        except Exception as e:
            app.logger.info(f"Error caching generated description for user: {persona_key}")
            raise e
    
    @classmethod
    def generate_personalised_description(cls, productid, userid) -> str:
        product = cls.get_product(productid)
        user = cls.get_user(userid)
        persona_key = cls.generate_key(user)
        cached_description = cls.check_ddb_cache(persona_key)
        if cached_description:
            return cached_description
        prompt = cls.generate_prompt(product, user)
        claude_prompt = f"\n\nHuman:{prompt}\n\nAssistant:"
        body = json.dumps({
            "prompt": claude_prompt,
            "max_tokens_to_sample":2000,
            "temperature":0,
            "top_p":1,
            "stop_sequences": ["\n\nHuman:"],
            "top_k": 250
        })
        modelId = 'anthropic.claude-v2'
        accept = 'application/json'
        contentType = 'application/json'
        response = cls.bedrock.invoke_model(
            body=body,
            modelId=modelId,
            accept=accept,
            contentType=contentType)
        response_body = json.loads(response.get('body').read())
        if 'Sorry' in response_body.get('completion'):
            app.logger.info('No description can be generated for product')
            return ''
    
        generated_description = ' '.join(response_body.get('completion').split('\n',2)[2:])
        cls.cache_generated_description(
            persona_key=persona_key,
            generated_description=generated_description
            )
        return generated_description
