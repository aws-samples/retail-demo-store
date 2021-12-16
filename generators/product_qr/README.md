# Product QR Code Generator

The script `generate_qr.py` can be used to generate QR codes which can be recognised by the product scanning functionality in the Retail Demo Store web UI.  

## Usage

`python generate_qr.py <product_ids>`

Generated QR codes will be output to the `codes` directory as `.png` files. A warning message will be displayed if any product IDs were not recognised.