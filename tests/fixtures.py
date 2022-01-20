from botocore.exceptions import ClientError

get_event = {
    "httpMethod": "GET",
    "queryStringParameters": {"skip": 1, "limit": 10},
}

get_data_scan_mock = {"Items": []}

post_event_valid_mock = {
    "httpMethod": "POST",
    "queryStringParameters": {},
    "body": "{"
    '"date" : "2000-01-23T04:56:07.000+00:00",\n'
    '  "description" : "Description of ther announceement",'
    '\n  "title" : "Widget Adapter"\n'
    "}",
}

post_event_invalid_mock = {
    "httpMethod": "POST",
    "queryStringParameters": {},
    "body": "{"
    '"date" : "2000-01-23T04:56:07.000+00:00",\n'
    '  "description2" : "Description of ther announceement",'
    '\n  "title" : "Widget Adapter"\n'
    "}",
}


class Table:
    @staticmethod
    def scan(*args, **kwargs):
        return {"Items": [""]}

    @staticmethod
    def put_item(*args, **kwargs):
        return "success"


class TableWithErrors:
    @staticmethod
    def scan(*args, **kwargs):
        raise ClientError({}, "operation_name")

    @staticmethod
    def put_item(*args, **kwargs):
        raise ClientError(
            {"Error": {"Code": "ConditionalCheckFailedException"}}, "operation_name"
        )
