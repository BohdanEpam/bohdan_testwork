from botocore.exceptions import ClientError
import trafaret as t
from .schemas import RequestQueryParamsSchema
from .handler_helpers import generate_json_response


def get_all_data(table, skip: int) -> list:
    """
    :param table: DynamoDb table object
    :param skip: number of records to skip for pagination format: int32
    :return:
    """
    response = table.scan()
    data = response["Items"]
    # Scan has 1 MB limit on the amount of data it will return in a request, so we need to paginate through the
    # results in a loop
    while "LastEvaluatedKey" in response:
        response = table.scan(ExclusiveStartKey=response["LastEvaluatedKey"])
        data.extend(response["Items"])

    return data[skip:]


def get_limited_data(table, skip: int, limit: int) -> list:
    """
    :param table: DynamoDb table object
    :param skip: number of records to skip for pagination format: int32
    :param limit: maximum number of records to return format: int32
    :return:
    """
    scan_limiting = skip + limit
    response = table.scan(Limit=scan_limiting)
    data = response["Items"]
    # Scan has 1 MB limit on the amount of data it will return in a request, so we need to paginate through them.
    # However, in this case, we don't scan the entire table, but only scan the number of items that we need.
    while "LastEvaluatedKey" in response and len(data) < scan_limiting:
        response = table.scan(
            ExclusiveStartKey=response["LastEvaluatedKey"], Limit=scan_limiting
        )
        data.extend(response["Items"])
    return data[skip:scan_limiting]


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
        return generate_json_response(400, {"message": "bad input parameter"})

    skip, limit = query_params.get("skip", 0), query_params.get("limit", 0)
    try:
        if limit:
            return generate_json_response(200, get_limited_data(table, skip, limit))
        return generate_json_response(200, get_all_data(table, skip))
    except ClientError as e:
        return generate_json_response(
            500,
            {
                "message": e.response.get("Error", {}).get(
                    "Message", "Something went wrong"
                )
            },
        )
    except Exception as e:
        return generate_json_response(500, {"message": f"Something went wrong: {e}"})
