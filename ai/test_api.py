#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Vietnamese Teacher AI Service
"""

import requests
import json

def test_ai_service():
    print("🧪 Testing Vietnamese Teacher AI Service")
    base_url = "http://localhost:5003"
    
    # Test health endpoint
    print("\n1. Testing /health endpoint...")
    try:
        response = requests.get(f"{base_url}/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test model info endpoint
    print("\n2. Testing /model-info endpoint...")
    try:
        response = requests.get(f"{base_url}/model-info")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test chat endpoint
    print("\n3. Testing /chat endpoint...")
    test_questions = [
        "Xin chào cô!",
        "6 thanh điệu là những thanh nào ạ?", 
        "Em muốn học phát âm",
        "Cảm ơn cô!"
    ]
    
    for question in test_questions:
        print(f"\n📝 Câu hỏi: {question}")
        try:
            response = requests.post(
                f"{base_url}/chat",
                json={"message": question},
                headers={"Content-Type": "application/json"}
            )
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"🤖 AI: {result['response']}")
            else:
                print(f"Error: {response.text}")
                
        except Exception as e:
            print(f"Error: {e}")
        
        print("-" * 50)

if __name__ == '__main__':
    test_ai_service()