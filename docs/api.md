# AI Fraud Detection API Documentation

## Overview

The AI Fraud Detection API is a fully self-contained, offline-first system for analyzing phone call audio and transcripts to detect potential scams and fraudulent activities.

## Base URL
```
http://localhost:8081/api/v1
```

## Authentication

All API endpoints (except `/health`) require authentication using an API key in the request header:

```
X-API-Key: fraud_detection_api_key_2026
```

### Getting the API Key

The current API key can be retrieved from the health endpoint:

```bash
curl -X GET http://localhost:8081/api/v1/health
```

Response includes the expected API key:
```json
{
  "status": "healthy",
  "authentication": {
    "required": true,
    "header": "X-API-Key",
    "demo_key": "fraud_detection_api_key_2026"
  }
}
```

### Environment Variable Configuration

You can set a custom API key using the `FRAUD_API_KEY` environment variable:

```bash
export FRAUD_API_KEY="your_custom_api_key_here"
python app.py
```

If no environment variable is set, the default demo key `fraud_detection_api_key_2026` is used.

## Endpoints

### 1. Health Check

Check the API status and service availability.

**Endpoint:** `GET /health`

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "services": {
    "fraud_detector": "online",
    "speech_processor": "online",
    "model_trainer": "online"
  }
}
```

### 2. Analyze Audio

Analyze an audio file for fraud detection.

**Endpoint:** `POST /analyze-audio`

**Headers:**
- `X-API-Key: fraud_detection_api_key_2026`
- `Content-Type: multipart/form-data`

**Parameters:**
- `audio` (file): Audio file (WAV, MP3, MP4, M4A, FLAC, OGG, WMA)

**Response:**
```json
{
  "is_fraud": true,
  "risk_score": 85,
  "risk_level": "high",
  "predicted_category": "tech_support",
  "confidence": 0.92,
  "language_detected": "en",
  "transcript": "Hello, this is Microsoft technical support...",
  "audio_processed": true,
  "explanations": [
    "Contains 3 urgency indicators",
    "Requests personal information",
    "Contains suspicious phrases",
    "High confidence prediction based on learned patterns"
  ],
  "analysis_timestamp": "2026-02-01T10:30:00.000Z",
  "model_version": "1.0.0"
}
```

### 3. Analyze Text

Analyze a text transcript for fraud detection.

**Endpoint:** `POST /analyze-text`

**Headers:**
- `X-API-Key: fraud_detection_api_key_2026`
- `Content-Type: application/json`

**Request Body:**
```json
{
  "text": "Hello, this is Microsoft technical support. We have detected suspicious activity on your computer..."
}
```

**Response:**
```json
{
  "is_fraud": true,
  "risk_score": 85,
  "risk_level": "high",
  "predicted_category": "tech_support",
  "confidence": 0.92,
  "language_detected": "en",
  "audio_processed": false,
  "explanations": [
    "Contains 3 urgency indicators",
    "Requests personal information",
    "Contains suspicious phrases",
    "High confidence prediction based on learned patterns"
  ],
  "analysis_timestamp": "2026-02-01T10:30:00.000Z",
  "model_version": "1.0.0"
}
```

### 4. Train Model

Train or retrain the fraud detection model with new data.

**Endpoint:** `POST /train`

**Headers:**
- `X-API-Key: fraud_detection_api_key_2026`
- `Content-Type: application/json`

**Request Body:**
```json
{
  "training_data": [
    {
      "text": "This is a scam call transcript...",
      "category": "tech_support"
    },
    {
      "text": "This is a legitimate call transcript...",
      "category": "legitimate"
    }
  ]
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Model trained successfully",
  "training_samples": 150,
  "train_accuracy": 0.95,
  "test_accuracy": 0.89,
  "cv_mean_accuracy": 0.91,
  "model_path": "models/fraud_model.joblib",
  "timestamp": "2026-02-01T10:30:00.000Z"
}
```

### 5. Model Information

Get information about the current fraud detection model.

**Endpoint:** `GET /model-info`

**Headers:**
- `X-API-Key: fraud_detection_api_key_2026`

**Response:**
```json
{
  "created_at": "2026-02-01T10:00:00.000Z",
  "version": "1.0.0",
  "categories": {
    "0": "tech_support",
    "1": "financial",
    "2": "romance",
    "3": "lottery_prize",
    "4": "phishing",
    "5": "robocall",
    "6": "legitimate"
  },
  "features": "TF-IDF (max_features=5000, ngram_range=(1,2))",
  "algorithm": "Logistic Regression",
  "training_samples": 150,
  "train_accuracy": 0.95,
  "test_accuracy": 0.89,
  "cv_mean_accuracy": 0.91
}
```

## Response Fields

### Fraud Analysis Response

- `is_fraud` (boolean): Whether the call is classified as fraudulent
- `risk_score` (integer): Risk score from 0-100
- `risk_level` (string): Risk level (very_low, low, medium, high)
- `predicted_category` (string): Predicted scam category or "legitimate"
- `confidence` (float): Model confidence score (0-1)
- `language_detected` (string): Detected language code (en, hi, te)
- `transcript` (string): Transcribed text (only for audio analysis)
- `audio_processed` (boolean): Whether audio was processed
- `explanations` (array): Human-readable reasons for the decision
- `analysis_timestamp` (string): ISO timestamp of analysis
- `model_version` (string): Version of the model used

### Scam Categories

- `tech_support`: Technical support scams
- `financial`: Banking and financial scams
- `romance`: Romance and relationship scams
- `lottery_prize`: Lottery and prize scams
- `phishing`: Phishing and credential theft
- `robocall`: Automated robocall scams
- `legitimate`: Legitimate calls

### Risk Levels

- `very_low`: Risk score 0-29
- `low`: Risk score 30-59
- `medium`: Risk score 60-79
- `high`: Risk score 80-100

## Error Responses

All error responses follow this format:

```json
{
  "error": "Error message",
  "message": "Detailed error description"
}
```

### Common Error Codes

- `400 Bad Request`: Invalid request data
- `401 Unauthorized`: Invalid or missing API key
- `413 Payload Too Large`: File size exceeds 50MB limit
- `500 Internal Server Error`: Server processing error

## Supported Languages

The API supports multilingual analysis for:

- **English (en)**: Full feature support
- **Hindi (hi)**: Text analysis with language-specific fraud patterns
- **Telugu (te)**: Text analysis with language-specific fraud patterns

Mixed-language text is automatically detected and processed appropriately.

## Rate Limits

- No rate limits for sandbox API key
- Maximum file size: 50MB
- Maximum request timeout: 30 seconds

## Example Usage

### cURL Examples

**Analyze Text:**
```bash
curl -X POST http://localhost:8081/api/v1/analyze-text \
  -H "X-API-Key: fraud_detection_api_key_2026" \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello, this is Microsoft support. Your computer has a virus."}'
```

**Analyze Audio:**
```bash
curl -X POST http://localhost:8081/api/v1/analyze-audio \
  -H "X-API-Key: fraud_detection_api_key_2026" \
  -F "audio=@sample_call.wav"
```

**Health Check:**
```bash
curl -X GET http://localhost:8081/api/v1/health
```

## Offline Operation

The API is designed to work completely offline:

- No internet connection required
- No external API dependencies
- All models and data stored locally
- Speech recognition uses offline engines
- Language detection works offline

This makes it suitable for deployment in low-connectivity environments or secure networks where internet access is restricted.