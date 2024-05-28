from pynamodb.models import Model
from pynamodb.attributes import UnicodeAttribute, NumberAttribute, UTCDateTimeAttribute, BooleanAttribute
from pynamodb.indexes import GlobalSecondaryIndex, AllProjection
import os
class AddressGlobalIndex(GlobalSecondaryIndex):
    class Meta:
        index_name = "address-index"
        projection = AllProjection()
    postal_code = NumberAttribute(hash_key=True)

class Address(Model):
    class Meta:
        table_name = os.getenv("ADDRESS_TABLE", "addresses")
        region = os.getenv("AWS_REGION","us-west-2")
        ddb_endpoint_override = os.getenv("DDB_ENDPOINT_OVERRIDE")
        if ddb_endpoint_override:
            host = ddb_endpoint_override

        
        
    address_id = UnicodeAttribute(hash_key=True)
    street_address = UnicodeAttribute()
    city = UnicodeAttribute()
    state = UnicodeAttribute()
    country = UnicodeAttribute()
    postal_code = NumberAttribute(null=False)
    
    address_global_index = AddressGlobalIndex()
    
class User(Model):
    class Meta:
        table_name = os.getenv("USER_TABLE", "users")
        region = os.getenv("AWS_REGION","us-west-2")
        ddb_endpoint_override = os.getenv("DDB_ENDPOINT_OVERRIDE")
        if ddb_endpoint_override:
            host = ddb_endpoint_override
        
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
