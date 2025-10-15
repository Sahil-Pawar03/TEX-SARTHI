#!/usr/bin/env python3
"""
Simple API test script for TEX-SARTHI Backend
Run this to test basic API functionality
"""

import requests
import json
import sys

BASE_URL = "http://localhost:3000/api"

def test_health():
    """Test health endpoint"""
    print("Testing health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Health check passed")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Make sure the server is running.")
        return False

def test_login():
    """Test login endpoint"""
    print("Testing login endpoint...")
    try:
        login_data = {
            "email": "admin@texsarthi.com",
            "password": "admin123"
        }
        response = requests.post(f"{BASE_URL}/login", json=login_data)
        if response.status_code == 200:
            data = response.json()
            if 'token' in data:
                print("✅ Login successful")
                return data['token']
            else:
                print("❌ Login failed: No token received")
                return None
        else:
            print(f"❌ Login failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Login test failed: {e}")
        return None

def test_dashboard(token):
    """Test dashboard endpoint"""
    print("Testing dashboard endpoint...")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/dashboard/stats", headers=headers)
        if response.status_code == 200:
            print("✅ Dashboard stats retrieved")
            return True
        else:
            print(f"❌ Dashboard test failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Dashboard test failed: {e}")
        return False

def test_customers(token):
    """Test customers endpoint"""
    print("Testing customers endpoint...")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/customers", headers=headers)
        if response.status_code == 200:
            print("✅ Customers endpoint working")
            return True
        else:
            print(f"❌ Customers test failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Customers test failed: {e}")
        return False

def test_orders(token):
    """Test orders endpoint"""
    print("Testing orders endpoint...")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/orders", headers=headers)
        if response.status_code == 200:
            print("✅ Orders endpoint working")
            return True
        else:
            print(f"❌ Orders test failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Orders test failed: {e}")
        return False

def test_inventory(token):
    """Test inventory endpoint"""
    print("Testing inventory endpoint...")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/inventory", headers=headers)
        if response.status_code == 200:
            print("✅ Inventory endpoint working")
            return True
        else:
            print(f"❌ Inventory test failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Inventory test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 50)
    print("TEX-SARTHI Backend API Test")
    print("=" * 50)
    
    # Test health
    if not test_health():
        print("\n❌ Server is not running. Please start the server first.")
        sys.exit(1)
    
    # Test login
    token = test_login()
    if not token:
        print("\n❌ Login failed. Cannot continue with other tests.")
        sys.exit(1)
    
    # Test other endpoints
    tests = [
        test_dashboard,
        test_customers,
        test_orders,
        test_inventory
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test(token):
            passed += 1
        print()
    
    print("=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")
    if passed == total:
        print("🎉 All tests passed! API is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the server logs.")
    print("=" * 50)

if __name__ == "__main__":
    main()
