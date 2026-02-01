#!/usr/bin/env python3
"""
AI Fraud Detection API - Main Application
Offline-first fraud detection system for phone call analysis
"""

import os
import json
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from functools import wraps
import logging

from src.fraud_detector import FraudDetector
from src.speech_processor import SpeechProcessor
from src.model_trainer import ModelTrainer
from src.utils import setup_logging, validate_audio_file, get_current_timestamp
from src.auth import AuthManager

# Initialize Flask app
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size
app.config['UPLOAD_FOLDER'] = 'temp_uploads'

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Initialize components
fraud_detector = FraudDetector()
speech_processor = SpeechProcessor()
model_trainer = ModelTrainer()

# Initialize authentication manager
auth_manager = AuthManager()

def require_api_key(f):
    """Decorator to require API key authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_result = auth_manager.authenticate_request(request)
        if not auth_result['success']:
            return jsonify({
                'error': auth_result['error'],
                'message': auth_result['message']
            }), auth_result['status_code']
        return f(*args, **kwargs)
    return decorated_function

@app.route('/api/v1/health', methods=['GET'])
def health_check():
    """Health check endpoint - No authentication required"""
    return jsonify({
        'status': 'healthy',
        'version': '1.0.0',
        'services': {
            'fraud_detector': 'online',
            'speech_processor': 'online',
            'model_trainer': 'online',
            'authentication': 'online'
        },
        'authentication': {
            'required': True,
            'header': auth_manager.get_api_key_header(),
            'demo_key': auth_manager.get_expected_api_key()
        }
    })

@app.route('/api/v1/auth/info', methods=['GET'])
@require_api_key
def auth_info():
    """Get authentication information - Requires valid API key"""
    return jsonify({
        'message': 'Authentication successful',
        'auth_info': auth_manager.get_auth_info(),
        'timestamp': get_current_timestamp()
    })

@app.route('/api/v1/analyze-audio', methods=['POST'])
@require_api_key
def analyze_audio():
    """Analyze audio file for fraud detection"""
    try:
        if 'audio' not in request.files:
            return jsonify({'error': 'No audio file provided'}), 400
        
        audio_file = request.files['audio']
        if audio_file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Validate audio file
        if not validate_audio_file(audio_file):
            return jsonify({'error': 'Invalid audio file format'}), 400
        
        # Save temporary file
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        filename = secure_filename(audio_file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        audio_file.save(filepath)
        
        try:
            # Convert speech to text
            transcript = speech_processor.process_audio(filepath)
            
            # Analyze for fraud
            result = fraud_detector.analyze_text(transcript)
            
            # Add transcript to response
            result['transcript'] = transcript
            result['audio_processed'] = True
            
            return jsonify(result)
            
        finally:
            # Clean up temporary file
            if os.path.exists(filepath):
                os.remove(filepath)
                
    except Exception as e:
        logger.error(f"Error analyzing audio: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/v1/analyze-text', methods=['POST'])
@require_api_key
@app.route('/api/v1/analyze-text', methods=['POST'])
@require_api_key
def analyze_text():
    """Analyze text OR audio transcript for fraud detection"""
    try:
        data = request.get_json() or {}

        text = data.get("text")

        # 🧠 If text is missing, try audio base64
        if not text:
            audio_base64 = data.get("audio_base64") or data.get("audio")

            if not audio_base64:
                return jsonify({
                    "error": "No text or audio provided",
                    "message": "Provide either text or base64-encoded audio"
                }), 400

            # Decode base64 audio
            import base64
            audio_bytes = base64.b64decode(audio_base64)

            # Save temp audio file
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            temp_path = os.path.join(app.config['UPLOAD_FOLDER'], "temp_audio.wav")

            with open(temp_path, "wb") as f:
                f.write(audio_bytes)

            # Convert speech to text
            text = speech_processor.process_audio(temp_path)

            # Cleanup
            os.remove(temp_path)

        if not text.strip():
            return jsonify({'error': 'Empty transcript after processing'}), 400

        # 🔍 Analyze fraud
        result = fraud_detector.analyze_text(text)
        result["audio_processed"] = True if "audio_base64" in data else False
        result["transcript"] = text

        return jsonify(result)

    except Exception as e:
        logger.error(f"Error analyzing input: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/v1/train', methods=['POST'])
@require_api_key
def train_model():
    """Train or retrain the fraud detection model"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No training data provided'}), 400
        
        # Train the model
        result = model_trainer.train_model(data)
        
        # Reload the fraud detector with new model
        fraud_detector.load_model()
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error training model: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/v1/model-info', methods=['GET'])
@require_api_key
def model_info():
    """Get information about the current model"""
    try:
        info = fraud_detector.get_model_info()
        return jsonify(info)
        
    except Exception as e:
        logger.error(f"Error getting model info: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.errorhandler(413)
def too_large(e):
    return jsonify({'error': 'File too large. Maximum size is 50MB'}), 413

@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Endpoint not found'}), 404

if __name__ == '__main__':
    # Ensure upload directory exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Initialize model on startup
    fraud_detector.initialize()
    
    logger.info("Starting AI Fraud Detection API...")
    port = int(os.environ.get("PORT", 8081))
    app.run(host="0.0.0.0", port=port, debug=False)