import dotenv
import os
import sys

"""
This file accepts 2 command line arguments:
1. The key of the value we are overwriting in the dotenv file (i.e. ORDERS_API_URL)
2. The new value of that key
"""
key = sys.argv[1]
new_value = sys.argv[2]

dotenv_file = dotenv.find_dotenv()
dotenv.load_dotenv(dotenv_file)

os.environ[key] = new_value
dotenv.set_key(dotenv_file, key, os.environ[key])
