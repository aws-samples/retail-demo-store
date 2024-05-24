from fastapi import FastAPI
from pynamodb.models import Model
from pynamodb.attributes import UnicodeAttribute, NumberAttribute, UTCDateTimeAttribute, BooleanAttribute
from pynamodb.indexes import GlobalSecondaryIndex, AllProjection

app = FastAPI()

class AddressGlobalIndex(GlobalSecondaryIndex):
    class Meta:
        index_name = "address-index"
        projection = AllProjection()
    postal_code = NumberAttribute(hash_key=True)

class Address(Model):
    class Meta:
        table_name = "addresses"
        region = "us-east-1"
        
    address_id = UnicodeAttribute(hash_key=True)
    street_address = UnicodeAttribute()
    city = UnicodeAttribute()
    state = UnicodeAttribute()
    country = UnicodeAttribute()
    postal_code = NumberAttribute(null=False)
    
    address_global_index = AddressGlobalIndex()
    
class User(Model):
    class Meta:
        table_name = "users"
        region = "us-east-1"
        
    id = UnicodeAttribute(hash_key=True)
    username = UnicodeAttribute()
    email = UnicodeAttribute()
    first_name = UnicodeAttribute()
    last_name = UnicodeAttribute()
    addresses = UnicodeAttribute()
    age = NumberAttribute()
    gender = UnicodeAttribute()
    persona = UnicodeAttribute()
    discount_persona = UnicodeAttribute()
    sign_up_date = UTCDateTimeAttribute()
    selectable_user = BooleanAttribute()
    last_sign_in_date = UTCDateTimeAttribute(null=True)
    identity_id = UnicodeAttribute(null=True)
    phone_number = UnicodeAttribute(null=True)

if __name__ == "__main__":
    User.create_table(billing_mode="PAY_PER_REQUEST")
    Address.create_table(billing_mode="PAY_PER_REQUEST")
