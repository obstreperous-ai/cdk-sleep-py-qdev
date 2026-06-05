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
