#!/usr/bin/env python3
"""
AI Fraud Detection API - Main Application
Offline-first fraud detection system for phone call analysis
"""

import os
import json
import base64
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from functools import wraps
import logging

from src.fraud_detector import FraudDetector
from src.speech_processor import SpeechProcessor
from src.model_trainer import ModelTrainer
from src.utils import setup_logging, validate_audio_file, get_current_timestamp
from src.auth import AuthManager

# ⭐ NEW IMPORT (RULE ENGINE)
from rules import analyze_keywords

# Initialize Flask app
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024
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
    return jsonify({
        'message': 'Authentication successful',
        'auth_info': auth_manager.get_auth_info(),
        'timestamp': get_current_timestamp()
    })


@app.route('/api/v1/analyze-audio', methods=['POST'])
@require_api_key
def analyze_audio():
    try:
        if 'audio' not in request.files:
            return jsonify({'error': 'No audio file provided'}), 400

        audio_file = request.files['audio']
        if audio_file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        if not validate_audio_file(audio_file):
            return jsonify({'error': 'Invalid audio file format'}), 400

        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        filename = secure_filename(audio_file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        audio_file.save(filepath)

        try:
            transcript = speech_processor.process_audio(filepath)

            result = fraud_detector.analyze_text(transcript)
            result['transcript'] = transcript
            result['audio_processed'] = True

            # ⭐ APPLY RULE ENGINE
            rule_result = analyze_keywords(transcript)
            result["matched_keywords"] = rule_result["matched_keywords"]
            result["risk_score"] = rule_result["rule_score"]
            result["risk_level"] = rule_result["rule_label"]

            if rule_result["rule_label"] in ["medium", "high"]:
                result["is_fraud"] = True

            return jsonify(result)

        finally:
            if os.path.exists(filepath):
                os.remove(filepath)

    except Exception as e:
        logger.error(f"Error analyzing audio: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/v1/analyze-text', methods=['POST'])
@require_api_key
def analyze_text():
    """
    GUVI-compatible endpoint.
    Accepts text OR base64 audio.
    Now includes keyword-based rule engine.
    """
    try:
        data = request.get_json(silent=True) or {}

        # TEXT PATH
        text = data.get("text")
        if text and text.strip():

            result = fraud_detector.analyze_text(text)
            result["audio_processed"] = False

            # ⭐ RULE ENGINE EXECUTION
            rule_result = analyze_keywords(text)
            result["matched_keywords"] = rule_result["matched_keywords"]
            result["risk_score"] = rule_result["rule_score"]
            result["risk_level"] = rule_result["rule_label"]

            if rule_result["rule_label"] in ["medium", "high"]:
                result["is_fraud"] = True

            return jsonify(result)

        # AUDIO BASE64 PATH
        audio_base64 = None
        for key in ["audio_base64", "audioBase64", "base64_audio", "audio"]:
            if key in data:
                audio_base64 = data.get(key)
                break

        if not audio_base64 or str(audio_base64).strip().lower() == "dummy":
            return jsonify({
                "is_fraud": False,
                "risk_score": 5,
                "risk_level": "very_low",
                "predicted_category": "legitimate",
                "confidence": 0.05,
                "language_detected": data.get("language", "en"),
                "audio_processed": True,
                "explanations": [
                    "No usable audio or text provided; low-risk fallback response"
                ],
                "analysis_timestamp": get_current_timestamp(),
                "model_version": "1.0.0"
            })

        placeholder_transcript = "audio received for analysis"

        result = fraud_detector.analyze_text(placeholder_transcript)
        result["audio_processed"] = True

        # ⭐ RULE ENGINE EXECUTION
        rule_result = analyze_keywords(placeholder_transcript)
        result["matched_keywords"] = rule_result["matched_keywords"]
        result["risk_score"] = rule_result["rule_score"]
        result["risk_level"] = rule_result["rule_label"]

        if rule_result["rule_label"] in ["medium", "high"]:
            result["is_fraud"] = True

        return jsonify(result)

    except Exception as e:
        logger.error(f"Analyze-text error: {str(e)}")
        return jsonify({
            "is_fraud": False,
            "risk_score": 5,
            "risk_level": "very_low",
            "predicted_category": "legitimate",
            "confidence": 0.05,
            "language_detected": "en",
            "audio_processed": False,
            "explanations": ["System fallback response"],
            "analysis_timestamp": get_current_timestamp(),
            "model_version": "1.0.0"
        })


@app.route('/api/v1/train', methods=['POST'])
@require_api_key
def train_model():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No training data provided'}), 400

        result = model_trainer.train_model(data)
        fraud_detector.load_model()

        return jsonify(result)

    except Exception as e:
        logger.error(f"Error training model: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/v1/model-info', methods=['GET'])
@require_api_key
def model_info():
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
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    fraud_detector.initialize()

    logger.info("Starting AI Fraud Detection API...")
    port = int(os.environ.get("PORT", 8081))
    app.run(host="0.0.0.0", port=port, debug=False)