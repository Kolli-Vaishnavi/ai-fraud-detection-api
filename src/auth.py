"""
Authentication Module
Centralized API key authentication for the fraud detection API
"""

import os
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class AuthManager:
    """Centralized authentication manager"""
    
    # Default API key for sandbox/demo usage
    DEFAULT_API_KEY = "fraud_detection_api_key_2026"
    
    def __init__(self):
        """Initialize authentication manager"""
        # Get API key from environment variable or use default
        self.api_key = os.getenv('FRAUD_API_KEY', self.DEFAULT_API_KEY)
        
        # Log the API key being used (for debugging)
        logger.info(f"Authentication initialized with API key: {self.api_key}")
        
        # Header name for API key
        self.api_key_header = 'X-API-Key'
    
    def authenticate_request(self, request) -> Dict[str, Any]:
        """
        Authenticate a Flask request
        
        Args:
            request: Flask request object
            
        Returns:
            Dict with authentication result
        """
        # Get API key from request headers
        provided_key = request.headers.get(self.api_key_header)
        
        # Check if API key is missing
        if not provided_key:
            return {
                'success': False,
                'error': 'Missing API key',
                'message': f'Please provide a valid {self.api_key_header} header',
                'status_code': 401
            }
        
        # Check if API key is empty
        if not provided_key.strip():
            return {
                'success': False,
                'error': 'Empty API key',
                'message': f'{self.api_key_header} header cannot be empty',
                'status_code': 401
            }
        
        # Check if API key is valid
        if provided_key != self.api_key:
            return {
                'success': False,
                'error': 'Invalid API key',
                'message': f'The provided {self.api_key_header} is not valid',
                'status_code': 403
            }
        
        # Authentication successful
        return {
            'success': True,
            'message': 'Authentication successful',
            'status_code': 200
        }
    
    def get_expected_api_key(self) -> str:
        """Get the expected API key for testing purposes"""
        return self.api_key
    
    def get_api_key_header(self) -> str:
        """Get the API key header name"""
        return self.api_key_header
    
    def validate_api_key_format(self, api_key: str) -> bool:
        """
        Validate API key format (basic validation)
        
        Args:
            api_key: API key to validate
            
        Returns:
            True if format is valid, False otherwise
        """
        if not api_key or not isinstance(api_key, str):
            return False
        
        # Basic format validation
        if len(api_key) < 10:  # Minimum length
            return False
        
        # Check for reasonable characters
        if not all(c.isalnum() or c in '_-' for c in api_key):
            return False
        
        return True
    
    def get_auth_info(self) -> Dict[str, Any]:
        """Get authentication configuration info"""
        return {
            'header_name': self.api_key_header,
            'expected_key': self.api_key,
            'key_source': 'environment' if os.getenv('FRAUD_API_KEY') else 'default',
            'key_length': len(self.api_key)
        }