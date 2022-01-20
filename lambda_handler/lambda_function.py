import os
import logging

import boto3
from handlers import (
    create_announcement,
    get_announcements,
    generate_json_response,
)

logger = logging.getLogger()
logger.setLevel(logging.INFO)


# Get the service resource.
dynamodb = boto3.resource("dynamodb")

# set environment variable
TABLE_NAME = os.environ.get("TABLE_NAME", "default")

method_mapping = {"GET": get_announcements, "POST": create_announcement}


def lambda_handler(event, context):
    table = dynamodb.Table(TABLE_NAME)
    request_method = event.get("httpMethod")
    logger.info(f"[LAMBDA EVENT]: {event}")
    if request_method in method_mapping:
        return method_mapping[request_method](event, table)
    return generate_json_response(405, {"message": "Method not allowed"})
