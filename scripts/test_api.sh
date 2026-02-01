#!/bin/bash

# AI Fraud Detection API - Test Script

echo "Testing AI Fraud Detection API..."

API_URL="http://localhost:8081/api/v1"

# Get API key from health endpoint
echo "Getting API key from health endpoint..."
API_KEY=$(curl -s -X GET "$API_URL/health" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    print(data.get('authentication', {}).get('demo_key', 'fraud_detection_api_key_2026'))
except:
    print('fraud_detection_api_key_2026')
")

echo "Using API Key: $API_KEY"
echo ""

# Test health check
echo "1. Testing health check..."
curl -s -X GET "$API_URL/health" | python3 -m json.tool
echo ""

# Test text analysis
echo "2. Testing text analysis..."
curl -s -X POST "$API_URL/analyze-text" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello, this is Microsoft technical support. We have detected suspicious activity on your computer. Please provide your credit card information immediately."}' \
  | python3 -m json.tool
echo ""

# Test model info
echo "3. Testing model info..."
curl -s -X GET "$API_URL/model-info" \
  -H "X-API-Key: $API_KEY" \
  | python3 -m json.tool
echo ""

# Test authentication (should fail)
echo "4. Testing authentication (should fail)..."
curl -s -X GET "$API_URL/model-info" \
  -H "X-API-Key: wrong_key" \
  | python3 -m json.tool
echo ""

echo "API testing completed!"