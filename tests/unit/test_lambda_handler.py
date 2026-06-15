"""
Unit tests for Lambda handler and helper functions.

Issue #15: Comprehensive test coverage for Lambda logic, including
validation functions, S3 operations, Polly integration, DynamoDB updates,
and error handling paths.
"""

import json
import pytest
from unittest.mock import Mock, patch, MagicMock
from io import BytesIO

# Import handler module
import sys
sys.path.insert(0, 'lambda/audio_processor')
from handler import (
    ValidationError,
    log_structured,
    validate_s3_event,
    validate_file_extension,
    download_from_s3,
    upload_to_s3,
    process_text_with_polly,
    process_audio_file,
    update_dynamodb_with_output,
    lambda_handler
)


# ============================================================================
# Test Fixtures
# ============================================================================

@pytest.fixture
def valid_s3_event():
    """Fixture for valid S3 event structure."""
    return {
        "detail": {
            "bucket": {
                "name": "test-input-bucket"
            },
            "object": {
                "key": "test-file.txt"
            }
        }
    }


@pytest.fixture
def lambda_context():
    """Fixture for Lambda context object."""
    context = Mock()
    context.request_id = "test-request-123"
    context.function_name = "SleepAudioProcessor"
    return context


# ============================================================================
# Test validate_s3_event
# ============================================================================

def test_validate_s3_event_success(valid_s3_event):
    """Test successful S3 event validation."""
    result = validate_s3_event(valid_s3_event)
    
    assert result["bucket"] == "test-input-bucket"
    assert result["key"] == "test-file.txt"


def test_validate_s3_event_empty_event():
    """Test validation fails with empty event."""
    with pytest.raises(ValidationError, match="Event is empty or None"):
        validate_s3_event(None)


def test_validate_s3_event_missing_detail():
    """Test validation fails when detail field is missing."""
    event = {}
    with pytest.raises(ValidationError, match="Missing 'detail' field"):
        validate_s3_event(event)


def test_validate_s3_event_missing_bucket_name():
    """Test validation fails when bucket name is missing."""
    event = {
        "detail": {
            "bucket": {},
            "object": {"key": "test.txt"}
        }
    }
    with pytest.raises(ValidationError, match="Missing or empty bucket name"):
        validate_s3_event(event)


def test_validate_s3_event_missing_object_key():
    """Test validation fails when object key is missing."""
    event = {
        "detail": {
            "bucket": {"name": "test-bucket"},
            "object": {}
        }
    }
    with pytest.raises(ValidationError, match="Missing or empty object key"):
        validate_s3_event(event)


# ============================================================================
# Test validate_file_extension
# ============================================================================

def test_validate_file_extension_txt():
    """Test validation passes for .txt files."""
    assert validate_file_extension("test.txt") is True


def test_validate_file_extension_mp3():
    """Test validation passes for .mp3 files."""
    assert validate_file_extension("test.mp3") is True


def test_validate_file_extension_wav():
    """Test validation passes for .wav files."""
    assert validate_file_extension("audio.wav") is True


def test_validate_file_extension_case_insensitive():
    """Test validation is case-insensitive."""
    assert validate_file_extension("test.TXT") is True
    assert validate_file_extension("test.MP3") is True


def test_validate_file_extension_unsupported():
    """Test validation fails for unsupported extensions."""
    with pytest.raises(ValidationError, match="Unsupported file extension"):
        validate_file_extension("test.pdf")


def test_validate_file_extension_no_extension():
    """Test validation fails for files without extension."""
    with pytest.raises(ValidationError, match="Unsupported file extension"):
        validate_file_extension("testfile")


# ============================================================================
# Test download_from_s3
# ============================================================================

@patch('handler.s3_client')
def test_download_from_s3_success(mock_s3_client):
    """Test successful S3 download."""
    # Mock S3 response
    mock_response = {
        'Body': BytesIO(b'test content')
    }
    mock_s3_client.get_object.return_value = mock_response
    
    result = download_from_s3("test-bucket", "test-key.txt")
    
    assert result == b'test content'
    mock_s3_client.get_object.assert_called_once_with(
        Bucket="test-bucket",
        Key="test-key.txt"
    )


@patch('handler.s3_client')
def test_download_from_s3_failure(mock_s3_client):
    """Test S3 download handles errors properly."""
    mock_s3_client.get_object.side_effect = Exception("S3 error")
    
    with pytest.raises(Exception, match="Failed to download from S3"):
        download_from_s3("test-bucket", "test-key.txt")


# ============================================================================
# Test upload_to_s3
# ============================================================================

@patch('handler.s3_client')
def test_upload_to_s3_success(mock_s3_client):
    """Test successful S3 upload."""
    result = upload_to_s3("test-bucket", "output/test.mp3", b'audio data')
    
    assert result == "s3://test-bucket/output/test.mp3"
    mock_s3_client.put_object.assert_called_once_with(
        Bucket="test-bucket",
        Key="output/test.mp3",
        Body=b'audio data',
        ContentType="audio/mpeg"
    )


@patch('handler.s3_client')
def test_upload_to_s3_with_custom_content_type(mock_s3_client):
    """Test S3 upload with custom content type."""
    result = upload_to_s3(
        "test-bucket",
        "output/test.wav",
        b'audio data',
        content_type="audio/wav"
    )
    
    assert result == "s3://test-bucket/output/test.wav"
    mock_s3_client.put_object.assert_called_once()
    call_args = mock_s3_client.put_object.call_args[1]
    assert call_args['ContentType'] == "audio/wav"


@patch('handler.s3_client')
def test_upload_to_s3_failure(mock_s3_client):
    """Test S3 upload handles errors properly."""
    mock_s3_client.put_object.side_effect = Exception("S3 error")
    
    with pytest.raises(Exception, match="Failed to upload to S3"):
        upload_to_s3("test-bucket", "test-key.mp3", b'data')


# ============================================================================
# Test process_text_with_polly
# ============================================================================

@patch('handler.polly_client')
def test_process_text_with_polly_success(mock_polly_client):
    """Test successful Polly text-to-speech processing."""
    # Mock Polly response
    mock_audio_stream = BytesIO(b'audio data from polly')
    mock_response = {
        'AudioStream': mock_audio_stream
    }
    mock_polly_client.synthesize_speech.return_value = mock_response
    
    result = process_text_with_polly("Test text", "audio-123")
    
    assert result == b'audio data from polly'
    mock_polly_client.synthesize_speech.assert_called_once()
    call_args = mock_polly_client.synthesize_speech.call_args[1]
    assert call_args['Text'] == "Test text"
    assert call_args['OutputFormat'] == 'mp3'
    assert call_args['VoiceId'] == 'Joanna'
    assert call_args['Engine'] == 'neural'


@patch('handler.polly_client')
def test_process_text_with_polly_truncates_long_text(mock_polly_client):
    """Test Polly processing truncates text longer than 3000 characters."""
    # Mock Polly response
    mock_audio_stream = BytesIO(b'audio data')
    mock_response = {'AudioStream': mock_audio_stream}
    mock_polly_client.synthesize_speech.return_value = mock_response
    
    # Create text longer than 3000 characters
    long_text = "a" * 5000
    
    result = process_text_with_polly(long_text, "audio-123")
    
    # Verify text was truncated to 3000 characters
    call_args = mock_polly_client.synthesize_speech.call_args[1]
    assert len(call_args['Text']) == 3000


@patch('handler.polly_client')
def test_process_text_with_polly_failure(mock_polly_client):
    """Test Polly processing handles errors properly."""
    mock_polly_client.synthesize_speech.side_effect = Exception("Polly error")
    
    with pytest.raises(Exception, match="Polly synthesis failed"):
        process_text_with_polly("Test text", "audio-123")


# ============================================================================
# Test process_audio_file
# ============================================================================

def test_process_audio_file_passthrough():
    """Test audio file processing (passthrough)."""
    content = b'audio file content'
    result = process_audio_file(content, "audio-123")
    
    # Currently just passes through
    assert result == content


# ============================================================================
# Test update_dynamodb_with_output
# ============================================================================

@patch('handler.dynamodb')
def test_update_dynamodb_with_output_success(mock_dynamodb):
    """Test successful DynamoDB update."""
    mock_table = MagicMock()
    mock_dynamodb.Table.return_value = mock_table
    
    update_dynamodb_with_output(
        "audio-123",
        "s3://bucket/output/audio-123.mp3",
        1024
    )
    
    mock_table.update_item.assert_called_once()
    call_args = mock_table.update_item.call_args[1]
    assert call_args['Key'] == {'audioId': 'audio-123'}
    assert ':loc' in call_args['ExpressionAttributeValues']
    assert call_args['ExpressionAttributeValues'][':loc'] == "s3://bucket/output/audio-123.mp3"
    assert call_args['ExpressionAttributeValues'][':size'] == 1024


@patch('handler.dynamodb')
def test_update_dynamodb_with_output_failure(mock_dynamodb):
    """Test DynamoDB update handles errors properly."""
    mock_table = MagicMock()
    mock_table.update_item.side_effect = Exception("DynamoDB error")
    mock_dynamodb.Table.return_value = mock_table
    
    with pytest.raises(Exception, match="Failed to update DynamoDB"):
        update_dynamodb_with_output("audio-123", "s3://bucket/file.mp3", 1024)


# ============================================================================
# Test lambda_handler - Success Paths
# ============================================================================

@patch('handler.update_dynamodb_with_output')
@patch('handler.upload_to_s3')
@patch('handler.process_text_with_polly')
@patch('handler.download_from_s3')
def test_lambda_handler_text_file_success(
    mock_download, mock_polly, mock_upload, mock_ddb_update,
    valid_s3_event, lambda_context
):
    """Test successful Lambda execution with text file."""
    # Mock return values
    mock_download.return_value = b'Sample text content for TTS'
    mock_polly.return_value = b'synthesized audio data'
    mock_upload.return_value = "s3://output-bucket/processed/test-file.mp3"
    
    result = lambda_handler(valid_s3_event, lambda_context)
    
    assert result["statusCode"] == 200
    assert result["audioId"] == "test-file.txt"
    assert result["validationStatus"] == "PASSED"
    assert result["outputLocation"] == "s3://output-bucket/processed/test-file.mp3"
    assert "processingTimeMs" in result
    
    # Verify functions were called correctly
    mock_download.assert_called_once_with("test-input-bucket", "test-file.txt")
    mock_polly.assert_called_once()
    mock_upload.assert_called_once()
    mock_ddb_update.assert_called_once()


@patch('handler.update_dynamodb_with_output')
@patch('handler.upload_to_s3')
@patch('handler.process_audio_file')
@patch('handler.download_from_s3')
def test_lambda_handler_audio_file_success(
    mock_download, mock_process_audio, mock_upload, mock_ddb_update,
    lambda_context
):
    """Test successful Lambda execution with audio file."""
    # Create event with audio file
    event = {
        "detail": {
            "bucket": {"name": "test-input-bucket"},
            "object": {"key": "test-audio.mp3"}
        }
    }
    
    # Mock return values
    mock_download.return_value = b'audio file data'
    mock_process_audio.return_value = b'processed audio data'
    mock_upload.return_value = "s3://output-bucket/processed/test-audio.mp3"
    
    result = lambda_handler(event, lambda_context)
    
    assert result["statusCode"] == 200
    assert result["audioId"] == "test-audio.mp3"
    assert result["outputKey"] == "processed/test-audio.mp3"
    
    # Verify audio processing path was used
    mock_process_audio.assert_called_once()


# ============================================================================
# Test lambda_handler - Error Paths
# ============================================================================

def test_lambda_handler_validation_error_empty_event(lambda_context):
    """Test Lambda handler raises ValidationError for empty event."""
    with pytest.raises(ValidationError):
        lambda_handler(None, lambda_context)


def test_lambda_handler_validation_error_unsupported_extension(lambda_context):
    """Test Lambda handler raises ValidationError for unsupported file extension."""
    event = {
        "detail": {
            "bucket": {"name": "test-bucket"},
            "object": {"key": "unsupported.pdf"}
        }
    }
    
    with pytest.raises(ValidationError, match="Unsupported file extension"):
        lambda_handler(event, lambda_context)


@patch('handler.download_from_s3')
def test_lambda_handler_s3_download_error(mock_download, valid_s3_event, lambda_context):
    """Test Lambda handler handles S3 download errors."""
    mock_download.side_effect = Exception("Failed to download from S3")
    
    with pytest.raises(Exception, match="Failed to download from S3"):
        lambda_handler(valid_s3_event, lambda_context)


# ============================================================================
# Test log_structured
# ============================================================================

@patch('handler.logger')
def test_log_structured_info_level(mock_logger):
    """Test structured logging at INFO level."""
    log_structured("INFO", "Test message", {"key": "value"}, "request-123")
    
    mock_logger.info.assert_called_once()
    logged_message = json.loads(mock_logger.info.call_args[0][0])
    assert logged_message["level"] == "INFO"
    assert logged_message["message"] == "Test message"
    assert logged_message["request_id"] == "request-123"
    assert logged_message["key"] == "value"


@patch('handler.logger')
def test_log_structured_error_level(mock_logger):
    """Test structured logging at ERROR level."""
    log_structured("ERROR", "Error occurred", {"error": "test error"})
    
    mock_logger.error.assert_called_once()
    logged_message = json.loads(mock_logger.error.call_args[0][0])
    assert logged_message["level"] == "ERROR"
    assert logged_message["message"] == "Error occurred"
