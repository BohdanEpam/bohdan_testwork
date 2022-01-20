import logging
from botocore.exceptions import ClientError
import trafaret as t
from .schemas import RequestQueryParamsSchema
from .handler_helpers import generate_json_response

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def get_data(table, skip: int, limit: int) -> list:
    """
    :param table: DynamoDb table object
    :param skip: number of records to skip for pagination format: int32
    :param limit: maximum number of records to return format: int32
    :return:
    """
    scan_limiting = skip + limit
    response = table.scan(Limit=scan_limiting) if limit else table.scan()
    data = response["Items"]
    is_limited = bool(limit)
    conditions_map = {
        True: "LastEvaluatedKey" in response and len(data) < scan_limiting,
        False: "LastEvaluatedKey" in response,
    }

    # Scan has 1 MB limit on the amount of data it will return in a request, so we need to paginate through them.
    # However, in this case of 'limit', we don't scan the entire table, but only scan the number of items that we need.
    while conditions_map[is_limited]:
        scan_kwargs = {"ExclusiveStartKey": response["LastEvaluatedKey"]}

        if limit:
            scan_kwargs["Limit"] = scan_limiting

        response = table.scan(**scan_kwargs)
        data.extend(response["Items"])
    return data[skip:scan_limiting] if limit else data[skip:]


def get_announcements(event: dict, table) -> dict:
    """
    :param event: Lambda event object
    :param table: DynamoDb table object
    :return: response object
    """
    query_params = event.get("queryStringParameters") or {}
    try:
        query_params = RequestQueryParamsSchema.check(query_params)
    except t.DataError as e:
        logger.exception(f"[Get announcements. ValidationError]: {e}")
        return generate_json_response(400, {"message": "bad input parameter"})

    skip, limit = query_params.get("skip", 0), query_params.get("limit", 0)
    try:
        return generate_json_response(200, get_data(table, skip, limit))
    except ClientError as e:
        logger.exception(f"[DynamoDb ClientError]: {e}")
        return generate_json_response(500, {"message": "Something went wrong"})
    except Exception as e:
        logger.exception(f"[Unexpected error]: {e}")
        return generate_json_response(500, {"message": "Something went wrong"})
