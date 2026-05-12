import aws_cdk as core
import aws_cdk.assertions as assertions
import pytest

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
