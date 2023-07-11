# This script displays the environment variables that the python tests will use from the src/.env file
import os

from dotenv import load_dotenv
load_dotenv()

print("#######################################################")
print("### Starting integration tests...")
print("#######################################################")
print("### List of API URLs in the environment variable from ~/src/.env")
print("#######################################################")
print("# PRODUCTS_API_URL = %s" % os.getenv("PRODUCTS_API_URL"))
print("# USERS_API_URL = %s" % os.getenv("USERS_API_URL"))
print("# ORDERS_API_URL = %s" % os.getenv("ORDERS_API_URL"))
print("# RECOMMENDATIONS_API_URL = %s" % os.getenv("RECOMMENDATIONS_API_URL"))
print("# CARTS_API_URL = %s" % os.getenv("CARTS_API_URL"))
print("# Empty values will be defaulted to local URL")
print("########################################")
