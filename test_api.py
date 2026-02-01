#!/usr/bin/env python3
"""
Test script for AI Fraud Detection API
Demonstrates API usage with sample requests
"""

import requests
import json
import os
from io import BytesIO

# API configuration
BASE_URL = "http://localhost:8081/api/v1"

def get_api_key():
    """Get the valid API key from the health endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            return data.get('authentication', {}).get('demo_key', 'fraud_detection_api_key_2026')
        else:
            return 'fraud_detection_api_key_2026'
    except:
        return 'fraud_detection_api_key_2026'

# Get the API key dynamically
API_KEY = get_api_key()
HEADERS = {"X-API-Key": API_KEY}

def test_health_check():
    """Test health check endpoint"""
    print("Testing health check...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print("-" * 50)

def test_analyze_text():
    """Test text analysis endpoint"""
    print("Testing text analysis...")
    
    # Test cases
    test_cases = [
        {
            "name": "Tech Support Scam",
            "text": "Hello, this is Microsoft technical support. We have detected suspicious activity on your computer. Please provide your credit card information to verify your identity and we will fix the problem immediately."
        },
        {
            "name": "Financial Scam",
            "text": "This is your bank calling. There has been fraudulent activity on your account. Please confirm your social security number and PIN to secure your account immediately."
        },
        {
            "name": "Legitimate Call",
            "text": "Hello, this is Dr. Smith's office calling to confirm your appointment tomorrow at 2 PM. Please call us back if you need to reschedule."
        },
        {
            "name": "Hindi Scam",
            "text": "नमस्ते, मैं बैंक से कॉल कर रहा हूं। आपके खाते में संदिग्ध गतिविधि है। कृपया अपना पिन नंबर बताएं।"
        },
        {
            "name": "Telugu Legitimate",
            "text": "మీ డాక్టర్ అపాయింట్మెంట్ రేపు మధ్యాహ్నం 2 గంటలకు ఉంది. దయచేసి సమయానికి రండి।"
        }
    ]
    
    for test_case in test_cases:
        print(f"\nTesting: {test_case['name']}")
        data = {"text": test_case["text"]}
        
        response = requests.post(
            f"{BASE_URL}/analyze-text",
            headers={**HEADERS, "Content-Type": "application/json"},
            json=data
        )
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Is Fraud: {result['is_fraud']}")
            print(f"Risk Score: {result['risk_score']}")
            print(f"Category: {result['predicted_category']}")
            print(f"Language: {result['language_detected']}")
            print(f"Explanations: {result['explanations']}")
        else:
            print(f"Error: {response.text}")
        print("-" * 30)

def test_model_info():
    """Test model info endpoint"""
    print("Testing model info...")
    response = requests.get(f"{BASE_URL}/model-info", headers=HEADERS)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print("-" * 50)

def test_train_model():
    """Test model training endpoint"""
    print("Testing model training...")
    
    training_data = {
        "training_data": [
            {
                "text": "This is a new scam pattern we want to detect",
                "category": "phishing"
            },
            {
                "text": "Another legitimate call example for training",
                "category": "legitimate"
            }
        ]
    }
    
    response = requests.post(
        f"{BASE_URL}/train",
        headers={**HEADERS, "Content-Type": "application/json"},
        json=training_data
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print("-" * 50)

def create_mock_audio_file():
    """Create a mock audio file for testing"""
    # Create a simple WAV file header (mock)
    wav_header = b'RIFF\x24\x08\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00\x44\xac\x00\x00\x88X\x01\x00\x02\x00\x10\x00data\x00\x08\x00\x00'
    # Add some mock audio data
    mock_audio_data = b'\x00' * 2048  # Silent audio data
    
    return wav_header + mock_audio_data

def test_analyze_audio():
    """Test audio analysis endpoint"""
    print("Testing audio analysis...")
    
    # Create mock audio file
    audio_data = create_mock_audio_file()
    
    files = {
        'audio': ('test_call.wav', BytesIO(audio_data), 'audio/wav')
    }
    
    response = requests.post(
        f"{BASE_URL}/analyze-audio",
        headers=HEADERS,
        files=files
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Is Fraud: {result['is_fraud']}")
        print(f"Risk Score: {result['risk_score']}")
        print(f"Category: {result['predicted_category']}")
        print(f"Audio Processed: {result['audio_processed']}")
        print(f"Transcript: {result.get('transcript', 'N/A')[:100]}...")
    else:
        print(f"Error: {response.text}")
    print("-" * 50)

def test_authentication():
    """Test API authentication"""
    print("Testing authentication...")
    
    # Test without API key
    response = requests.get(f"{BASE_URL}/model-info")
    print(f"Without API key - Status: {response.status_code}")
    
    # Test with wrong API key
    wrong_headers = {"X-API-Key": "wrong_key"}
    response = requests.get(f"{BASE_URL}/model-info", headers=wrong_headers)
    print(f"With wrong API key - Status: {response.status_code}")
    
    # Test with correct API key
    response = requests.get(f"{BASE_URL}/model-info", headers=HEADERS)
    print(f"With correct API key - Status: {response.status_code}")
    print("-" * 50)

def main():
    """Run all tests"""
    print("AI Fraud Detection API Test Suite")
    print("=" * 50)
    
    # Get and display API key
    global API_KEY, HEADERS
    API_KEY = get_api_key()
    HEADERS = {"X-API-Key": API_KEY}
    print(f"Using API Key: {API_KEY}")
    print()
    
    try:
        test_health_check()
        test_authentication()
        test_model_info()
        test_analyze_text()
        test_analyze_audio()
        test_train_model()
        
        print("\nAll tests completed!")
        
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to API. Make sure the server is running on localhost:8081")
    except Exception as e:
        print(f"Error running tests: {e}")

if __name__ == "__main__":
    main()