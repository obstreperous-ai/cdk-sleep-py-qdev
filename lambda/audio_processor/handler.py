"""
Lambda handler for audio processing in the Sleep Audio Pipeline.

Issue #8 Enhancement: Added input validation for S3 events and file format checking
for future audio processing, metadata enrichment, or validation logic.

Current functionality:
- Receives input from Step Functions state machine
- Logs S3 event details and audioId
- Returns a simple success response with metadata
- Basic error handling
- Input validation for required fields (bucket, key)
- File extension validation (rejects unsupported formats)

Future enhancements:
- File validation (format, size, content-type)
- Audio metadata extraction (duration, bitrate, codec)
- Content analysis and categorization
- Integration with additional processing services
"""

import json
import logging
import os
from typing import Dict, Any

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Environment variables
TABLE_NAME = os.environ.get("TABLE_NAME", "SleepAudioMetadataTable")

# Supported audio file extensions for the sleep audio pipeline
SUPPORTED_EXTENSIONS = {".mp3", ".wav", ".flac", ".txt", ".m4a", ".ogg"}


class ValidationError(Exception):
    """Custom exception for input validation errors."""
    pass


def validate_s3_event(event: Dict[str, Any]) -> Dict[str, str]:
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
    
    Args:
        event: Input event from Step Functions containing S3 event details
        context: Lambda context object
        
    Returns:
        Dict containing processing result with audioId, status, and metadata
    """
    try:
        # Log the incoming event for debugging
        logger.info(f"Received event: {json.dumps(event)}")
        
        # Validate S3 event structure and extract fields
        validated_data = validate_s3_event(event)
        bucket_name = validated_data["bucket"]
        audio_id = validated_data["key"]
        
        logger.info(f"Validated S3 event - AudioId: {audio_id}, Bucket: {bucket_name}")
        
        # Validate file extension
        validate_file_extension(audio_id)
        logger.info(f"File extension validated for: {audio_id}")
        
        # Placeholder for future processing logic (Issue #8+)
        # Future enhancements:
        # - Extract audio metadata (duration, bitrate, codec)
        # - Validate file size limits
        # - Perform content analysis
        # - Check for duplicate uploads
        
        # Return success response with basic metadata
        return {
            "statusCode": 200,
            "audioId": audio_id,
            "bucket": bucket_name,
            "validationStatus": "PASSED",
            "message": "Input validation and audio processing completed successfully"
        }
        
    except ValidationError as e:
        logger.error(f"Validation error: {str(e)}")
        # Re-raise validation errors so Step Functions can catch and handle them
        raise
    except Exception as e:
        logger.error(f"Error processing audio: {str(e)}", exc_info=True)
        raise
