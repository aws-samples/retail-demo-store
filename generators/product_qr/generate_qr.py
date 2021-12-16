import argparse
import json
import qrcode
import os
import yaml

parser = argparse.ArgumentParser()
parser.add_argument('product_ids', nargs='+', help='List of IDs of products to generate QR codes for')
args = parser.parse_args()

base_path = os.path.dirname(os.path.realpath(__file__))
products_path = os.path.normpath(base_path + '/../../src/products/src/products-service/data/products.yaml')
products = yaml.safe_load(open(products_path).read())

img_dir = os.path.join(base_path, 'codes')
os.makedirs(img_dir, exist_ok=True)
for product in products:
    if product['id'] in args.product_ids:
        img = qrcode.make(json.dumps(product))
        img_path = os.path.join(img_dir, f'{product["id"]}.png')
        img.save(img_path)
        args.product_ids.remove(product['id'])
        print(f'QR code generated for product with ID: {product["id"]}')

if args.product_ids:
    print('\nWARNING: The following product ID(s) do not exist:')
    print('-', ', '.join(args.product_ids))
else:
    print('QR codes generated for all requested IDs.')
