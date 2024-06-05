from pynamodb.models import Model
from pynamodb.indexes import GlobalSecondaryIndex, AllProjection
from pynamodb.attributes import UnicodeAttribute, NumberAttribute, UTCDateTimeAttribute, BooleanAttribute, MapAttribute, ListAttribute
import os
class UsernameIndex(GlobalSecondaryIndex):
    """
    A Global Secondary Index to be used for querying by username.
    """
    class Meta:
        index_name = 'username-index'
        projection = AllProjection()

    username = UnicodeAttribute(hash_key=True)

class IdentityIdIndex(GlobalSecondaryIndex):
    """
    A Global Secondary Index to be used for querying by identity_id.
    """
    class Meta:
        index_name = 'identity_id-index'
        projection = AllProjection()

    identity_id = UnicodeAttribute(hash_key=True)
    
    
class Address(MapAttribute):
    first_name = UnicodeAttribute()
    last_name = UnicodeAttribute()
    address1 = UnicodeAttribute() 
    address2 = UnicodeAttribute()
    city = UnicodeAttribute()
    state = UnicodeAttribute()
    country = UnicodeAttribute()
    zipcode = UnicodeAttribute()
    default = BooleanAttribute()

    def to_dict(self):
        """Serializes Address to a dictionary."""
        return {
            'first_name': self.first_name,
            'last_name': self.last_name,
            'address1': self.address1,
            'address2': self.address2,
            'city': self.city,
            'state': self.state,
            'country': self.country,
            'zipcode': self.zipcode,
            'default': self.default
        }

class User(Model):
    class Meta:
        table_name = os.getenv("DDB_TABLE_USERS", "users")
        region = os.getenv("AWS_REGION", "us-west-2")
        if os.getenv("DDB_ENDPOINT_OVERRIDE"):
            host = os.getenv("DDB_ENDPOINT_OVERRIDE")

    username_index = UsernameIndex()
    identity_id_index = IdentityIdIndex()
    id = UnicodeAttribute(hash_key=True)
    username = UnicodeAttribute()
    email = UnicodeAttribute()
    first_name = UnicodeAttribute(null=True)
    last_name = UnicodeAttribute(null=True)
    addresses = ListAttribute(of=Address)  
    age = NumberAttribute(default=0)
    gender = UnicodeAttribute(null=True)
    persona = UnicodeAttribute(null=True)
    discount_persona = UnicodeAttribute(null=True)
    sign_up_date = UTCDateTimeAttribute(null=True)
    selectable_user = BooleanAttribute(null=True)
    last_sign_in_date = UTCDateTimeAttribute(null=True)
    identity_id = UnicodeAttribute(null=True)
    phone_number = UnicodeAttribute(null=True)

    def to_dict(self):
        """Serializes User to a dictionary, including nested Address objects."""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'addresses': [address.to_dict() for address in self.addresses] if self.addresses else [],
            'age': self.age,
            'gender': self.gender,
            'persona': self.persona,
            'discount_persona': self.discount_persona,
            'sign_up_date': self.sign_up_date.isoformat() if self.sign_up_date else None,
            'selectable_user': self.selectable_user,
            'last_sign_in_date': self.last_sign_in_date.isoformat() if self.last_sign_in_date else None,
            'identity_id': self.identity_id,
            'phone_number': self.phone_number
        }

