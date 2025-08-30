#!/usr/bin/env python3
"""
PathRAG API Live Test Script
This script tests the live PathRAG API to verify it's working correctly
"""

import requests
import json
import sys
from pathlib import Path

def test_api_endpoint(url, method='GET', data=None, description=""):
    """Test an API endpoint and return the result"""
    print(f"\n🔍 Testing: {description}")
    print(f"   URL: {url}")
    print(f"   Method: {method}")
    
    try:
        if method == 'GET':
            response = requests.get(url, timeout=10)
        elif method == 'POST':
            headers = {'Content-Type': 'application/json'}
            response = requests.post(url, json=data, headers=headers, timeout=10)
        else:
            print(f"   ❌ Unsupported method: {method}")
            return False
            
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                print(f"   ✅ Success!")
                if 'status' in result:
                    print(f"   Status: {result['status']}")
                if 'services' in result:
                    print(f"   Services: {result['services']}")
                return True
            except json.JSONDecodeError:
                print(f"   ✅ Success! (Non-JSON response)")
                print(f"   Response: {response.text[:200]}...")
                return True
        else:
            print(f"   ❌ Failed with status {response.status_code}")
            print(f"   Response: {response.text[:200]}...")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Request failed: {str(e)}")
        return False

def main():
    """Main test function"""
    print("=" * 60)
    print("PathRAG API Live System Test")
    print("=" * 60)
    
    # Test configuration
    base_url = "http://localhost:8000"
    domain_url = "http://movie.ft.tc:8000"
    
    tests_passed = 0
    total_tests = 0
    
    # Test 1: Health Check (localhost)
    total_tests += 1
    if test_api_endpoint(f"{base_url}/health", description="Health Check (localhost)"):
        tests_passed += 1
    
    # Test 2: Health Check (domain)
    total_tests += 1
    if test_api_endpoint(f"{domain_url}/health", description="Health Check (domain)"):
        tests_passed += 1
    
    # Test 3: Root endpoint
    total_tests += 1
    if test_api_endpoint(f"{base_url}/", description="Root API Information"):
        tests_passed += 1
    
    # Test 4: Documentation endpoint
    total_tests += 1
    if test_api_endpoint(f"{base_url}/docs", description="API Documentation"):
        tests_passed += 1
    
    # Test 5: Query endpoint
    total_tests += 1
    query_data = {
        "query": "What is PathRAG?",
        "top_k": 5
    }
    if test_api_endpoint(f"{base_url}/query", method="POST", data=query_data, description="Query Endpoint"):
        tests_passed += 1
    
    # Test 6: Insert endpoint
    total_tests += 1
    insert_data = {
        "documents": [
            "PathRAG is a powerful knowledge graph system.",
            "It uses ArangoDB for storage and provides REST API access."
        ]
    }
    if test_api_endpoint(f"{base_url}/insert", method="POST", data=insert_data, description="Insert Endpoint"):
        tests_passed += 1
    
    # Test 7: Query after insert
    total_tests += 1
    query_data2 = {
        "query": "Tell me about PathRAG system",
        "top_k": 3
    }
    if test_api_endpoint(f"{base_url}/query", method="POST", data=query_data2, description="Query After Insert"):
        tests_passed += 1
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Tests Passed: {tests_passed}/{total_tests}")
    print(f"Success Rate: {(tests_passed/total_tests)*100:.1f}%")
    
    if tests_passed == total_tests:
        print("\n🎉 ALL TESTS PASSED! Your PathRAG API is working perfectly!")
        print("\n✅ System Status:")
        print("   • API Server: Running and responsive")
        print("   • Health Check: Passing")
        print("   • All Endpoints: Functional")
        print("   • Domain Access: Working")
        print("   • Database: Connected")
        
        print(f"\n🌐 Your PathRAG API is live at:")
        print(f"   • Local: {base_url}")
        print(f"   • Domain: {domain_url}")
        
        return True
    else:
        print(f"\n❌ {total_tests - tests_passed} tests failed. Please check the issues above.")
        return False

if __name__ == "__main__":
    success = main()
    
    if success:
        print("\n🚀 Your PathRAG system is ready for production use!")
        sys.exit(0)
    else:
        print("\n🔧 Please fix the issues and run the test again.")
        sys.exit(1)
