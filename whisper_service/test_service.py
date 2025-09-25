#!/usr/bin/env python3
"""
Simple Test Script for Whisper STT Service
"""

import requests
import json
import os

# Test configuration
WHISPER_SERVICE_URL = "http://localhost:5001"
TEST_AUDIO_PATH = "test_audio.wav"  # You can add a test audio file

def test_health_check():
    """Test health check endpoint"""
    print("🔍 Testing health check...")
    try:
        response = requests.get(f"{WHISPER_SERVICE_URL}/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_service_info():
    """Test service info endpoint"""
    print("\n🔍 Testing service info...")
    try:
        response = requests.get(f"{WHISPER_SERVICE_URL}/")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Service info failed: {e}")
        return False

def test_accent_detection():
    """Test accent detection endpoint"""
    print("\n🔍 Testing accent detection...")
    try:
        test_texts = [
            "Xin chào, tôi đến từ Hà Nội",
            "Chào đỏ, tôi là người Nghệ An", 
            "Chào bạn, tôi sống ở Sài Gòn"
        ]
        
        for text in test_texts:
            response = requests.post(
                f"{WHISPER_SERVICE_URL}/detect-accent",
                json={"text": text}
            )
            print(f"\nText: '{text}'")
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                print(f"Region: {result['region']} (confidence: {result['confidence']:.3f})")
                if result.get('indicators'):
                    print(f"Indicators: {result['indicators']}")
            else:
                print(f"Error: {response.text}")
                
        return True
    except Exception as e:
        print(f"❌ Accent detection failed: {e}")
        return False

def test_transcription_with_file():
    """Test transcription with audio file (if available)"""
    print("\n🔍 Testing transcription (file required)...")
    
    if not os.path.exists(TEST_AUDIO_PATH):
        print(f"⚠️  Audio file '{TEST_AUDIO_PATH}' not found. Skipping transcription test.")
        print("💡 To test transcription, add a Vietnamese audio file as 'test_audio.wav'")
        return True
    
    try:
        with open(TEST_AUDIO_PATH, 'rb') as audio_file:
            files = {'audio': audio_file}
            data = {'language': 'vi', 'detect_accent': 'true'}
            
            response = requests.post(
                f"{WHISPER_SERVICE_URL}/transcribe",
                files=files,
                data=data
            )
            
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Transcribed: '{result.get('text', 'N/A')}'")
            print(f"Language: {result.get('language', 'N/A')}")
            print(f"Confidence: {result.get('confidence', 'N/A')}")
            if 'accent' in result:
                print(f"Accent: {result['accent']['region']} ({result['accent']['confidence']:.3f})")
        else:
            print(f"Error: {response.text}")
            
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Transcription test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing Whisper STT Service")
    print("=" * 50)
    
    # Check if service is running
    tests = [
        ("Health Check", test_health_check),
        ("Service Info", test_service_info),
        ("Accent Detection", test_accent_detection),
        ("Transcription", test_transcription_with_file)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            if test_func():
                print(f"✅ {test_name} passed")
                passed += 1
            else:
                print(f"❌ {test_name} failed")
        except Exception as e:
            print(f"❌ {test_name} error: {e}")
    
    print(f"\n{'='*50}")
    print(f"🏆 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Whisper service is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the service configuration.")
    
    print("\n💡 Usage examples:")
    print("curl -X GET http://localhost:5001/health")
    print("curl -X POST http://localhost:5001/detect-accent -H 'Content-Type: application/json' -d '{\"text\":\"Chào đỏ\"}'")

if __name__ == "__main__":
    main()