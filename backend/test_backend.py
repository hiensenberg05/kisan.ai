#!/usr/bin/env python3
"""
Simple test script to verify backend endpoints are working
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health check endpoint"""
    print("🔍 Testing health check...")
    try:
        response = requests.get(f"{BASE_URL}/api/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check passed: {data.get('data', {}).get('status', 'unknown')}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_chat():
    """Test text chat endpoint"""
    print("\n💬 Testing text chat...")
    try:
        payload = {"query": "What is the best crop for Karnataka?"}
        response = requests.post(f"{BASE_URL}/api/chat/text", json=payload, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✅ Chat endpoint working")
                print(f"📝 Response: {data.get('data', {}).get('response', '')[:100]}...")
                return True
            else:
                print(f"❌ Chat failed: {data.get('error', 'Unknown error')}")
                return False
        else:
            print(f"❌ Chat failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Chat error: {e}")
        return False

def test_market():
    """Test market prices endpoint"""
    print("\n💰 Testing market prices...")
    try:
        payload = {"crop": "tomato", "location": "karnataka"}
        response = requests.post(f"{BASE_URL}/api/market/prices", json=payload, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✅ Market prices endpoint working")
                return True
            else:
                print(f"❌ Market prices failed: {data.get('error', 'Unknown error')}")
                return False
        else:
            print(f"❌ Market prices failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Market prices error: {e}")
        return False

def test_policies():
    """Test policies search endpoint"""
    print("\n📋 Testing policies search...")
    try:
        payload = {"query": "farmer subsidy schemes"}
        response = requests.post(f"{BASE_URL}/api/policies/search", json=payload, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✅ Policies search endpoint working")
                return True
            else:
                print(f"❌ Policies search failed: {data.get('error', 'Unknown error')}")
                return False
        else:
            print(f"❌ Policies search failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Policies search error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting backend tests...")
    print(f"📍 Testing against: {BASE_URL}")
    print("=" * 50)
    
    tests = [
        test_health,
        test_chat,
        test_market,
        test_policies
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        time.sleep(1)  # Small delay between tests
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Backend is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the backend logs for issues.")
    
    return passed == total

if __name__ == "__main__":
    main() 