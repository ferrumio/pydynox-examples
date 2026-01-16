"""DynamoDB models for URL Shortener."""

import os

from pydynox import DynamoDBClient, Model, ModelConfig, set_default_client
from pydynox.attributes import NumberAttribute, StringAttribute, TTLAttribute
from pydynox.generators import AutoGenerate

# Setup client from environment
_endpoint_url = os.environ.get("DYNAMODB_ENDPOINT_URL")
if _endpoint_url:
    # Local development with LocalStack
    client = DynamoDBClient(
        region="us-east-1",
        endpoint_url=_endpoint_url,
        access_key="testing",
        secret_key="testing",
    )
else:
    # AWS
    client = DynamoDBClient()

set_default_client(client)


class ShortUrl(Model):
    """A shortened URL with expiry and click tracking."""

    model_config = ModelConfig(table=os.environ.get("TABLE_NAME", "urls"))

    short_code = StringAttribute(hash_key=True, default=AutoGenerate.KSUID)
    original_url = StringAttribute()
    clicks = NumberAttribute(default=0)
    expires_at = TTLAttribute()
