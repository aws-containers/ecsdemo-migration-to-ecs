from pynamodb.models import Model
from pynamodb.attributes import UnicodeAttribute
from os import getenv

def get_region():
    from requests import get
    from json import loads
    try:
        region = loads(get(f'{getenv("ECS_CONTAINER_METADATA_URI_V4")}/task').text).get('AvailabilityZone')[:-1]
        #region = loads(get('http://169.254.169.254/latest/dynamic/instance-identity/document').text).get('region')
    except:
        region = 'us-west-2'
    return region

class UserModel(Model):
    """
    User table
    """
    class Meta:
        table_name = getenv('DYNAMO_TABLE')
        region = get_region()
        
    email = UnicodeAttribute(null=True)
    phone = UnicodeAttribute(null=True)
    first_name = UnicodeAttribute(hash_key=True)
    last_name = UnicodeAttribute(range_key=True)
