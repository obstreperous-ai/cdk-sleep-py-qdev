#!/usr/bin/env python3
import os

import aws_cdk as cdk

from cdk_base.cdk_base_stack import CdkBaseStack


app = cdk.App()

# Get environment from context (--context env=dev|stage|prod) or default to dev
env_name = app.node.try_get_context("env") or "dev"

# Environment-specific AWS account and region configuration
# In a real deployment, these would come from context or environment variables
env_configs = {
    "dev": {
        "account": os.getenv('CDK_DEFAULT_ACCOUNT'),
        "region": os.getenv('CDK_DEFAULT_REGION', 'us-east-1'),
    },
    "stage": {
        "account": os.getenv('CDK_DEFAULT_ACCOUNT'),
        "region": os.getenv('CDK_DEFAULT_REGION', 'us-east-1'),
    },
    "prod": {
        "account": os.getenv('CDK_DEFAULT_ACCOUNT'),
        "region": os.getenv('CDK_DEFAULT_REGION', 'us-east-1'),
    }
}

# Create the main application stack with environment-specific configuration
CdkBaseStack(
    app,
    f"CdkBaseStack-{env_name}",
    env_name=env_name,
    env=cdk.Environment(
        account=env_configs[env_name]["account"],
        region=env_configs[env_name]["region"]
    ),
)

app.synth()
