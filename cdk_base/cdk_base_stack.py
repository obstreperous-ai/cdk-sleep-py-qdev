from aws_cdk import (
    Stack,
    aws_s3 as s3,
    aws_events as events,
    aws_events_targets as targets,
    aws_logs as logs,
    RemovalPolicy,
)
from constructs import Construct

class CdkBaseStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # ====================================================================
        # Issue #3: S3 Buckets and EventBridge Rule for Sleep Audio Pipeline
        # ====================================================================
        
        # Input S3 Bucket - receives raw audio/text uploads
        self.input_bucket = s3.Bucket(
            self,
            "SleepAudioInputBucket",
            encryption=s3.BucketEncryption.S3_MANAGED,
            versioned=True,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            event_bridge_enabled=True,  # Enable EventBridge notifications
            enforce_ssl=True,
            removal_policy=RemovalPolicy.RETAIN,  # Protect production data
        )
        
        # Output S3 Bucket - stores processed audio files
        self.output_bucket = s3.Bucket(
            self,
            "SleepAudioOutputBucket",
            encryption=s3.BucketEncryption.S3_MANAGED,
            versioned=True,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            enforce_ssl=True,
            removal_policy=RemovalPolicy.RETAIN,  # Protect production data
        )
        
        # CloudWatch Log Group for EventBridge rule (placeholder target)
        log_group = logs.LogGroup(
            self,
            "SleepAudioEventLogGroup",
            log_group_name="/aws/events/sleep-audio-pipeline",
            removal_policy=RemovalPolicy.DESTROY,  # Safe to delete logs
        )
        
        # EventBridge Rule - triggers on S3 Object Created events
        event_rule = events.Rule(
            self,
            "SleepAudioInputRule",
            description="Triggers audio processing when new files are uploaded to input bucket",
            event_pattern=events.EventPattern(
                source=["aws.s3"],
                detail_type=["Object Created"],
                detail={
                    "bucket": {
                        "name": [self.input_bucket.bucket_name]
                    }
                }
            ),
            enabled=True,
        )

        # Add CloudWatch Logs as placeholder target
        # (Will be replaced with Step Functions in Issue #4)
        event_rule.add_target(
            targets.CloudWatchLogGroup(log_group)
        )
