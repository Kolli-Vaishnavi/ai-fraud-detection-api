#!/usr/bin/env python3
"""
Authentication Test Suite for AI Fraud Detection API
Tests API key authentication across all endpoints
"""

import requests
import json
import sys
from typing import Dict, List, Tuple

# API configuration
BASE_URL = "http://localhost:8081/api/v1"

class AuthTester:
    """Authentication testing class"""
    
    def __init__(self):
        self.base_url = BASE_URL
        self.valid_api_key = None
        self.test_results = []
        
    def get_valid_api_key(self) -> str:
        """Get the valid API key from health endpoint"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                return data.get('authentication', {}).get('demo_key', 'fraud_detection_api_key_2026')
            else:
                print(f"Warning: Could not get API key from health endpoint. Using default.")
                return 'fraud_detection_api_key_2026'
        except Exception as e:
            print(f"Warning: Error getting API key from health endpoint: {e}")
            return 'fraud_detection_api_key_2026'
    
    def test_health_endpoint_no_auth(self) -> bool:
        """Test that health endpoint works without authentication"""
        print("Testing health endpoint (no auth required)...")
        
        try:
            response = requests.get(f"{self.base_url}/health", timeout=10)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                print(f"✅ Health endpoint accessible without auth")
                print(f"   Status: {data.get('status')}")
                print(f"   Expected API Key: {data.get('authentication', {}).get('demo_key')}")
                self.valid_api_key = data.get('authentication', {}).get('demo_key')
            else:
                print(f"❌ Health endpoint failed: {response.status_code}")
                
            self.test_results.append(("Health endpoint (no auth)", success))
            return success
            
        except Exception as e:
            print(f"❌ Health endpoint error: {e}")
            self.test_results.append(("Health endpoint (no auth)", False))
            return False
    
    def test_endpoint_auth(self, method: str, endpoint: str, data: Dict = None, files: Dict = None) -> Dict[str, bool]:
        """
        Test authentication for a specific endpoint
        
        Returns:
            Dict with test results for different auth scenarios
        """
        results = {}
        
        # Test 1: No API key
        print(f"  Testing {method} {endpoint} - No API key...")
        try:
            if method.upper() == 'GET':
                response = requests.get(f"{self.base_url}{endpoint}", timeout=10)
            elif method.upper() == 'POST':
                if files:
                    response = requests.post(f"{self.base_url}{endpoint}", data=data, files=files, timeout=30)
                else:
                    response = requests.post(f"{self.base_url}{endpoint}", json=data, timeout=30)
            
            # Should fail with 401
            success = response.status_code == 401
            if success:
                error_data = response.json()
                print(f"    ✅ Correctly rejected (401): {error_data.get('error', 'No error message')}")
            else:
                print(f"    ❌ Expected 401, got {response.status_code}")
            
            results['no_key'] = success
            
        except Exception as e:
            print(f"    ❌ Error testing no key: {e}")
            results['no_key'] = False
        
        # Test 2: Invalid API key
        print(f"  Testing {method} {endpoint} - Invalid API key...")
        try:
            headers = {"X-API-Key": "invalid_key_12345"}
            
            if method.upper() == 'GET':
                response = requests.get(f"{self.base_url}{endpoint}", headers=headers, timeout=10)
            elif method.upper() == 'POST':
                if files:
                    response = requests.post(f"{self.base_url}{endpoint}", headers=headers, data=data, files=files, timeout=30)
                else:
                    headers["Content-Type"] = "application/json"
                    response = requests.post(f"{self.base_url}{endpoint}", headers=headers, json=data, timeout=30)
            
            # Should fail with 403
            success = response.status_code == 403
            if success:
                error_data = response.json()
                print(f"    ✅ Correctly rejected (403): {error_data.get('error', 'No error message')}")
            else:
                print(f"    ❌ Expected 403, got {response.status_code}")
            
            results['invalid_key'] = success
            
        except Exception as e:
            print(f"    ❌ Error testing invalid key: {e}")
            results['invalid_key'] = False
        
        # Test 3: Valid API key
        print(f"  Testing {method} {endpoint} - Valid API key...")
        try:
            headers = {"X-API-Key": self.valid_api_key}
            
            if method.upper() == 'GET':
                response = requests.get(f"{self.base_url}{endpoint}", headers=headers, timeout=10)
            elif method.upper() == 'POST':
                if files:
                    response = requests.post(f"{self.base_url}{endpoint}", headers=headers, data=data, files=files, timeout=30)
                else:
                    headers["Content-Type"] = "application/json"
                    response = requests.post(f"{self.base_url}{endpoint}", headers=headers, json=data, timeout=30)
            
            # Should succeed (200, 201, etc.)
            success = 200 <= response.status_code < 300
            if success:
                print(f"    ✅ Correctly accepted ({response.status_code})")
            else:
                print(f"    ❌ Expected success, got {response.status_code}: {response.text[:100]}")
            
            results['valid_key'] = success
            
        except Exception as e:
            print(f"    ❌ Error testing valid key: {e}")
            results['valid_key'] = False
        
        return results
    
    def create_mock_audio_file(self):
        """Create mock audio file for testing"""
        from io import BytesIO
        # Simple WAV header + silent audio data
        wav_header = b'RIFF\x24\x08\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00\x44\xac\x00\x00\x88X\x01\x00\x02\x00\x10\x00data\x00\x08\x00\x00'
        mock_audio_data = b'\x00' * 1024
        return BytesIO(wav_header + mock_audio_data)
    
    def test_all_endpoints(self):
        """Test authentication for all protected endpoints"""
        print("\nTesting Authentication for All Protected Endpoints")
        print("=" * 60)
        
        # Define all protected endpoints to test
        endpoints_to_test = [
            {
                'method': 'GET',
                'endpoint': '/auth/info',
                'name': 'Auth Info'
            },
            {
                'method': 'POST',
                'endpoint': '/analyze-text',
                'name': 'Analyze Text',
                'data': {'text': 'Hello, this is a test message for fraud detection.'}
            },
            {
                'method': 'POST',
                'endpoint': '/analyze-audio',
                'name': 'Analyze Audio',
                'files': {'audio': ('test.wav', self.create_mock_audio_file(), 'audio/wav')}
            },
            {
                'method': 'GET',
                'endpoint': '/model-info',
                'name': 'Model Info'
            },
            {
                'method': 'POST',
                'endpoint': '/train',
                'name': 'Train Model',
                'data': {
                    'training_data': [
                        {'text': 'Test scam message', 'category': 'phishing'},
                        {'text': 'Test legitimate message', 'category': 'legitimate'}
                    ]
                }
            }
        ]
        
        all_passed = True
        
        for endpoint_config in endpoints_to_test:
            print(f"\nTesting {endpoint_config['name']} endpoint...")
            
            # Prepare test data
            data = endpoint_config.get('data')
            files = endpoint_config.get('files')
            
            # If files, recreate the BytesIO object for each test
            if files:
                files = {'audio': ('test.wav', self.create_mock_audio_file(), 'audio/wav')}
            
            # Test the endpoint
            results = self.test_endpoint_auth(
                endpoint_config['method'],
                endpoint_config['endpoint'],
                data=data,
                files=files
            )
            
            # Check if all tests passed
            endpoint_passed = all(results.values())
            if endpoint_passed:
                print(f"  ✅ {endpoint_config['name']} - All auth tests passed")
            else:
                print(f"  ❌ {endpoint_config['name']} - Some auth tests failed")
                all_passed = False
            
            # Store results
            self.test_results.append((f"{endpoint_config['name']} - No Key", results.get('no_key', False)))
            self.test_results.append((f"{endpoint_config['name']} - Invalid Key", results.get('invalid_key', False)))
            self.test_results.append((f"{endpoint_config['name']} - Valid Key", results.get('valid_key', False)))
        
        return all_passed
    
    def test_curl_examples(self):
        """Test curl command examples"""
        print("\nTesting cURL Command Examples")
        print("=" * 40)
        
        # Test health check (no auth)
        print("1. Health check (no authentication):")
        print(f"   curl -X GET {self.base_url}/health")
        
        # Test with valid API key
        print(f"\n2. Analyze text (with valid API key):")
        print(f"   curl -X POST {self.base_url}/analyze-text \\")
        print(f"     -H 'X-API-Key: {self.valid_api_key}' \\")
        print(f"     -H 'Content-Type: application/json' \\")
        print(f"     -d '{{\"text\": \"Hello, this is Microsoft support. Your computer has a virus.\"}}'")
        
        # Test auth info
        print(f"\n3. Authentication info:")
        print(f"   curl -X GET {self.base_url}/auth/info \\")
        print(f"     -H 'X-API-Key: {self.valid_api_key}'")
        
        # Test model info
        print(f"\n4. Model information:")
        print(f"   curl -X GET {self.base_url}/model-info \\")
        print(f"     -H 'X-API-Key: {self.valid_api_key}'")
        
        print(f"\n5. Example of failed authentication (invalid key):")
        print(f"   curl -X GET {self.base_url}/model-info \\")
        print(f"     -H 'X-API-Key: invalid_key'")
        print(f"   # Should return 403 Forbidden")
    
    def run_all_tests(self):
        """Run complete authentication test suite"""
        print("AI Fraud Detection API - Authentication Test Suite")
        print("=" * 60)
        
        # Test 1: Health endpoint (no auth required)
        health_ok = self.test_health_endpoint_no_auth()
        
        if not health_ok:
            print("\n❌ Health endpoint failed. Cannot continue with auth tests.")
            return False
        
        # Ensure we have a valid API key
        if not self.valid_api_key:
            self.valid_api_key = self.get_valid_api_key()
        
        print(f"\nUsing API key for tests: {self.valid_api_key}")
        
        # Test 2: All protected endpoints
        all_endpoints_ok = self.test_all_endpoints()
        
        # Test 3: Show curl examples
        self.test_curl_examples()
        
        # Summary
        print("\n" + "=" * 60)
        print("AUTHENTICATION TEST SUMMARY")
        print("=" * 60)
        
        passed_tests = sum(1 for _, result in self.test_results if result)
        total_tests = len(self.test_results)
        
        print(f"Total tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        
        if all_endpoints_ok and health_ok:
            print("\n✅ ALL AUTHENTICATION TESTS PASSED")
            print("\nThe API authentication is working correctly:")
            print("- Health endpoint accessible without authentication")
            print("- Protected endpoints reject requests without API key (401)")
            print("- Protected endpoints reject requests with invalid API key (403)")
            print("- Protected endpoints accept requests with valid API key (200)")
            return True
        else:
            print("\n❌ SOME AUTHENTICATION TESTS FAILED")
            print("\nPlease check the failed tests above and fix the authentication issues.")
            return False

def main():
    """Main test function"""
    try:
        tester = AuthTester()
        success = tester.run_all_tests()
        sys.exit(0 if success else 1)
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to API. Please make sure the server is running on localhost:8081")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error running authentication tests: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()