from pynamodb.models import Model
from pynamodb.attributes import UnicodeAttribute

class UserModel(Model):
    """
    User table
    """
    class Meta:
        table_name = "demoAppUsers"
        region = "us-west-2"
        
    email = UnicodeAttribute(null=True)
    phone = UnicodeAttribute(null=True)
    first_name = UnicodeAttribute(hash_key=True)
    last_name = UnicodeAttribute(range_key=True)
