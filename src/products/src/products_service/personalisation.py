# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
from abc import ABC, abstractmethod
from flask import current_app
import boto3
import json

bedrock = boto3.client('bedrock-runtime')

class Cache(ABC):

    @abstractmethod
    def get(self, key: str):
        pass
    
    @abstractmethod
    def put(self, key: str, obj):
        pass

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

def generate_prompt(product, user_persona,user_age_range) -> str:
    description = product.get('description', '')
    product_name = product.get('name', '')
    product_category = product.get('category', '')
    product_style = product.get('style', '')
    user_persona = ",".join(user_persona.split('_'))

    instructions = (
        f"Please generate an enhanced product description personalised for a customer aged {user_age_range}, interested in {user_persona}. "
        f"However, do not mention their age in the rewrite. "
        f"The product is named \"{product_name}\" and is a product of type \"{product_style}\" in the {product_category} category."
    )

    template = (
        f"I'd like you to rewrite the following paragraph using the following instructions:\n"
        f"\"{instructions}\"\n"
        f"\n"
        f"\"{description}\"\n\n"
        f"Please put your rewrite in <p></p> tags."
    )
    return template

def create_claude_request(prompt:str) -> str:
    return json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 300,
        "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            }
                        ]
                    }
        ],
        "temperature": 0,
        "top_p": 1,
        "top_k": 250,
    })

def generate_personalised_description(product, user, cache: Cache) -> str:
    user_age_range = getAgeRange(user.get('age'))
    user_persona = user.get('persona')

    def get_personalised_description() -> (bool, str):
        prompt = generate_prompt(product, user_persona,user_age_range)
        body = create_claude_request(prompt)
        current_app.logger.debug(f"Generated request:\n{body}")
        
        response = bedrock.invoke_model(
            body=body, 
            modelId="anthropic.claude-3-haiku-20240307-v1:0",
            accept="application/json", 
            contentType="application/json"
        )
        response_body = json.loads(response['body'].read())
        response_text = response_body.get("content")[0].get("text")
        
        if 'Sorry' in response_text:
            current_app.logger.info(f"No personalised description can be generated for product: {product['id']}")
            return False, ''
        
        current_app.logger.debug(f"Response:\n{response_text}")
        return True, response_text
    
    cache_key = generate_key(user_persona, user_age_range, product['id'])
    return with_cache(cache_key, cache, get_personalised_description)

def with_cache(cache_key: str, cache: Cache, func):
    if current_app.config['CACHE_PERSONALISED_PRODUCTS']:
        cached_description = cache.get(cache_key)
        if cached_description:
            return cached_description
        
    cache_response, response = func()
        
    if current_app.config['CACHE_PERSONALISED_PRODUCTS'] and cache_response:
        cache.put(cache_key, response)
        
    return response

def generate_key(user_persona, user_age_range, product_id) -> str:
    return f"{user_persona}-{user_age_range}-{product_id}"