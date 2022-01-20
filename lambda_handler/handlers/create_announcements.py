import json
import logging
import trafaret as t
from botocore.exceptions import ClientError
from .schemas import AnnouncementsTableSchema
from .handler_helpers import generate_json_response

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def create_announcement(event: dict, table) -> dict:
    """
    :param event: Lambda event object
    :param table: DynamoDb table object
    :return: response object
    """
    body = {}
    if event.get("body"):
        body = json.loads(event.get("body"))
    try:
        validated = AnnouncementsTableSchema.check(body)
    except t.DataError as e:
        logger.exception(f"[Create announcement. ValidationError]: {e}")
        return generate_json_response(400, {"message": "invalid input, object invalid"})

    try:
        table.put_item(
            Item=validated, ConditionExpression="attribute_not_exists(title)"
        )
        return generate_json_response(201, {"message": "item created"})

    except ClientError as e:
        logger.exception(f"[DynamoDb ClientError]: {e}")
        if e.response["Error"]["Code"] == "ConditionalCheckFailedException":
            return generate_json_response(409, {"message": "an item already exists"})
        return generate_json_response(500, {"message": "Something went wrong"})
    except Exception as e:
        logger.exception(f"[Unexpected error]: {e}")
        return generate_json_response(500, {"message": "Something went wrong"})
