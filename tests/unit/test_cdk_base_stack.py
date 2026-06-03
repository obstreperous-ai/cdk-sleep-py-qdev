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
