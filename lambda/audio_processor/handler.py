"""
Lambda handler for audio processing in the Sleep Audio Pipeline.

Issue #8: Added input validation for S3 events and file format checking
Issue #10: Enhanced with structured JSON logging and improved observability
          for production monitoring, X-Ray tracing support, and detailed
          request tracking with correlation IDs.
Issue #11: Core audio processing logic with S3 download/upload, Polly integration, and DynamoDB updates

Current functionality:
- Receives input from Step Functions state machine
- Logs S3 event details and audioId
- Returns a simple success response with metadata
- Basic error handling
- Input validation for required fields (bucket, key)
- File extension validation (rejects unsupported formats)
- Structured JSON logging with request IDs and timestamps
- Downloads input files from S3
- Processes text files with Amazon Polly TTS
- Uploads processed audio to output S3 bucket
- Updates DynamoDB with output location and metadata

Future enhancements:
- File validation (format, size, content-type)
- Audio metadata extraction (duration, bitrate, codec)
- Content analysis and categorization
- Integration with additional processing services
"""

import json
import logging
import os
import time
import boto3
from datetime import datetime
from typing import Dict, Any

# Initialize AWS clients
s3_client = boto3.client('s3')
polly_client = boto3.client('polly')
dynamodb = boto3.resource('dynamodb')

# Configure structured logging for production observability
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Simple JSON formatter for structured logs
logging.basicConfig(format='%(message)s')

# Environment variables
OUTPUT_BUCKET_NAME = os.environ.get("OUTPUT_BUCKET_NAME", "")
TABLE_NAME = os.environ.get("TABLE_NAME", "SleepAudioMetadataTable")

# Supported audio file extensions for the sleep audio pipeline
SUPPORTED_EXTENSIONS = {".mp3", ".wav", ".flac", ".txt", ".m4a", ".ogg"}


class ValidationError(Exception):
    """Custom exception for input validation errors."""
    pass


def validate_s3_event(event: Dict[str, Any]) -> Dict[str, str]:
def log_structured(level: str, message: str, context: Dict[str, Any] = None, request_id: str = None):
    """
    Log structured JSON messages for better observability and monitoring.
    
    Args:
        level: Log level (INFO, ERROR, WARNING, DEBUG)
        message: Human-readable log message
        context: Additional context data to include in log
        request_id: Request/execution ID for correlation
    """
    log_entry = {
        "timestamp": time.time(),
        "level": level,
        "message": message,
        "request_id": request_id or "unknown",
    }
    
    if context:
        log_entry.update(context)
    
    log_message = json.dumps(log_entry)
    
    if level == "ERROR":
        logger.error(log_message)
    else:
        logger.info(log_message)


    """
    Validate S3 event structure and extract required fields.
    
    Args:
        event: Input event from Step Functions containing S3 event details
        
    Returns:
        Dict with validated bucket and key
        
    Raises:
        ValidationError: If required fields are missing or invalid
    """
    # Validate event structure
    if not event:
        raise ValidationError("Event is empty or None")
    
    # Extract detail section
    detail = event.get("detail", {})
    if not detail:
        raise ValidationError("Missing 'detail' field in S3 event")
    
    # Extract and validate bucket
    bucket_info = detail.get("bucket", {})
    bucket_name = bucket_info.get("name", "")
    if not bucket_name:
        raise ValidationError("Missing or empty bucket name in S3 event")
    
    # Extract and validate object key
    object_info = detail.get("object", {})
    object_key = object_info.get("key", "")
    if not object_key:
        raise ValidationError("Missing or empty object key in S3 event")
    
    return {
        "bucket": bucket_name,
        "key": object_key
    }


def validate_file_extension(file_key: str) -> bool:
    """
    Validate that the file has a supported extension.
    
    Args:
        file_key: S3 object key (filename)
        
    Returns:
        True if extension is supported
        
    Raises:
        ValidationError: If file extension is not supported
    """
    # Extract file extension (case-insensitive)
    extension = None
    if "." in file_key:
        extension = "." + file_key.rsplit(".", 1)[-1].lower()
    
    if not extension or extension not in SUPPORTED_EXTENSIONS:
        supported_list = ", ".join(sorted(SUPPORTED_EXTENSIONS))
        raise ValidationError(
            f"Unsupported file extension: '{extension}'. "
            f"Supported formats: {supported_list}"
        )
    
    return True


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
def download_from_s3(bucket: str, key: str) -> bytes:
    """
    Download a file from S3.
    
    Args:
        bucket: S3 bucket name
        key: S3 object key
        
    Returns:
        File content as bytes
        
    Raises:
        Exception: If download fails
    """
    try:
        response = s3_client.get_object(Bucket=bucket, Key=key)
        return response['Body'].read()
    except Exception as e:
        raise Exception(f"Failed to download from S3: {str(e)}")


def upload_to_s3(bucket: str, key: str, content: bytes, content_type: str = "audio/mpeg") -> str:
    """
    Upload a file to S3.
    
    Args:
        bucket: S3 bucket name
        key: S3 object key
        content: File content as bytes
        content_type: MIME type of the content
        
    Returns:
        S3 URI of uploaded file
        
    Raises:
        Exception: If upload fails
    """
    try:
        s3_client.put_object(
            Bucket=bucket,
            Key=key,
            Body=content,
            ContentType=content_type
        )
        return f"s3://{bucket}/{key}"
    except Exception as e:
        raise Exception(f"Failed to upload to S3: {str(e)}")


def process_text_with_polly(text_content: str, audio_id: str) -> bytes:
    """
    Process text content using Amazon Polly text-to-speech.
    
    Args:
        text_content: Text to convert to speech
        audio_id: Audio ID for tracking
        
    Returns:
        Audio content as bytes (MP3 format)
        
    Raises:
        Exception: If Polly synthesis fails
    """
    try:
        # Limit text length for Polly (max 3000 characters for standard, 6000 for SSML)
        max_chars = 3000
        if len(text_content) > max_chars:
            text_content = text_content[:max_chars]
            logger.info(f"Truncated text to {max_chars} characters for audio_id: {audio_id}")
        
        # Use Neural engine with Joanna voice for soothing sleep audio
        response = polly_client.synthesize_speech(
            Text=text_content,
            OutputFormat='mp3',
            VoiceId='Joanna',
            Engine='neural'
        )
        
        return response['AudioStream'].read()
    except Exception as e:
        raise Exception(f"Polly synthesis failed: {str(e)}")


def process_audio_file(content: bytes, audio_id: str) -> bytes:
    """
    Process audio file (passthrough for now, future enhancement for normalization).
    
    Args:
        content: Audio file content
        audio_id: Audio ID for tracking
        
    Returns:
        Processed audio content
    """
    # For now, just return the original content
    # Future: Add audio normalization, enhancement, mixing with ambient sounds
    logger.info(f"Audio file passthrough for audio_id: {audio_id}, size: {len(content)} bytes")
    return content


def update_dynamodb_with_output(audio_id: str, output_location: str, file_size: int) -> None:
    """
    Update DynamoDB with output file location and metadata.
    
    Args:
        audio_id: Audio ID (DynamoDB partition key)
        output_location: S3 URI of output file
        file_size: Size of output file in bytes
        
    Raises:
        Exception: If DynamoDB update fails
    """
    try:
        table = dynamodb.Table(TABLE_NAME)
        table.update_item(
            Key={'audioId': audio_id},
            UpdateExpression='SET outputLocation = :loc, outputFileSize = :size, updatedAt = :timestamp',
            ExpressionAttributeValues={
                ':loc': output_location,
                ':size': file_size,
                ':timestamp': datetime.utcnow().isoformat() + 'Z'
            }
        )
        logger.info(f"Updated DynamoDB for audio_id: {audio_id} with output location")
    except Exception as e:
        raise Exception(f"Failed to update DynamoDB: {str(e)}")


    """
    Lambda handler for audio processing with input validation.
    Enhanced with structured logging and X-Ray compatible tracing.
    Enhanced with real audio processing logic - downloads from S3, processes,
    uploads to output bucket, and updates DynamoDB with metadata.
    
        event: Input event from Step Functions containing S3 event details
        context: Lambda context object
        
    Returns:
        Dict containing processing result with audioId, status, and metadata
        Dict containing processing result with audioId, status, output location, and metadata
    # Extract request ID from Lambda context for correlation
    request_id = context.request_id if context else "local-test"
    start_time = time.time()
    
    try:
        # Structured log: Processing started
        log_structured(
            "INFO",
            "Audio processing started",
            context={
                "event_type": "processing_start",
                "function_name": context.function_name if context else "unknown"
            },
            request_id=request_id
        )
        
        # Validate S3 event structure and extract fields
        validated_data = validate_s3_event(event)
        bucket_name = validated_data["bucket"]
        audio_id = validated_data["key"]
        
        # Structured log: Validation successful
        log_structured(
            "INFO",
            "S3 event validation successful",
            context={
                "event_type": "validation_success",
                "audio_id": audio_id,
                "bucket": bucket_name
            },
            request_id=request_id
        )
        
        # Validate file extension
        validate_file_extension(audio_id)
        
        # Structured log: File extension validated
        processing_time = time.time() - start_time
            "INFO",
            "File extension validation successful",
            context={
                "event_type": "extension_validation_success",
                "audio_id": audio_id,
                "processing_time_ms": int(processing_time * 1000)
            },
            request_id=request_id
        )
        
        # Download input file from S3
        log_structured(
            "INFO",
            "Downloading input file from S3",
            context={
                "event_type": "s3_download_start",
                "audio_id": audio_id,
                "bucket": bucket_name
            },
            request_id=request_id
        )
        
        input_content = download_from_s3(bucket_name, audio_id)
        
        log_structured(
            "INFO",
            "Input file downloaded successfully",
            context={
                "event_type": "s3_download_success",
                "audio_id": audio_id,
                "file_size_bytes": len(input_content)
            },
            request_id=request_id
        )
        
        # Process based on file type
        output_content = None
        output_key = None
        
        if audio_id.lower().endswith('.txt'):
            # Text file - use Polly for TTS
            log_structured("INFO", "Processing text file with Polly TTS",
                          context={"event_type": "polly_processing_start", "audio_id": audio_id},
                          request_id=request_id)
            
            text_content = input_content.decode('utf-8')
            output_content = process_text_with_polly(text_content, audio_id)
            output_key = f"processed/{audio_id.rsplit('.', 1)[0]}.mp3"
        else:
            # Audio file - passthrough (future: enhancement/normalization)
            log_structured("INFO", "Processing audio file",
                          context={"event_type": "audio_processing_start", "audio_id": audio_id},
                          request_id=request_id)
            
            output_content = process_audio_file(input_content, audio_id)
            output_key = f"processed/{audio_id}"
        
        # Upload processed audio to output bucket
        log_structured("INFO", "Uploading processed audio to output bucket",
                      context={"event_type": "s3_upload_start", "output_key": output_key},
                      request_id=request_id)
        
        output_location = upload_to_s3(OUTPUT_BUCKET_NAME, output_key, output_content)
        
        log_structured("INFO", "Processed audio uploaded successfully",
                      context={"event_type": "s3_upload_success", "output_location": output_location,
                              "output_size_bytes": len(output_content)},
                      request_id=request_id)
        
        # Update DynamoDB with output location
        update_dynamodb_with_output(audio_id, output_location, len(output_content))
        
        # Calculate total processing time
        processing_time = time.time() - start_time
        
        # Return success response with output metadata
        result = {
            "statusCode": 200,
            "audioId": audio_id,
            "bucket": bucket_name,
            "outputLocation": output_location,
            "outputKey": output_key,
            "outputSizeBytes": len(output_content),
            "validationStatus": "PASSED",
            "message": "Audio processing completed successfully - file downloaded, processed, and uploaded",
            "processingTimeMs": int(processing_time * 1000)
        }
        
        # Structured log: Processing completed
        log_structured(
            "INFO",
            "Audio processing completed successfully",
            context={
                "event_type": "processing_complete",
                "audio_id": audio_id,
                "status": "success",
                "processing_time_ms": int(processing_time * 1000)
            },
            request_id=request_id
        )
        
        return result
        
    except ValidationError as e:
        # Structured log: Validation error
        log_structured("ERROR", "Validation error occurred", 
                      context={"event_type": "validation_error", "error": str(e)},
                      request_id=request_id)
        # Re-raise validation errors so Step Functions can catch and handle them
        raise
    except Exception as e:
        # Structured log: Unexpected error
        log_structured("ERROR", "Unexpected error during processing",
                      context={"event_type": "processing_error", "error": str(e)},
                      request_id=request_id)
        raise
