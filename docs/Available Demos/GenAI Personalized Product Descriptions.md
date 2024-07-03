---
weight: 7
---
# Personalized Product Descriptions with GenAI

## Overview

Generative AI can be used to automate the creation of marketing content, including generating personalized product descriptions. This can save marketers significant time and effort, allowing them to focus on other aspects of their strategy.

The real power of generative AI for product descriptions is the ability to dynamically create unique, personalized content for each customer segment or individual user. Previously, marketers would need to manually generate multiple copies of product descriptions for different customer attributes. Generative AI can automate this process, providing opportunities to tailor the descriptions to each user's preferences and context.

## Implementation in the Retail Demo Store

The Retail Demo Store integrates the product service with Amazon Bedrock to retrieve personalized product descriptions based on the logged-in user's age and interests.

Amazon Bedrock makes Foundation Models (FMs) accessible via an API, and in this demo, Anthropic's Claude v2 is the underlying FM used for generating the personalized descriptions.

The prompt used to generate the personalized descriptions takes the following form:

```
I'd like you to rewrite the following paragraph using the following instructions:
"{instructions}"

"{original product description}"

Please put your rewrite in <p></p> tags.
```

The instructions used are:

```
Please generate an enhanced product description personalised for a customer aged {age range}, interested in {interests}.
However, do not mention their age in the rewrite. 
The product is named "{product name}" and is a product of type "{product type}" in the {product category} category.
```

This allows the generative AI model to dynamically create a personalized product description based on the user's age and interests, without explicitly mentioning those details.

## Architecture

The overall architecture of this demo involves the following components:

1. The user authenticates with Amazon Cognito and obtains an identity token, which is passed to subsequent API requests.
2. The Web UI uploads a product image to S3 and calls the API Gateway to request a personalized product description.
3. The API Gateway validates the identity token and proxies the request to a Lambda function.
4. The Lambda function retrieves the user's age and interests from the identity token, constructs the prompt, and calls Amazon Bedrock to generate the personalized description.
5. The generated description is returned to the Web UI for display.

By integrating Generative AI through Amazon Bedrock, the Retail Demo Store is able to provide personalized product descriptions that are tailored to each individual user, improving the overall shopping experience.