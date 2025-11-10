#!/usr/bin/env python3
"""
Simple test script for SHL Assessment Recommendation API
Run this after starting the server with: python main.py
"""

import requests
import json
import sys
from typing import Dict, Any

BASE_URL = "http://localhost:8000"

def print_section(title: str):
    """Print a formatted section header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def test_health_check() -> bool:
    """Test the health check endpoint"""
    print_section("1. Testing Health Check")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except requests.exceptions.RequestException as e:
        print(f"❌ Error: {e}")
        return False

def test_root_endpoint() -> bool:
    """Test the root endpoint"""
    print_section("2. Testing Root Endpoint")
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except requests.exceptions.RequestException as e:
        print(f"❌ Error: {e}")
        return False

def test_recommendations(query: str = "Java developer with problem-solving skills") -> bool:
    """Test the recommendations endpoint"""
    print_section("3. Testing Recommendations Endpoint")
    print(f"Query: '{query}'")
    try:
        response = requests.post(
            f"{BASE_URL}/recommend",
            json={"query": query},
            timeout=30
        )
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            recommendations = data.get('recommended_assessments', [])
            print(f"\n✅ Found {len(recommendations)} recommendations")
            
            # Display first 3 recommendations
            for i, assessment in enumerate(recommendations[:3], 1):
                print(f"\n  Recommendation {i}:")
                print(f"    Name: {assessment.get('name', 'N/A')}")
                print(f"    Duration: {assessment.get('duration', 'N/A')} minutes")
                print(f"    Test Type: {', '.join(assessment.get('test_type', []))}")
                print(f"    Remote Support: {assessment.get('remote_support', 'N/A')}")
            
            if len(recommendations) > 3:
                print(f"\n  ... and {len(recommendations) - 3} more recommendations")
            
            return True
        else:
            print(f"❌ Error: {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Error: {e}")
        return False

def test_list_assessments(limit: int = 5) -> bool:
    """Test the list assessments endpoint"""
    print_section("4. Testing List Assessments Endpoint")
    try:
        response = requests.get(f"{BASE_URL}/assessments?limit={limit}", timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            total = data.get('total', 0)
            assessments = data.get('assessments', [])
            print(f"\n✅ Total assessments available: {total}")
            print(f"Showing: {len(assessments)} assessments")
            
            for i, assessment in enumerate(assessments[:3], 1):
                print(f"\n  Assessment {i}: {assessment.get('name', 'N/A')}")
            
            return True
        else:
            print(f"❌ Error: {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Error: {e}")
        return False

def test_query_analysis(query: str = "technical skills assessment") -> bool:
    """Test the query analysis endpoint"""
    print_section("5. Testing Query Analysis Endpoint")
    print(f"Query: '{query}'")
    try:
        response = requests.get(
            f"{BASE_URL}/analyze",
            params={"query": query},
            timeout=10
        )
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except requests.exceptions.RequestException as e:
        print(f"❌ Error: {e}")
        return False

def test_error_handling() -> bool:
    """Test error handling with invalid input"""
    print_section("6. Testing Error Handling")
    print("Testing with invalid query (too short)...")
    try:
        response = requests.post(
            f"{BASE_URL}/recommend",
            json={"query": "ab"},  # Too short
            timeout=10
        )
        print(f"Status Code: {response.status_code}")
        
        # FastAPI returns 422 (Unprocessable Entity) for Pydantic validation errors
        # This is the correct HTTP status code for validation failures
        if response.status_code in [400, 422]:
            print("✅ Correctly rejected invalid query")
            error_data = response.json()
            print(f"Error response: {json.dumps(error_data, indent=2)}")
            return True
        else:
            print(f"⚠️  Unexpected status code: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("  SHL Assessment Recommendation API - Test Suite")
    print("="*60)
    print(f"\nTesting API at: {BASE_URL}")
    print("Make sure the server is running: python main.py\n")
    
    # Check if server is reachable
    try:
        requests.get(f"{BASE_URL}/health", timeout=2)
    except requests.exceptions.RequestException:
        print("❌ ERROR: Cannot connect to the API server!")
        print("   Please start the server first: python main.py")
        sys.exit(1)
    
    results = []
    
    # Run all tests
    results.append(("Health Check", test_health_check()))
    results.append(("Root Endpoint", test_root_endpoint()))
    results.append(("Recommendations", test_recommendations()))
    results.append(("List Assessments", test_list_assessments()))
    results.append(("Query Analysis", test_query_analysis()))
    results.append(("Error Handling", test_error_handling()))
    
    # Summary
    print_section("Test Summary")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status}: {test_name}")
    
    print(f"\n{'='*60}")
    print(f"  Results: {passed}/{total} tests passed")
    print(f"{'='*60}\n")
    
    if passed == total:
        print("🎉 All tests passed!")
        sys.exit(0)
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        sys.exit(1)

if __name__ == "__main__":
    main()

