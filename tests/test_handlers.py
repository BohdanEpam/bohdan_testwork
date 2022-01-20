import copy
import os
import sys
import inspect
import json
import unittest

from unittest.mock import patch
import tests.fixtures as fixtures
import logging

current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)

new_parent_dir = "{}/lambda_handler".format(os.path.dirname(current_dir))
sys.path.insert(0, new_parent_dir)

from lambda_handler.lambda_function import lambda_handler

logger = logging.getLogger()


class HandlersTestCases(unittest.TestCase):
    def setUp(self) -> None:
        self.dynamo_table = patch(
            "lambda_handler.lambda_function.dynamodb.Table", return_value=fixtures.Table
        )
        self.dynamo_table.start()
        self.get_event_success = fixtures.get_event
        self.get_event_failed = copy.deepcopy(fixtures.get_event)
        self.get_event_failed["queryStringParameters"] = {"skip": "abc"}

        self.post_event_success = fixtures.post_event_valid_mock
        self.post_event_failed = fixtures.post_event_invalid_mock

    def tearDown(self) -> None:
        patch.stopall()

    def test_get_announcements_success(self):
        result = lambda_handler(self.get_event_success, None)
        self.assertEqual([], json.loads(result["body"]))
        self.assertEqual(200, result["statusCode"])

    @patch(
        "lambda_handler.lambda_function.dynamodb.Table",
        return_value=fixtures.TableWithErrors,
    )
    def test_get_announcements_client_error_failed(self, table_with_errors_mock):
        result = lambda_handler(self.get_event_success, None)
        self.assertEqual(
            {"message": "Something went wrong"}, json.loads(result["body"])
        )
        self.assertEqual(500, result["statusCode"])

    def test_get_announcements_validation_failed(self):
        result = lambda_handler(self.get_event_failed, None)
        self.assertEqual({"message": "bad input parameter"}, json.loads(result["body"]))
        self.assertEqual(400, result["statusCode"])

    def test_create_announcements_success(self):
        result = lambda_handler(self.post_event_success, None)
        self.assertEqual({"message": "item created"}, json.loads(result["body"]))
        self.assertEqual(201, result["statusCode"])

    def test_create_announcements_validation_failed(self):
        result = lambda_handler(self.post_event_failed, None)
        self.assertEqual(
            {"message": "invalid input, object invalid"}, json.loads(result["body"])
        )
        self.assertEqual(400, result["statusCode"])

    @patch(
        "lambda_handler.lambda_function.dynamodb.Table",
        return_value=fixtures.TableWithErrors,
    )
    def test_create_announcements_client_error_failed(self, table_with_errors_mock):
        result = lambda_handler(self.post_event_success, None)
        self.assertEqual(
            {"message": "an item already exists"}, json.loads(result["body"])
        )
        self.assertEqual(409, result["statusCode"])
