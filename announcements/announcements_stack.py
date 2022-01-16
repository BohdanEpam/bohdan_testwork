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
        announcements_table = aws_dynamodb.Table(
            self,
            "announcements",
            partition_key=aws_dynamodb.Attribute(
                name="title", type=aws_dynamodb.AttributeType.STRING
            ),
            billing_mode=aws_dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=aws_cdk.RemovalPolicy.DESTROY,
        )

        # create lambda function with layer
        lambda_fnc = aws_lambda.Function(
            self,
            "lambda_fnc",
            runtime=aws_lambda.Runtime.PYTHON_3_7,
            handler="lambda_function.lambda_handler",
            code=aws_lambda.Code.from_asset("./lambda"),
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

        lambda_fnc.add_environment("TABLE_NAME", announcements_table.table_name)

        # grant permission to lambda to write to demo table
        announcements_table.grant_write_data(lambda_fnc)

        # grant permission to lambda to read from demo table
        announcements_table.grant_read_data(lambda_fnc)

        # create gateway according openApi specification
        with open("docs/api_build_specification.json", "r") as json_file:
            content = json_file.read()
        content = content.replace("${API_LAMBDA_ARN}", lambda_fnc.function_arn)
        openapi_json = json.loads(content)
        api_gateway = aws_apigateway.SpecRestApi(
            self,
            "lambda-api",
            rest_api_name="announcement",
            api_definition=aws_apigateway.ApiDefinition.from_inline(openapi_json),
        )
        principal = aws_iam.ServicePrincipal("apigateway.amazonaws.com")
        lambda_fnc.grant_invoke(principal)

        # create lambda-gateway permissions
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
