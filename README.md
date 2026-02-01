# AI Fraud Detection API

A fully self-contained, offline-first fraud detection system for analyzing phone call audio and transcripts using machine learning.

## Features

- **Offline Speech-to-Text**: Convert audio to text without internet
- **ML-based Fraud Detection**: TF-IDF + Logistic Regression classifier
- **Multilingual Support**: English, Hindi, Telugu with auto-detection
- **Risk Scoring**: 0-100 continuous risk scores with explanations
- **Model Training**: Retrain models with new datasets
- **RESTful API**: Production-ready endpoints with authentication

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the API
python app.py

# Test authentication
python validate_auth.py

# Run comprehensive tests
python run_auth_tests.py
```

API will be available at `http://localhost:8081`

## Authentication

Use API key: `fraud_detection_api_key_2026`

You can also set a custom API key using environment variable:
```bash
export FRAUD_API_KEY="your_custom_key"
python app.py
```

## Endpoints

- `POST /api/v1/analyze-audio` - Analyze audio file for fraud
- `POST /api/v1/analyze-text` - Analyze transcript text
- `POST /api/v1/train` - Train/retrain the model
- `GET /api/v1/model-info` - Get model information
- `GET /api/v1/health` - Health check

See `docs/api.md` for detailed documentation.