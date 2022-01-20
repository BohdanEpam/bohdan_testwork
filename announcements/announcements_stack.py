import json

import aws_cdk
from aws_cdk import (
    aws_lambda,
    aws_dynamodb,
    aws_apigateway,
    Duration,
    Stack,
    RemovalPolicy,
    aws_iam,
)
from constructs import Construct


class AnnouncementsStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        # create dynamo table
        announcements_table = self.create_announcements_table(
            table_name="announcements"
        )

        # create lambda function with layer
        lambda_fnc = self.create_lambda_function(func_name="lambda_fnc")

        # add DynamoDb table name to lambda env
        lambda_fnc.add_environment("TABLE_NAME", announcements_table.table_name)

        # grant permission to lambda to write and read to table
        announcements_table.grant_write_data(lambda_fnc)
        announcements_table.grant_read_data(lambda_fnc)

        # create gateway according openApi specification
        api_gateway = self.create_api_gateway(lambda_fnc)

        # create lambda-gateway permissions
        self.create_lambda_gateway_permissions(lambda_fnc, api_gateway)

    def create_api_gateway(
        self, lambda_fnc: aws_lambda.Function
    ) -> aws_apigateway.SpecRestApi:
        # create gateway according openApi specification
        with open("docs/api_build_specification.json", "r") as json_file:
            content = json_file.read()
        content = content.replace("${API_LAMBDA_ARN}", lambda_fnc.function_arn)
        openapi_json = json.loads(content)
        return aws_apigateway.SpecRestApi(
            self,
            "lambda-api",
            rest_api_name="announcement",
            api_definition=aws_apigateway.ApiDefinition.from_inline(openapi_json),
        )

    def create_lambda_function(self, func_name: str) -> aws_lambda.Function:
        return aws_lambda.Function(
            self,
            func_name,
            runtime=aws_lambda.Runtime.PYTHON_3_7,
            handler="lambda_function.lambda_handler",
            code=aws_lambda.Code.from_asset("./lambda_handler"),
            timeout=Duration.seconds(10),
            layers=[
                aws_lambda.LayerVersion(
                    self,
                    "lambda-layer",
                    code=aws_lambda.AssetCode("lambda_layer/layer/"),
                    compatible_runtimes=[aws_lambda.Runtime.PYTHON_3_7],
                    removal_policy=RemovalPolicy.DESTROY,
                )
            ],
        )

    def create_announcements_table(self, table_name: str) -> aws_dynamodb.Table:
        return aws_dynamodb.Table(
            self,
            table_name,
            partition_key=aws_dynamodb.Attribute(
                name="title", type=aws_dynamodb.AttributeType.STRING
            ),
            billing_mode=aws_dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=aws_cdk.RemovalPolicy.DESTROY,
        )

    @staticmethod
    def create_lambda_gateway_permissions(
        lambda_fnc: aws_lambda.Function, api_gateway: aws_apigateway.RestApiBase
    ):
        principal = aws_iam.ServicePrincipal("apigateway.amazonaws.com")
        lambda_fnc.grant_invoke(principal)

        lambda_fnc.add_permission(
            "statement_id_1",
            principal=principal,
            source_arn=api_gateway.arn_for_execute_api(
                method="GET", path="/announcement", stage="*"
            ),
        )
        lambda_fnc.add_permission(
            "statement_id_2",
            principal=principal,
            source_arn=api_gateway.arn_for_execute_api(
                method="POST", path="/announcement", stage="*"
            ),
        )
