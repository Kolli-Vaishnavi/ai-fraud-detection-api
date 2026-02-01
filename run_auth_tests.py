#!/usr/bin/env python3
"""
Comprehensive Authentication Test Runner
Runs all authentication-related tests and validations
"""

import subprocess
import sys
import time
import requests
import os
from multiprocessing import Process

def start_api_server():
    """Start the API server in a separate process"""
    def run_server():
        os.system("python app.py > server.log 2>&1")
    
    server_process = Process(target=run_server)
    server_process.start()
    return server_process

def wait_for_server(max_wait=30):
    """Wait for the server to be ready"""
    print("Waiting for server to start...")
    
    for i in range(max_wait):
        try:
            response = requests.get("http://localhost:8081/api/v1/health", timeout=2)
            if response.status_code == 200:
                print(f"✅ Server is ready after {i+1} seconds")
                return True
        except:
            pass
        
        time.sleep(1)
        print(f"   Waiting... ({i+1}/{max_wait})")
    
    print("❌ Server failed to start within timeout")
    return False

def run_test_script(script_name, description):
    """Run a test script and return success status"""
    print(f"\n{'='*60}")
    print(f"Running {description}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run([sys.executable, script_name], 
                              capture_output=True, text=True, timeout=60)
        
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        
        success = result.returncode == 0
        if success:
            print(f"✅ {description} PASSED")
        else:
            print(f"❌ {description} FAILED (exit code: {result.returncode})")
        
        return success
        
    except subprocess.TimeoutExpired:
        print(f"❌ {description} TIMED OUT")
        return False
    except Exception as e:
        print(f"❌ {description} ERROR: {e}")
        return False

def main():
    """Main test runner"""
    print("AI Fraud Detection API - Comprehensive Authentication Test Suite")
    print("=" * 70)
    
    # Check if server is already running
    server_running = False
    try:
        response = requests.get("http://localhost:8081/api/v1/health", timeout=2)
        if response.status_code == 200:
            print("✅ Server is already running")
            server_running = True
    except:
        print("Server is not running, will start it...")
    
    server_process = None
    
    try:
        # Start server if not running
        if not server_running:
            print("Starting API server...")
            server_process = start_api_server()
            
            if not wait_for_server():
                print("❌ Failed to start server")
                return False
        
        # Run all authentication tests
        test_results = []
        
        # Test 1: Basic authentication validation
        success = run_test_script("validate_auth.py", "Basic Authentication Validation")
        test_results.append(("Basic Auth Validation", success))
        
        # Test 2: Comprehensive authentication test suite
        success = run_test_script("test_auth.py", "Comprehensive Authentication Test Suite")
        test_results.append(("Comprehensive Auth Tests", success))
        
        # Test 3: General API tests (should work with new auth)
        success = run_test_script("test_api.py", "General API Tests")
        test_results.append(("General API Tests", success))
        
        # Test 4: Sample requests (should work with new auth)
        print(f"\n{'='*60}")
        print("Running Sample Requests Test")
        print(f"{'='*60}")
        
        try:
            # Run just a quick sample test
            result = subprocess.run([sys.executable, "-c", """
import requests
import sys

API_BASE_URL = "http://localhost:8081/api/v1"

# Get API key
try:
    response = requests.get(f"{API_BASE_URL}/health")
    api_key = response.json().get('authentication', {}).get('demo_key', 'fraud_detection_api_key_2026')
    print(f"Using API key: {api_key}")
    
    # Test analyze-text endpoint
    response = requests.post(
        f"{API_BASE_URL}/analyze-text",
        headers={"X-API-Key": api_key, "Content-Type": "application/json"},
        json={"text": "Hello, this is Microsoft support. Your computer has a virus."}
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Sample request successful")
        print(f"   Is fraud: {result.get('is_fraud')}")
        print(f"   Risk score: {result.get('risk_score')}")
        sys.exit(0)
    else:
        print(f"❌ Sample request failed: {response.status_code}")
        sys.exit(1)
        
except Exception as e:
    print(f"❌ Sample request error: {e}")
    sys.exit(1)
"""], capture_output=True, text=True, timeout=30)
            
            print(result.stdout)
            if result.stderr:
                print("STDERR:", result.stderr)
            
            success = result.returncode == 0
            if success:
                print("✅ Sample Requests Test PASSED")
            else:
                print("❌ Sample Requests Test FAILED")
            
            test_results.append(("Sample Requests", success))
            
        except Exception as e:
            print(f"❌ Sample Requests Test ERROR: {e}")
            test_results.append(("Sample Requests", False))
        
        # Summary
        print(f"\n{'='*70}")
        print("FINAL TEST SUMMARY")
        print(f"{'='*70}")
        
        total_tests = len(test_results)
        passed_tests = sum(1 for _, success in test_results if success)
        
        for test_name, success in test_results:
            status = "✅ PASSED" if success else "❌ FAILED"
            print(f"{test_name:.<50} {status}")
        
        print(f"\nTotal Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        
        if passed_tests == total_tests:
            print(f"\n🎉 ALL AUTHENTICATION TESTS PASSED!")
            print("\nThe API authentication system is working correctly:")
            print("✅ Consistent API key across all endpoints")
            print("✅ Proper rejection of invalid/missing keys")
            print("✅ Health endpoint accessible without auth")
            print("✅ All protected endpoints require valid auth")
            print("✅ Environment variable support working")
            print("✅ Error messages are clear and helpful")
            return True
        else:
            print(f"\n❌ SOME TESTS FAILED")
            print("Please review the failed tests above and fix any issues.")
            return False
    
    finally:
        # Clean up server process if we started it
        if server_process:
            print("\nStopping server...")
            server_process.terminate()
            server_process.join(timeout=5)
            if server_process.is_alive():
                server_process.kill()

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        sys.exit(1)