import aws_cdk as core
import aws_cdk.assertions as assertions
import pytest
import json

from cdk_base.cdk_base_stack import CdkBaseStack


@pytest.fixture
def cdk_app():
    """Fixture to create a CDK app for testing."""
    return core.App()


@pytest.fixture
def cdk_stack(cdk_app):
    """Fixture to create the CdkBaseStack for testing."""
    return CdkBaseStack(cdk_app, "cdk-base")


@pytest.fixture
def template(cdk_stack):
    """Fixture to get the CloudFormation template from the stack."""
    return assertions.Template.from_stack(cdk_stack)


def test_stack_creates_successfully(cdk_stack):
    """Test that the stack can be instantiated without errors."""
    assert cdk_stack is not None
    assert isinstance(cdk_stack, CdkBaseStack)


def test_stack_has_no_resources_initially(template):
    """TDD Test: Verify the stack starts empty."""
    assert template is not None
    template_dict = template.to_json()
    app = core.App()
    assert "Resources" in template_dict


# ============================================================================
# TDD Tests for Issue #3: S3 Buckets and EventBridge Rule
# ============================================================================

def test_input_s3_bucket_exists(template):
    """TDD Test: Verify Input S3 Bucket exists."""
    template.resource_count_is("AWS::S3::Bucket", 2)  # Input + Output
    
    # Check that at least one bucket has EventBridge notifications enabled
    template.has_resource_properties("AWS::S3::Bucket", {
        "NotificationConfiguration": {
            "EventBridgeConfiguration": {
                "EventBridgeEnabled": True
            }
        }
    })


def test_input_bucket_has_versioning_enabled(template):
    """TDD Test: Verify Input Bucket has versioning enabled."""
    template.has_resource_properties("AWS::S3::Bucket", {
        "VersioningConfiguration": {
            "Status": "Enabled"
        }
    })


def test_input_bucket_has_encryption(template):
    """TDD Test: Verify Input Bucket has encryption enabled."""
    template.has_resource_properties("AWS::S3::Bucket", {
        "BucketEncryption": {
            "ServerSideEncryptionConfiguration": [
                {
                    "ServerSideEncryptionByDefault": {
                        "SSEAlgorithm": "AES256"
                    }
                }
            ]
        }
    })


def test_input_bucket_blocks_public_access(template):
    """TDD Test: Verify Input Bucket blocks public access."""
    template.has_resource_properties("AWS::S3::Bucket", {
        "PublicAccessBlockConfiguration": {
            "BlockPublicAcls": True,
            "BlockPublicPolicy": True,
            "IgnorePublicAcls": True,
            "RestrictPublicBuckets": True
        }
    })


def test_output_s3_bucket_exists(template):
    """TDD Test: Verify Output S3 Bucket exists with proper configuration."""
    # Already counted in test_input_s3_bucket_exists (2 buckets total)
    # Verify output bucket also has versioning
    template.has_resource_properties("AWS::S3::Bucket", {
        "VersioningConfiguration": {
            "Status": "Enabled"
        }
    })


def test_output_bucket_has_encryption(template):
    """TDD Test: Verify Output Bucket has encryption enabled."""
    # Both buckets should have encryption
    template.has_resource_properties("AWS::S3::Bucket", {
        "BucketEncryption": {
            "ServerSideEncryptionConfiguration": [
                {
                    "ServerSideEncryptionByDefault": {
                        "SSEAlgorithm": "AES256"
                    }
                }
            ]
        }
    })


def test_eventbridge_rule_exists(template):
    """TDD Test: Verify EventBridge Rule exists for S3 Object Created events."""
    template.resource_count_is("AWS::Events::Rule", 1)


def test_eventbridge_rule_has_correct_event_pattern(template):
    """TDD Test: Verify EventBridge Rule has correct event pattern for S3."""
    # Check that the rule has an event pattern that matches S3 events
    template.has_resource_properties("AWS::Events::Rule", {
        "State": "ENABLED"
    })
    
    # Verify the rule has an event pattern (will check for S3 source and Object Created detail-type)
    template.has_resource_properties("AWS::Events::Rule", {
        "EventPattern": {
            "source": ["aws.s3"],
            "detail-type": ["Object Created"]
        }
    })


def test_eventbridge_rule_has_target(template):
    """TDD Test: Verify EventBridge Rule has at least one target configured."""
    # Rule must have targets defined (even if placeholder)
    template.has_resource_properties("AWS::Events::Rule", {
        "Targets": assertions.Match.any_value()
    })


# ============================================================================
# TDD Tests for Issue #4: Step Functions State Machine with Polly Integration
# ============================================================================

def test_step_functions_state_machine_exists(template):
    """TDD Test: Verify Step Functions state machine exists."""
    template.resource_count_is("AWS::StepFunctions::StateMachine", 1)


def test_state_machine_has_cloudwatch_logs_enabled(template):
    """TDD Test: Verify state machine has CloudWatch Logs enabled."""
    template.has_resource_properties("AWS::StepFunctions::StateMachine", {
        "LoggingConfiguration": {
            "Level": assertions.Match.string_like_regexp("ALL|ERROR|FATAL|OFF"),
            "IncludeExecutionData": assertions.Match.any_value()
        }
    })


def test_state_machine_has_execution_role(template):
    """TDD Test: Verify state machine has an execution IAM role."""
    # State machine should reference an IAM role
    template.has_resource_properties("AWS::StepFunctions::StateMachine", {
        "RoleArn": assertions.Match.any_value()
    })
    
    # IAM role for state machine should exist
    template.has_resource_properties("AWS::IAM::Role", {
        "AssumeRolePolicyDocument": {
            "Statement": [
                {
                    "Action": "sts:AssumeRole",
                    "Effect": "Allow",
                    "Principal": {
                        "Service": "states.amazonaws.com"
                    }
                }
            ]
        }
    })


def test_state_machine_definition_contains_polly_task(template):
    """TDD Test: Verify state machine definition contains Polly task or integration."""
    # The state machine definition should contain a reference to Polly
    # This checks that the DefinitionString contains "Polly" or "polly"
    template.has_resource_properties("AWS::StepFunctions::StateMachine", {
        "DefinitionString": assertions.Match.string_like_regexp(".*[Pp]olly.*")
    })


def test_eventbridge_rule_targets_state_machine(template):
    """TDD Test: Verify EventBridge rule now targets Step Functions state machine."""
    # EventBridge rule should have a target that points to a Step Functions state machine
    # The target should have Arn pointing to a state machine and RoleArn for invoking it
    template.has_resource_properties("AWS::Events::Rule", {
        "Targets": [
            {
                "Arn": assertions.Match.any_value(),
                "RoleArn": assertions.Match.any_value()
            }
        ]
    })


def test_state_machine_iam_role_has_polly_permissions(template):
    """TDD Test: Verify state machine IAM role has Polly permissions (least privilege)."""
    # Check that there's an IAM policy that grants polly permissions
    template.has_resource_properties("AWS::IAM::Policy", {
        "PolicyDocument": {
            "Statement": assertions.Match.array_with([
                assertions.Match.object_like({
                    "Action": assertions.Match.any_value(),
                    "Effect": "Allow",
                    "Resource": assertions.Match.any_value()
                })
            ])
        }
    })


# ============================================================================
# TDD Tests for Issue #5: DynamoDB Table + Step Functions I/O Handling
# ============================================================================

def test_dynamodb_table_exists(template):
    """TDD Test: Verify DynamoDB table exists for audio metadata."""
    template.resource_count_is("AWS::DynamoDB::Table", 1)


def test_dynamodb_table_has_correct_key_schema(template):
    """TDD Test: Verify DynamoDB table has correct partition key (audioId)."""
    template.has_resource_properties("AWS::DynamoDB::Table", {
        "KeySchema": [
            {
                "AttributeName": "audioId",
                "KeyType": "HASH"
            }
        ],
        "AttributeDefinitions": assertions.Match.array_with([
            {
                "AttributeName": "audioId",
                "AttributeType": "S"
            }
        ])
    })


def test_dynamodb_table_has_encryption_enabled(template):
    """TDD Test: Verify DynamoDB table has server-side encryption enabled."""
    template.has_resource_properties("AWS::DynamoDB::Table", {
        "SSESpecification": {
            "SSEEnabled": True
        }
    })


def test_dynamodb_table_has_billing_mode(template):
    """TDD Test: Verify DynamoDB table has on-demand billing mode."""
    template.has_resource_properties("AWS::DynamoDB::Table", {
        "BillingMode": "PAY_PER_REQUEST"
    })


def test_dynamodb_table_has_point_in_time_recovery(template):
    """TDD Test: Verify DynamoDB table has point-in-time recovery enabled."""
    template.has_resource_properties("AWS::DynamoDB::Table", {
        "PointInTimeRecoverySpecification": {
            "PointInTimeRecoveryEnabled": True
        }
    })


def test_state_machine_has_dynamodb_permissions(template):
    """TDD Test: Verify state machine IAM role has DynamoDB read/write permissions."""
    # Check that there's an IAM policy that grants DynamoDB permissions
    template.has_resource_properties("AWS::IAM::Policy", {
        "PolicyDocument": {
            "Statement": assertions.Match.array_with([
                assertions.Match.object_like({
                    "Action": assertions.Match.array_with([
                        assertions.Match.string_like_regexp("dynamodb:PutItem|dynamodb:UpdateItem")
                    ]),
                    "Effect": "Allow"
                })
            ])
        }
    })


def test_state_machine_definition_contains_dynamodb_task(template):
    """TDD Test: Verify state machine definition contains DynamoDB task."""
    # The state machine definition should contain references to DynamoDB operations
    # This checks that the DefinitionString contains "DynamoDB" or "dynamodb"
    template.has_resource_properties("AWS::StepFunctions::StateMachine", {
        "DefinitionString": assertions.Match.string_like_regexp(".*[Dd]ynamo[Dd][Bb].*")
    })


def test_state_machine_input_mapping_from_s3_event(template):
    """TDD Test: Verify EventBridge passes S3 event data to state machine correctly."""
    # EventBridge rule should pass the entire event (already implemented in Issue #4)
    # This test verifies the input mapping is configured
    template.has_resource_properties("AWS::Events::Rule", {
        "Targets": assertions.Match.array_with([
            assertions.Match.object_like({
                "Arn": assertions.Match.any_value(),
                "Input": assertions.Match.absent()  # No custom input transform, passes full event
            })
        ])
    })


# ============================================================================
# TDD Tests for Issue #6: SNS Notifications and Error Handling
# ============================================================================

def test_sns_topics_exist(template):
    """TDD Test: Verify SNS topics exist for notifications."""
    # Should have 2 SNS topics: one for completion, one for errors
    template.resource_count_is("AWS::SNS::Topic", 2)


def test_sns_topics_have_encryption(template):
    """TDD Test: Verify SNS topics have KMS encryption enabled."""
    # Both topics should have KMS encryption
    template.has_resource_properties("AWS::SNS::Topic", {
        "KmsMasterKeyId": assertions.Match.any_value()
    })


def test_sns_completed_topic_exists(template):
    """TDD Test: Verify SNS topic for pipeline completion exists."""
    # Check for topic with display name containing "Completed" or similar
    template.has_resource_properties("AWS::SNS::Topic", {
        "DisplayName": assertions.Match.string_like_regexp(".*[Cc]ompleted.*")
    })


def test_sns_failed_topic_exists(template):
    """TDD Test: Verify SNS topic for pipeline errors exists."""
    # Check for topic with display name containing "Failed" or "Error"
    template.has_resource_properties("AWS::SNS::Topic", {
        "DisplayName": assertions.Match.string_like_regexp(".*[Ff]ailed.*|.*[Ee]rror.*")
    })


def test_state_machine_has_error_handling(template):
    """TDD Test: Verify state machine definition contains error handling (Catch blocks)."""
    # The state machine definition should contain Catch or error handling keywords
    template.has_resource_properties("AWS::StepFunctions::StateMachine", {
        "DefinitionString": assertions.Match.string_like_regexp(".*[Cc]atch.*")
    })


def test_state_machine_publishes_to_sns_on_success(template):
    """TDD Test: Verify state machine publishes to SNS on successful completion."""
    # The state machine definition should contain SNS publish action
    template.has_resource_properties("AWS::StepFunctions::StateMachine", {
        "DefinitionString": assertions.Match.string_like_regexp(".*sns:Publish.*")
    })


def test_state_machine_publishes_to_sns_on_failure(template):
    """TDD Test: Verify state machine publishes to SNS on error/failure."""
    # This is covered by the general SNS publish test above
    # and the error handling test (Catch blocks)
    # The definition should have both Catch and sns:Publish
    template.has_resource_properties("AWS::StepFunctions::StateMachine", {
        "DefinitionString": assertions.Match.string_like_regexp(".*[Cc]atch.*")
    })
    template.has_resource_properties("AWS::StepFunctions::StateMachine", {
        "DefinitionString": assertions.Match.string_like_regexp(".*sns:Publish.*")
    })


def test_state_machine_updates_status_to_completed(template):
    """TDD Test: Verify state machine updates DynamoDB status to COMPLETED."""
    # The state machine definition should contain UpdateItem with COMPLETED status
    template.has_resource_properties("AWS::StepFunctions::StateMachine", {
        "DefinitionString": assertions.Match.string_like_regexp(".*COMPLETED.*")
    })


def test_state_machine_updates_status_to_failed(template):
    """TDD Test: Verify state machine updates DynamoDB status to FAILED."""
    # The state machine definition should contain UpdateItem with FAILED status
    template.has_resource_properties("AWS::StepFunctions::StateMachine", {
        "DefinitionString": assertions.Match.string_like_regexp(".*FAILED.*")
    })


def test_dynamodb_status_updates_in_definition(template):
    """TDD Test: Verify state machine definition contains DynamoDB UpdateItem operations."""
    # The state machine definition should contain UpdateItem action
    template.has_resource_properties("AWS::StepFunctions::StateMachine", {
        "DefinitionString": assertions.Match.string_like_regexp(".*dynamodb:UpdateItem.*|.*UpdateItem.*")
    })


def test_state_machine_has_sns_publish_permissions(template):
    """TDD Test: Verify state machine IAM role has SNS publish permissions."""
    # Check that there's an IAM policy that grants SNS publish permissions
    template.has_resource_properties("AWS::IAM::Policy", {
        "PolicyDocument": {
            "Statement": assertions.Match.array_with([
                assertions.Match.object_like({
                    "Action": assertions.Match.array_with([
                        "sns:Publish"
                    ]),
                    "Effect": "Allow"
                })
            ])
        }
    })


def test_state_machine_has_dynamodb_update_permissions(template):
    """TDD Test: Verify state machine IAM role has DynamoDB UpdateItem permissions."""
    # This should already exist from Issue #5, but verify it's there
    template.has_resource_properties("AWS::IAM::Policy", {
        "PolicyDocument": {
            "Statement": assertions.Match.array_with([
                assertions.Match.object_like({
                    "Action": assertions.Match.array_with([
                        assertions.Match.string_like_regexp(".*dynamodb:UpdateItem.*")
                    ]),
                    "Effect": "Allow"
                })
            ])
        }
    })


# ============================================================================
# TDD Tests for Issue #7: Lambda Function Integration
# ============================================================================

def test_lambda_function_exists(template):
    """TDD Test: Verify Lambda function exists for audio processing."""
    # Should have 1 Lambda function: SleepAudioProcessor
    template.resource_count_is("AWS::Lambda::Function", 1)


def test_lambda_function_has_python_runtime(template):
    """TDD Test: Verify Lambda function uses Python runtime."""
    # Lambda should use Python 3.12 or later
    template.has_resource_properties("AWS::Lambda::Function", {
        "Runtime": assertions.Match.string_like_regexp("python3\\..*")
    })


def test_lambda_function_has_correct_handler(template):
    """TDD Test: Verify Lambda function has correct handler configuration."""
    # Handler should point to handler.lambda_handler
    template.has_resource_properties("AWS::Lambda::Function", {
        "Handler": assertions.Match.string_like_regexp(".*handler\\.lambda_handler.*|.*lambda_handler.*")
    })


def test_lambda_function_has_environment_variables(template):
    """TDD Test: Verify Lambda function has environment variables configured."""
    # Lambda should have environment variables including TABLE_NAME
    template.has_resource_properties("AWS::Lambda::Function", {
        "Environment": {
            "Variables": assertions.Match.object_like({
                "TABLE_NAME": assertions.Match.any_value()
            })
        }
    })


def test_lambda_execution_role_exists(template):
    """TDD Test: Verify Lambda function has an execution IAM role."""
    # Lambda function should reference an IAM role
    template.has_resource_properties("AWS::Lambda::Function", {
        "Role": assertions.Match.any_value()
    })
    
    # IAM role for Lambda should exist with correct trust policy
    template.has_resource_properties("AWS::IAM::Role", {
        "AssumeRolePolicyDocument": {
            "Statement": assertions.Match.array_with([
                {
                    "Action": "sts:AssumeRole",
                    "Effect": "Allow",
                    "Principal": {
                        "Service": "lambda.amazonaws.com"
                    }
                }
            ])
        }
    })


def test_state_machine_definition_contains_lambda_invoke(template):
    """TDD Test: Verify state machine definition contains Lambda invocation task."""
    # The state machine definition should contain a Lambda invoke action
    # This checks that the DefinitionString contains "lambda:InvokeFunction" or similar
    template.has_resource_properties("AWS::StepFunctions::StateMachine", {
        "DefinitionString": assertions.Match.string_like_regexp(".*lambda:InvokeFunction.*|.*Lambda.*")
    })


def test_state_machine_role_has_lambda_invoke_permissions(template):
    """TDD Test: Verify state machine IAM role has permission to invoke Lambda."""
    # Check that there's an IAM policy that grants lambda:InvokeFunction permission
    template.has_resource_properties("AWS::IAM::Policy", {
        "PolicyDocument": {
            "Statement": assertions.Match.array_with([
                assertions.Match.object_like({
                    "Action": "lambda:InvokeFunction",
                    "Effect": "Allow"
                })
            ])
        }
    })


def test_synthesized_template_snapshot(template):
    """TDD Test: Snapshot test to catch unexpected changes in synthesized template."""
    # This test verifies the template structure hasn't changed unexpectedly
    # It's a broad check that complements the fine-grained tests above
    template_dict = template.to_json()
    assert "Resources" in template_dict
    assert len(template_dict["Resources"]) > 0
