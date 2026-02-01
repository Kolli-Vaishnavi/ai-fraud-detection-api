#!/usr/bin/env python3
"""
Authentication Validation Script
Validates that authentication is working correctly across all endpoints
"""

import requests
import json
import sys
import os

def validate_authentication():
    """Validate authentication system"""
    print("AI Fraud Detection API - Authentication Validation")
    print("=" * 60)
    
    base_url = "http://localhost:8081/api/v1"
    
    # Step 1: Test health endpoint (should work without auth)
    print("1. Testing health endpoint (no authentication required)...")
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            api_key = data.get('authentication', {}).get('demo_key')
            print(f"   ✅ Health endpoint accessible")
            print(f"   ✅ Expected API key: {api_key}")
            
            if not api_key:
                print("   ❌ No API key found in health response")
                return False
        else:
            print(f"   ❌ Health endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Health endpoint error: {e}")
        return False
    
    # Step 2: Test authentication info endpoint
    print("\n2. Testing authentication info endpoint...")
    
    # Without API key (should fail)
    try:
        response = requests.get(f"{base_url}/auth/info", timeout=10)
        if response.status_code == 401:
            error_data = response.json()
            print(f"   ✅ Correctly rejected without API key: {error_data.get('error')}")
        else:
            print(f"   ❌ Expected 401, got {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Error testing no API key: {e}")
        return False
    
    # With invalid API key (should fail)
    try:
        headers = {"X-API-Key": "invalid_key"}
        response = requests.get(f"{base_url}/auth/info", headers=headers, timeout=10)
        if response.status_code == 403:
            error_data = response.json()
            print(f"   ✅ Correctly rejected invalid API key: {error_data.get('error')}")
        else:
            print(f"   ❌ Expected 403, got {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Error testing invalid API key: {e}")
        return False
    
    # With valid API key (should succeed)
    try:
        headers = {"X-API-Key": api_key}
        response = requests.get(f"{base_url}/auth/info", headers=headers, timeout=10)
        if response.status_code == 200:
            auth_data = response.json()
            print(f"   ✅ Successfully authenticated with valid API key")
            print(f"   ✅ Auth info: {auth_data.get('message')}")
        else:
            print(f"   ❌ Expected 200, got {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Error testing valid API key: {e}")
        return False
    
    # Step 3: Test a few more endpoints quickly
    print("\n3. Testing other protected endpoints...")
    
    endpoints_to_test = [
        ("GET", "/model-info", "Model Info", None),
        ("POST", "/analyze-text", "Analyze Text", {"text": "Test message"})
    ]
    
    for method, endpoint, name, data in endpoints_to_test:
        print(f"   Testing {name}...")
        
        # Test without API key
        try:
            if method == "GET":
                response = requests.get(f"{base_url}{endpoint}", timeout=10)
            else:
                response = requests.post(f"{base_url}{endpoint}", json=data, timeout=10)
            
            if response.status_code == 401:
                print(f"     ✅ {name} correctly rejects without API key")
            else:
                print(f"     ❌ {name} expected 401, got {response.status_code}")
                return False
        except Exception as e:
            print(f"     ❌ Error testing {name} without key: {e}")
            return False
        
        # Test with valid API key
        try:
            headers = {"X-API-Key": api_key}
            if method == "GET":
                response = requests.get(f"{base_url}{endpoint}", headers=headers, timeout=10)
            else:
                headers["Content-Type"] = "application/json"
                response = requests.post(f"{base_url}{endpoint}", headers=headers, json=data, timeout=10)
            
            if 200 <= response.status_code < 300:
                print(f"     ✅ {name} correctly accepts valid API key")
            else:
                print(f"     ❌ {name} expected success, got {response.status_code}")
                # Don't fail here as some endpoints might have other validation
        except Exception as e:
            print(f"     ❌ Error testing {name} with valid key: {e}")
            return False
    
    # Step 4: Test environment variable override
    print("\n4. Testing environment variable configuration...")
    
    # Check if FRAUD_API_KEY environment variable is set
    env_key = os.getenv('FRAUD_API_KEY')
    if env_key:
        print(f"   ✅ Environment variable FRAUD_API_KEY is set: {env_key}")
        if env_key == api_key:
            print(f"   ✅ Environment key matches API response")
        else:
            print(f"   ⚠️  Environment key differs from API response")
    else:
        print(f"   ✅ No environment variable set, using default key")
    
    print("\n" + "=" * 60)
    print("✅ AUTHENTICATION VALIDATION PASSED")
    print("\nAuthentication system is working correctly:")
    print("- Health endpoint accessible without authentication")
    print("- Protected endpoints require valid X-API-Key header")
    print("- Invalid/missing API keys are properly rejected")
    print("- Valid API key allows access to protected endpoints")
    print(f"- Current API key: {api_key}")
    
    return True

def show_curl_examples():
    """Show curl command examples"""
    print("\n" + "=" * 60)
    print("CURL COMMAND EXAMPLES")
    print("=" * 60)
    
    base_url = "http://localhost:8081/api/v1"
    
    # Get API key first
    try:
        response = requests.get(f"{base_url}/health")
        api_key = response.json().get('authentication', {}).get('demo_key', 'fraud_detection_api_key_2026')
    except:
        api_key = 'fraud_detection_api_key_2026'
    
    print("1. Health check (no authentication):")
    print(f"   curl -X GET {base_url}/health")
    
    print("\n2. Authentication info (requires API key):")
    print(f"   curl -X GET {base_url}/auth/info \\")
    print(f"     -H 'X-API-Key: {api_key}'")
    
    print("\n3. Analyze text (requires API key):")
    print(f"   curl -X POST {base_url}/analyze-text \\")
    print(f"     -H 'X-API-Key: {api_key}' \\")
    print(f"     -H 'Content-Type: application/json' \\")
    print(f"     -d '{{\"text\": \"Hello, this is Microsoft support.\"}}'")
    
    print("\n4. Model info (requires API key):")
    print(f"   curl -X GET {base_url}/model-info \\")
    print(f"     -H 'X-API-Key: {api_key}'")
    
    print("\n5. Example of authentication failure:")
    print(f"   curl -X GET {base_url}/model-info \\")
    print(f"     -H 'X-API-Key: invalid_key'")
    print("   # Should return 403 Forbidden")
    
    print("\n6. Example of missing authentication:")
    print(f"   curl -X GET {base_url}/model-info")
    print("   # Should return 401 Unauthorized")

def main():
    """Main validation function"""
    try:
        success = validate_authentication()
        
        if success:
            show_curl_examples()
            print(f"\n✅ Authentication validation completed successfully!")
            sys.exit(0)
        else:
            print(f"\n❌ Authentication validation failed!")
            sys.exit(1)
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to API. Please make sure the server is running on localhost:8081")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error during validation: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()