#!/usr/bin/env python3
"""
Sample API requests for AI Fraud Detection API
"""

import requests
import json

# Configuration
API_BASE_URL = "http://localhost:8081/api/v1"

def get_api_key():
    """Get the valid API key from the health endpoint"""
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            return data.get('authentication', {}).get('demo_key', 'fraud_detection_api_key_2026')
        else:
            return 'fraud_detection_api_key_2026'
    except:
        return 'fraud_detection_api_key_2026'

def analyze_scam_examples():
    """Analyze various scam examples"""
    
    API_KEY = get_api_key()
    
    scam_examples = [
        {
            "name": "Tech Support Scam",
            "text": "Hello, this is Microsoft technical support. We have detected a virus on your computer. Please give me remote access to fix it immediately. I need your credit card to verify your identity.",
            "expected_category": "tech_support"
        },
        {
            "name": "IRS Robocall Scam",
            "text": "This is the IRS. You owe $5,000 in back taxes. If you don't pay immediately, we will issue a warrant for your arrest. Press 1 to speak with an agent now.",
            "expected_category": "robocall"
        },
        {
            "name": "Bank Phishing Scam",
            "text": "Your bank account has been suspended due to suspicious activity. Please call us immediately at 1-800-FAKE-BANK and provide your account number and PIN to reactivate.",
            "expected_category": "financial"
        },
        {
            "name": "Lottery Prize Scam",
            "text": "Congratulations! You have won $50,000 in the Microsoft lottery! To claim your prize, please send $500 for processing fees to our office in Nigeria.",
            "expected_category": "lottery_prize"
        },
        {
            "name": "Romance Scam",
            "text": "My dearest love, I am stuck in Ghana and need $2,000 for my plane ticket home. Please send money via Western Union so we can finally meet in person.",
            "expected_category": "romance"
        }
    ]
    
    print("Analyzing Scam Examples")
    print("=" * 50)
    
    for example in scam_examples:
        print(f"\nAnalyzing: {example['name']}")
        print(f"Text: {example['text'][:100]}...")
        
        response = requests.post(
            f"{API_BASE_URL}/analyze-text",
            headers={
                "X-API-Key": API_KEY,
                "Content-Type": "application/json"
            },
            json={"text": example["text"]}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✓ Is Fraud: {result['is_fraud']}")
            print(f"✓ Risk Score: {result['risk_score']}/100")
            print(f"✓ Predicted Category: {result['predicted_category']}")
            print(f"✓ Expected Category: {example['expected_category']}")
            print(f"✓ Confidence: {result['confidence']:.2f}")
            print(f"✓ Explanations: {', '.join(result['explanations'][:2])}")
            
            # Check if prediction matches expectation
            if result['predicted_category'] == example['expected_category']:
                print("✅ Prediction matches expected category")
            else:
                print("⚠️  Prediction differs from expected category")
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
        
        print("-" * 30)

def analyze_legitimate_examples():
    """Analyze legitimate call examples"""
    
    API_KEY = get_api_key()
    
    legitimate_examples = [
        {
            "name": "Doctor Appointment Reminder",
            "text": "Hello, this is Dr. Smith's office calling to confirm your appointment tomorrow at 2 PM. Please call us back if you need to reschedule."
        },
        {
            "name": "Pharmacy Notification",
            "text": "Hi, this is CVS Pharmacy. Your prescription is ready for pickup. We're open until 9 PM today."
        },
        {
            "name": "Job Interview Follow-up",
            "text": "Hi, this is Sarah from ABC Company. I'm calling to follow up on your job application. Could you please call me back at your convenience?"
        },
        {
            "name": "School Nurse Call",
            "text": "Hello, this is the school nurse. Your child has a mild fever and should be picked up from school. Please call us back when you receive this message."
        },
        {
            "name": "Restaurant Reservation",
            "text": "Hello, this is Mario's Restaurant calling to confirm your reservation for tonight at 7 PM. We look forward to seeing you."
        }
    ]
    
    print("\nAnalyzing Legitimate Examples")
    print("=" * 50)
    
    for example in legitimate_examples:
        print(f"\nAnalyzing: {example['name']}")
        print(f"Text: {example['text'][:100]}...")
        
        response = requests.post(
            f"{API_BASE_URL}/analyze-text",
            headers={
                "X-API-Key": API_KEY,
                "Content-Type": "application/json"
            },
            json={"text": example["text"]}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✓ Is Fraud: {result['is_fraud']}")
            print(f"✓ Risk Score: {result['risk_score']}/100")
            print(f"✓ Predicted Category: {result['predicted_category']}")
            print(f"✓ Confidence: {result['confidence']:.2f}")
            
            if not result['is_fraud'] and result['predicted_category'] == 'legitimate':
                print("✅ Correctly identified as legitimate")
            else:
                print("⚠️  Incorrectly flagged as fraud")
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
        
        print("-" * 30)

def analyze_multilingual_examples():
    """Analyze multilingual examples"""
    
    API_KEY = get_api_key()
    
    multilingual_examples = [
        {
            "name": "Hindi Financial Scam",
            "text": "नमस्ते, मैं बैंक से कॉल कर रहा हूं। आपके खाते में संदिग्ध गतिविधि है। कृपया तुरंत अपना पिन नंबर और क्रेडिट कार्ड की जानकारी बताएं।",
            "language": "Hindi"
        },
        {
            "name": "Telugu Lottery Scam",
            "text": "అభినందనలు! మీరు లాటరీలో 50,000 రూపాయలు గెలిచారు। బహుమతి పొందడానికి దయచేసి 500 రూపాయలు రుసుము పంపండి।",
            "language": "Telugu"
        },
        {
            "name": "Hindi Legitimate Call",
            "text": "नमस्ते, मैं डॉक्टर शर्मा के क्लिनिक से कॉल कर रहा हूं। आपका अपॉइंटमेंट कल दोपहर 2 बजे है। कृपया समय पर आएं।",
            "language": "Hindi"
        },
        {
            "name": "Telugu Legitimate Call",
            "text": "నమస్కారం, నేను ABC కంపెనీ నుండి కాల్ చేస్తున్నాను. మీ ఉద్యోగ దరఖాస్తు గురించి మాట్లాడాలని ఉంది। దయచేసి మాకు తిరిగి కాల్ చేయండి.",
            "language": "Telugu"
        },
        {
            "name": "Mixed Language Scam",
            "text": "Hello, मैं Microsoft से कॉल कर रहा हूं। Your computer has virus. Please give me your credit card details तुरंत।",
            "language": "Mixed (English/Hindi)"
        }
    ]
    
    print("\nAnalyzing Multilingual Examples")
    print("=" * 50)
    
    for example in multilingual_examples:
        print(f"\nAnalyzing: {example['name']} ({example['language']})")
        print(f"Text: {example['text'][:100]}...")
        
        response = requests.post(
            f"{API_BASE_URL}/analyze-text",
            headers={
                "X-API-Key": API_KEY,
                "Content-Type": "application/json"
            },
            json={"text": example["text"]}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✓ Is Fraud: {result['is_fraud']}")
            print(f"✓ Risk Score: {result['risk_score']}/100")
            print(f"✓ Predicted Category: {result['predicted_category']}")
            print(f"✓ Language Detected: {result['language_detected']}")
            print(f"✓ Confidence: {result['confidence']:.2f}")
            print(f"✓ Key Explanations: {', '.join(result['explanations'][:2])}")
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
        
        print("-" * 30)

def main():
    """Run all example analyses"""
    print("AI Fraud Detection API - Sample Analysis")
    print("=" * 60)
    
    # Get API key
    API_KEY = get_api_key()
    print(f"Using API Key: {API_KEY}")
    
    try:
        # Check API health first
        health_response = requests.get(f"{API_BASE_URL}/health")
        if health_response.status_code != 200:
            print("❌ API is not healthy. Please start the server first.")
            return
        
        print("✅ API is healthy. Running sample analyses...\n")
        
        analyze_scam_examples()
        analyze_legitimate_examples()
        analyze_multilingual_examples()
        
        print("\n" + "=" * 60)
        print("Sample analysis completed!")
        print("Check the results above to see how the API performs on different types of calls.")
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to API. Please make sure the server is running on localhost:8081")
    except Exception as e:
        print(f"❌ Error running samples: {e}")

if __name__ == "__main__":
    main()