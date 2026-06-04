from aws_cdk import (
    Stack,
    aws_s3 as s3,
    aws_events as events,
    aws_events_targets as targets,
    aws_logs as logs,
    aws_stepfunctions as sfn,
    aws_stepfunctions_tasks as tasks,
    aws_iam as iam,
    RemovalPolicy,
    Duration,
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
        # ====================================================================
        # Issue #4: Step Functions State Machine with Polly Integration
        # ====================================================================
        
        # CloudWatch Log Group for Step Functions state machine
        state_machine_log_group = logs.LogGroup(
            self,
            "SleepAudioStateMachineLogGroup",
            log_group_name="/aws/stepfunctions/sleep-audio-pipeline",
            removal_policy=RemovalPolicy.DESTROY,
        )
        
        # Define the Polly task - minimal placeholder for text-to-speech synthesis
        # This uses StartSpeechSynthesisTask for async processing
        polly_task = tasks.CallAwsService(
            self,
            "PollyTextToSpeech",
            service="polly",
            action="startSpeechSynthesisTask",
            parameters={
                "Engine": "neural",
                "OutputFormat": "mp3",
                "OutputS3BucketName": self.output_bucket.bucket_name,
                "Text": sfn.JsonPath.string_at("$.detail.object.key"),  # Placeholder
                "VoiceId": "Joanna",  # Default soothing voice
            },
            iam_resources=[
                f"arn:aws:polly:*:{Stack.of(self).account}:lexicon/*",
            ],
            result_path="$.pollyResult",
        )
        
        # Define the state machine with Polly task
        # Simple flow: Start → Polly Task → End
        state_machine_definition = polly_task
        
        # Create the state machine
        state_machine = sfn.StateMachine(
            self,
            "SleepAudioPipelineStateMachine",
            state_machine_name="SleepAudioPipelineStateMachine",
            definition_body=sfn.DefinitionBody.from_chainable(state_machine_definition),
            logs=sfn.LogOptions(
                destination=state_machine_log_group,
                level=sfn.LogLevel.ALL,
                include_execution_data=True,
            ),
            tracing_enabled=True,  # Enable X-Ray tracing for observability
        )
        
        # Grant the state machine permissions to write to output bucket
        # (Polly needs to write generated audio to S3)
        self.output_bucket.grant_put(state_machine)
        
        # Grant the state machine permissions to read from input bucket
        # (Future: for reading text files)
        self.input_bucket.grant_read(state_machine)
        
        # Add explicit Polly permissions to the state machine role
        # Least privilege: only allow starting synthesis tasks
        state_machine.add_to_role_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "polly:StartSpeechSynthesisTask",
                    "polly:GetSpeechSynthesisTask",
                    "polly:ListSpeechSynthesisTasks",
                ],
                resources=["*"],  # Polly doesn't support resource-level permissions
            )
        )
        
        # ====================================================================
        # EventBridge Rule - Wiring to Step Functions
        # ====================================================================
        
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

        # Add Step Functions state machine as primary target
        # Replaces the CloudWatch Logs placeholder from Issue #3
        event_rule.add_target(
            targets.SfnStateMachine(
                state_machine,
                input=events.RuleTargetInput.from_event_path("$"),  # Pass entire event
                retry_attempts=2,  # Retry on failure
            )
        )
        
        # Keep CloudWatch Logs as secondary target for debugging
        # (This allows us to see the raw events for troubleshooting)
        event_rule.add_target(
            targets.CloudWatchLogGroup(log_group)
        )
