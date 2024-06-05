from pynamodb.models import Model
from pynamodb.indexes import GlobalSecondaryIndex, AllProjection
from pynamodb.attributes import UnicodeAttribute, NumberAttribute, UTCDateTimeAttribute, BooleanAttribute, MapAttribute, ListAttribute
from datetime import datetime
import pytz
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
    first_name = UnicodeAttribute(default="")
    last_name = UnicodeAttribute(default="")
    addresses = ListAttribute(of=Address)
    age = NumberAttribute(default=0)
    gender = UnicodeAttribute(null=True)
    persona = UnicodeAttribute(default="")
    discount_persona = UnicodeAttribute(default="")
    sign_up_date = UTCDateTimeAttribute(null=True)
    selectable_user = BooleanAttribute(null=True)
    last_sign_in_date = UTCDateTimeAttribute(null=True)
    identity_id = UnicodeAttribute(null=True)
    phone_number = UnicodeAttribute(default="")

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

    def preprocess_datetime_fields(self):
        """Convert string representation of datetime to datetime objects for relevant fields."""
        datetime_fields = ['sign_up_date', 'last_sign_in_date']
        for field in datetime_fields:
            value = getattr(self, field, None)
            if isinstance(value, str):
                setattr(self, field, self.parse_iso_datetime(value))

    @staticmethod
    def parse_iso_datetime(date_str):
        """Convert ISO 8601 string to datetime object."""
        try:
            return datetime.fromisoformat(date_str.replace('Z', '+00:00')).astimezone(pytz.utc)
        except ValueError as e:
            print(f"Error parsing date: {e}")
            return None

    def save(self,**expected_values):
        """Override save to preprocess datetime fields."""
        self.preprocess_datetime_fields()
        super(User, self).save(**expected_values)