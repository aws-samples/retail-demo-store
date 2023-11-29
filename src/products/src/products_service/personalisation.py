# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
from abc import ABC, abstractmethod
from flask import current_app
from anthropic_bedrock import AnthropicBedrock
import anthropic_bedrock

from products_service import users

bedrock = AnthropicBedrock()

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
    template = (
        f"Given the following user details:\n"
        f"- User Age Range: {user_age_range}\n"
        f"- User Interests: {user_persona}\n"
        f"Given the following product details:\n"
        f"- Original Description: {description}\n"
        f"- Product Name: {product_name}\n"
        f"- Product Category: {product_category}\n"
        f"- Product Type: {product_style}\n"
        f"Please generate an enhanced product description personalised for the user "  
        f"that incorporates all the above elements while ensuring "
        f"high-quality language and factual coherence. Make the description rich in relevant details "
        f"and present it in a format that includes:\n"
        f"- A compelling opening sentence\n"
        f"- Key features\n"
        f"- Benefits\n"
        f"- Each paragraph generated should be in xml format, like so: <p>Paragraph here</p>\n"
    )
    current_app.logger.debug(f"Generated prompt: {template}")
    return template

def generate_personalised_description(product, user_id, cache: Cache) -> str:
    user = users.get(user_id)
    user_age_range = getAgeRange(user.get('age'))
    user_persona = user.get('persona')

    def get_personalised_description() -> (bool, str):
        prompt = generate_prompt(product, user_persona,user_age_range)
        claude_prompt = f"{anthropic_bedrock.HUMAN_PROMPT} {prompt} {anthropic_bedrock.AI_PROMPT}"
        response = bedrock.completions.create(
                    model="anthropic.claude-v2",
                    max_tokens_to_sample=300,
                    prompt=claude_prompt,
                    top_p=1,
                    top_k=250)
        
        if 'Sorry' in response.completion:
            current_app.logger.info(f"No personalised description can be generated for product: {product['id']}")
            return False, ''

        return True, ' '.join(response.completion.split('\n',2)[2:])
    
    cache_key = generate_key(user_persona, user_age_range, product['id'])
    return with_cache(cache_key, cache, get_personalised_description)

def with_cache(cache_key: str, cache: Cache, func):
    if current_app.config['CACHE_PERSONALISED_PRODUCTS']:
        cached_description = cache.get(cache_key)
        if cached_description:
            return cached_description
        
        cache_response, response = func()
        
        if cache_response:
            cache.put(cache_key, response)
        
        return response

    return func()


def generate_key(user_persona, user_age_range, product_id) -> str:
    return f"{user_persona}-{user_age_range}-{product_id}"