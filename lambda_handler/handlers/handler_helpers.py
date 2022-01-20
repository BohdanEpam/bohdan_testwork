import json
from typing import Any


def generate_json_response(status_code: int, body: Any) -> dict:
    """
    :param status_code: response status code
    :param body: response body - dict/list/int, flot, etc.
    :return: dict object with prepared response structure, with all headers
    """
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
        },
        "body": json.dumps(body),
    }
