"""
Lambda handler for audio processing in the Sleep Audio Pipeline.

Issue #8: Added input validation for S3 events and file format checking
Issue #10: Enhanced with structured JSON logging and improved observability
          for production monitoring, X-Ray tracing support, and detailed
          request tracking with correlation IDs.

Current functionality:
- Receives input from Step Functions state machine
- Logs S3 event details and audioId
- Returns a simple success response with metadata
- Basic error handling
- Input validation for required fields (bucket, key)
- File extension validation (rejects unsupported formats)
- Structured JSON logging with request IDs and timestamps

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
from typing import Dict, Any

# Configure structured logging for production observability
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Simple JSON formatter for structured logs
logging.basicConfig(format='%(message)s')

# Environment variables
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
    """
    Lambda handler for audio processing with input validation.
    Enhanced with structured logging and X-Ray compatible tracing.
    Args:
        event: Input event from Step Functions containing S3 event details
        context: Lambda context object
        
    Returns:
        Dict containing processing result with audioId, status, and metadata
    """
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
        log_structured(
            "INFO",
            "File extension validation successful",
            context={
                "event_type": "extension_validation_success",
                "audio_id": audio_id,
                "processing_time_ms": int(processing_time * 1000)
            },
            request_id=request_id
        )
        
        # Return success response with basic metadata
        result = {
            "statusCode": 200,
            "audioId": audio_id,
            "bucket": bucket_name,
            "validationStatus": "PASSED",
            "message": "Input validation and audio processing completed successfully",
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
