"""
Utility functions for the fraud detection API
"""

import os
import logging
from werkzeug.utils import secure_filename

def setup_logging():
    """Setup logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('fraud_detection.log'),
            logging.StreamHandler()
        ]
    )

def validate_audio_file(file):
    """Validate uploaded audio file"""
    if not file:
        return False
    
    # Check file extension
    allowed_extensions = {'wav', 'mp3', 'mp4', 'm4a', 'flac', 'ogg', 'wma'}
    filename = secure_filename(file.filename)
    
    if '.' not in filename:
        return False
    
    extension = filename.rsplit('.', 1)[1].lower()
    return extension in allowed_extensions

def sanitize_filename(filename):
    """Sanitize filename for safe storage"""
    return secure_filename(filename)

def ensure_directory_exists(directory):
    """Ensure directory exists, create if not"""
    os.makedirs(directory, exist_ok=True)

def get_file_size_mb(filepath):
    """Get file size in MB"""
    if os.path.exists(filepath):
        size_bytes = os.path.getsize(filepath)
        return size_bytes / (1024 * 1024)
    return 0

def clean_text(text):
    """Clean and normalize text"""
    if not text:
        return ""
    
    # Remove extra whitespace
    text = ' '.join(text.split())
    
    # Remove null characters
    text = text.replace('\x00', '')
    
    return text.strip()

def format_confidence_score(score):
    """Format confidence score as percentage"""
    return f"{score * 100:.1f}%"

def get_risk_color(risk_score):
    """Get color code for risk score visualization"""
    if risk_score >= 80:
        return "#FF4444"  # Red
    elif risk_score >= 60:
        return "#FF8800"  # Orange
    elif risk_score >= 30:
        return "#FFAA00"  # Yellow
    else:
        return "#44AA44"  # Green

def truncate_text(text, max_length=500):
    """Truncate text to maximum length"""
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."

def validate_api_request(data, required_fields):
    """Validate API request data"""
    if not data:
        return False, "No data provided"
    
    for field in required_fields:
        if field not in data:
            return False, f"Missing required field: {field}"
        
        if not data[field]:
            return False, f"Empty value for required field: {field}"
    
    return True, "Valid"

def create_error_response(message, code=400):
    """Create standardized error response"""
    return {
        'error': True,
        'message': message,
        'code': code,
        'timestamp': get_current_timestamp()
    }

def create_success_response(data):
    """Create standardized success response"""
    response = {
        'error': False,
        'timestamp': get_current_timestamp()
    }
    response.update(data)
    return response

def get_current_timestamp():
    """Get current timestamp in ISO format"""
    from datetime import datetime
    return datetime.now().isoformat()

def log_api_call(endpoint, method, status_code, response_time=None):
    """Log API call for monitoring"""
    logger = logging.getLogger('api_monitor')
    log_message = f"{method} {endpoint} - Status: {status_code}"
    
    if response_time:
        log_message += f" - Time: {response_time:.3f}s"
    
    logger.info(log_message)