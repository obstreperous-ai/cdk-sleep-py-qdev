from aws_cdk import (
    Stack,
    aws_s3 as s3,
    aws_lambda as lambda_,
    aws_sns as sns,
    aws_dynamodb as dynamodb,
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
        # Issue #4: Step Functions State Machine with Polly Integration
        # Issue #5: DynamoDB Table for Audio Pipeline Metadata
        # ====================================================================
        
        # DynamoDB Table - stores metadata for audio processing pipeline
        self.metadata_table = dynamodb.Table(
            self,
            "SleepAudioMetadataTable",
            table_name="SleepAudioMetadataTable",
            partition_key=dynamodb.Attribute(
                name="audioId",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,  # On-demand billing
            encryption=dynamodb.TableEncryption.AWS_MANAGED,  # Server-side encryption
            point_in_time_recovery=True,  # Enable backup for data protection
            removal_policy=RemovalPolicy.DESTROY,  # For dev/test - change to RETAIN for prod
        )
        
        # ====================================================================
        # Issue #6: SNS Topics for Pipeline Notifications
        # ====================================================================
        # Issue #7: Lambda Function for Audio Processing
        # ====================================================================
        
        # Lambda function for audio processing - placeholder for future validation,
        # metadata enrichment, or other processing logic
        self.audio_processor_lambda = lambda_.Function(
            self,
            "SleepAudioProcessor",
            function_name="SleepAudioProcessor",
            runtime=lambda_.Runtime.PYTHON_3_12,
            handler="handler.lambda_handler",
            code=lambda_.Code.from_asset("lambda/audio_processor"),
            environment={
                "TABLE_NAME": self.metadata_table.table_name,
            },
            description="Audio processor Lambda for validation and metadata enrichment",
            timeout=Duration.seconds(30),  # 30 second timeout for processing
        )
        
        # Grant Lambda function read access to DynamoDB table (for future enhancements)
        # Currently the Lambda just logs and returns, but this permission enables
        # future features like reading existing metadata or updating records
        self.metadata_table.grant_read_data(self.audio_processor_lambda)
        
        # ====================================================================
        # Issue #6: SNS Topics for Pipeline Notifications
        # ====================================================================
        
        # SNS Topic for successful pipeline completion
        self.completed_topic = sns.Topic(
            self,
            "SleepAudioPipelineCompleted",
            display_name="Sleep Audio Pipeline Completed",
            master_key=sns.Topic.DEFAULT_MASTER_KEY,  # Use default AWS managed KMS key
        )
        
        # SNS Topic for pipeline failures
        self.failed_topic = sns.Topic(
            self,
            "SleepAudioPipelineFailed",
            display_name="Sleep Audio Pipeline Failed",
            master_key=sns.Topic.DEFAULT_MASTER_KEY,  # Use default AWS managed KMS key
        )
        
        # ====================================================================
        
        # CloudWatch Log Group for Step Functions state machine
        state_machine_log_group = logs.LogGroup(
            self,
            "SleepAudioStateMachineLogGroup",
            log_group_name="/aws/stepfunctions/sleep-audio-pipeline",
            removal_policy=RemovalPolicy.DESTROY,
        )
        
        # Define the Polly task - minimal placeholder for text-to-speech synthesis
        # Define DynamoDB PutItem task - writes initial metadata record
        # This captures the S3 event data and creates a tracking record
        put_metadata_task = tasks.DynamoPutItem(
            self,
            "PutInitialMetadata",
            table=self.metadata_table,
            item={
                "audioId": tasks.DynamoAttributeValue.from_string(
                    sfn.JsonPath.string_at("$.detail.object.key")
                ),
                "status": tasks.DynamoAttributeValue.from_string("PROCESSING"),
                "inputBucket": tasks.DynamoAttributeValue.from_string(
                    sfn.JsonPath.string_at("$.detail.bucket.name")
                ),
                "inputKey": tasks.DynamoAttributeValue.from_string(
                    sfn.JsonPath.string_at("$.detail.object.key")
                ),
                "createdAt": tasks.DynamoAttributeValue.from_string(
                    sfn.JsonPath.string_at("$$.State.EnteredTime")
                ),
                "updatedAt": tasks.DynamoAttributeValue.from_string(
                    sfn.JsonPath.string_at("$$.State.EnteredTime")
                ),
            },
            result_path="$.dynamoResult",
        )
        
        # ====================================================================
        # Issue #7: Lambda Invocation Task
        # ====================================================================
        
        # Lambda invocation task - processes audio metadata and performs validation
        # This is inserted after PutInitialMetadata and before Polly task
        invoke_audio_processor = tasks.LambdaInvoke(
            self,
            "InvokeAudioProcessor",
            lambda_function=self.audio_processor_lambda,
            payload=sfn.TaskInput.from_object(sfn.JsonPath.entire_payload),
            result_path="$.lambdaResult",
        )
        
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
        
        # ====================================================================
        # Issue #6: Error Handling and Status Updates
        # ====================================================================
        
        # SUCCESS PATH: Update DynamoDB status to COMPLETED
        update_status_completed = tasks.DynamoUpdateItem(
            self,
            "UpdateStatusCompleted",
            table=self.metadata_table,
            key={
                "audioId": tasks.DynamoAttributeValue.from_string(
                    sfn.JsonPath.string_at("$.detail.object.key")
                )
            },
            update_expression="SET #status = :completed, #updatedAt = :timestamp",
            expression_attribute_names={
                "#status": "status",
                "#updatedAt": "updatedAt"
            },
            expression_attribute_values={
                ":completed": tasks.DynamoAttributeValue.from_string("COMPLETED"),
                ":timestamp": tasks.DynamoAttributeValue.from_string(
                    sfn.JsonPath.string_at("$$.State.EnteredTime")
                )
            },
            result_path="$.updateCompletedResult",
        )
        
        # SUCCESS PATH: Publish success notification to SNS
        publish_success = tasks.SnsPublish(
            self,
            "PublishSuccessNotification",
            topic=self.completed_topic,
            message=sfn.TaskInput.from_object({
                "status": "COMPLETED",
                "audioId": sfn.JsonPath.string_at("$.detail.object.key"),
                "bucket": sfn.JsonPath.string_at("$.detail.bucket.name"),
                "timestamp": sfn.JsonPath.string_at("$$.State.EnteredTime"),
                "message": "Audio processing completed successfully"
            }),
            subject="Sleep Audio Pipeline - Processing Completed",
            result_path="$.snsSuccessResult",
        )
        
        # ERROR PATH: Update DynamoDB status to FAILED
        update_status_failed = tasks.DynamoUpdateItem(
            self,
            "UpdateStatusFailed",
            table=self.metadata_table,
            key={
                "audioId": tasks.DynamoAttributeValue.from_string(
                    sfn.JsonPath.string_at("$.detail.object.key")
                )
            },
            update_expression="SET #status = :failed, #updatedAt = :timestamp, #error = :errorMsg",
            expression_attribute_names={
                "#status": "status",
                "#updatedAt": "updatedAt",
                "#error": "errorMessage"
            },
            expression_attribute_values={
                ":failed": tasks.DynamoAttributeValue.from_string("FAILED"),
                ":timestamp": tasks.DynamoAttributeValue.from_string(
                    sfn.JsonPath.string_at("$$.State.EnteredTime")
                ),
                ":errorMsg": tasks.DynamoAttributeValue.from_string(
                    sfn.JsonPath.string_at("$.errorMessage")
                )
            },
            result_path="$.updateFailedResult",
        )
        
        # ERROR PATH: Publish error notification to SNS
        publish_error = tasks.SnsPublish(
            self,
            "PublishErrorNotification",
            topic=self.failed_topic,
            message=sfn.TaskInput.from_object({
                "status": "FAILED",
                "audioId": sfn.JsonPath.string_at("$.detail.object.key"),
                "bucket": sfn.JsonPath.string_at("$.detail.bucket.name"),
                "timestamp": sfn.JsonPath.string_at("$$.State.EnteredTime"),
                "error": sfn.JsonPath.string_at("$.errorMessage"),
                "message": "Audio processing failed"
            }),
            subject="Sleep Audio Pipeline - Processing Failed",
            result_path="$.snsErrorResult",
        )
        
        # Chain the error path: update status → publish notification
        lambda_error_handler_chain = update_status_failed.next(publish_error)
        
        # ====================================================================
        # Issue #8: Add Error Handling to Lambda Invocation
        # ====================================================================
        
        # Add error handling (Catch) to Lambda invocation task
        # This catches validation errors and other Lambda failures
        invoke_audio_processor.add_catch(
            lambda_error_handler_chain,
            errors=["States.ALL"],
            result_path="$.errorInfo"
        )
        
        # Add error handling (Catch) to Polly task (already exists, updating for consistency)
        # Creates a separate error handler chain for Polly errors
        polly_error_handler_chain = tasks.DynamoUpdateItem(
            self,
            "UpdateStatusFailedPolly",
            table=self.metadata_table,
            key={
                "audioId": tasks.DynamoAttributeValue.from_string(
                    sfn.JsonPath.string_at("$.detail.object.key")
                )
            },
            update_expression="SET #status = :failed, #updatedAt = :timestamp, #error = :errorMsg",
            expression_attribute_names={
                "#status": "status",
                "#updatedAt": "updatedAt",
                "#error": "errorMessage"
            },
            expression_attribute_values={
                ":failed": tasks.DynamoAttributeValue.from_string("FAILED"),
                ":timestamp": tasks.DynamoAttributeValue.from_string(
                    sfn.JsonPath.string_at("$$.State.EnteredTime")
                ),
                ":errorMsg": tasks.DynamoAttributeValue.from_string(
                    sfn.JsonPath.string_at("$.errorMessage")
                )
            },
            result_path="$.updateFailedResult",
        ).next(
            tasks.SnsPublish(
                self,
                "PublishPollyErrorNotification",
                topic=self.failed_topic,
                message=sfn.TaskInput.from_object({
                    "status": "FAILED",
                    "audioId": sfn.JsonPath.string_at("$.detail.object.key"),
                    "bucket": sfn.JsonPath.string_at("$.detail.bucket.name"),
                    "timestamp": sfn.JsonPath.string_at("$$.State.EnteredTime"),
                    "error": sfn.JsonPath.string_at("$.errorMessage"),
                    "message": "Polly processing failed"
                }),
                subject="Sleep Audio Pipeline - Polly Failed",
                result_path="$.snsErrorResult",
            )
        )
        
        polly_task.add_catch(
            polly_error_handler_chain,
            errors=["States.ALL"],
            result_path="$.errorInfo"
        )
        
        # Chain the success path: Polly → update status → publish notification
        success_chain = polly_task.next(update_status_completed).next(publish_success)
        
        # Define the complete state machine workflow
        # Flow: Start → PutInitialMetadata → InvokeAudioProcessor (Lambda) → PollyTask (with Catch) → UpdateStatusCompleted → PublishSuccess → End
        #       Error Path: Catch → UpdateStatusFailed → PublishError → End
        state_machine_definition = put_metadata_task.next(invoke_audio_processor).next(success_chain)
        
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
        # Grant the state machine permissions to write to DynamoDB table
        # Allows tracking of audio processing metadata
        self.metadata_table.grant_write_data(state_machine)
        
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
        # Issue #6: Grant SNS Publish Permissions
        # ====================================================================
        
        # Grant the state machine permissions to publish to SNS topics
        self.completed_topic.grant_publish(state_machine)
        self.failed_topic.grant_publish(state_machine)
        
        # Note: DynamoDB UpdateItem permissions are already covered by grant_write_data()
        # which includes both PutItem and UpdateItem actions
        
        # ====================================================================
        # ====================================================================
        # EventBridge Rule - Wiring to Step Functions
        # ====================================================================
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
