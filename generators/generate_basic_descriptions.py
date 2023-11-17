import os
import boto3
from tqdm import tqdm
import yaml
import json
import shutil


bedrock = boto3.client(service_name='bedrock-runtime')

def write_yaml(products):
    with open("products_new.yaml", 'w') as stream:
        try:
            yaml.safe_dump(products, stream, sort_keys=False)
        except yaml.YAMLError as exc:
            print(exc)



def call_model(prompt):
    body = json.dumps(
        {"prompt": prompt
        , "max_tokens_to_sample" : 300  
         
         })
    modelId = 'anthropic.claude-v2'
    accept = 'application/json'
    contentType = 'application/json'
    response = bedrock.invoke_model(
        body=body, 
        modelId=modelId, 
        accept=accept,
        contentType=contentType)
    response_body = json.loads(response.get('body').read())

    # text
    if(response_body['completion'].find(":")>0):
        return(response_body['completion'].split(":")[1].strip())
    else:
        return(response_body['completion'].strip())


def generate_description(index):

    prompt = f"""Human: Consider this product information 
    {products[index]}

    Create an engaging product description in 35 words for the product listed above, make it professional
    Assistant:
    """

    products[index]['description']= call_model(prompt)


def generate_title(index):

    prompt = f"""Human: Consider this product information 
    {products[index]}

    create a more original and engaging title for the product in about 5 words listed above, the title shouldn't be a duplicate
    Assistant:
    """

    products[index]['name'] =  call_model(prompt)

if not os.path.isfile('products_new.yaml'):
    shutil.copy2('../src/products/src/products-service/data/products.yaml', 'products_new.yaml') # complete target filename given

with open("products_new.yaml", 'r') as stream:
    try:
        products=yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc)
    


def generate_improved_product(index):
    # skip already generated products (resume capacity!)
    if 'generated' not in products[index]:
        generate_description(index)
        generate_title(index)
        products[index]['generated']='YES'
        if (index%20==0):
            write_yaml(products)
    

print("** generating new products info descriptions and title**")
for i in tqdm(range(len(products))):
    generate_improved_product(i)

