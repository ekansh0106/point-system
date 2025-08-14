#!/usr/bin/env python3
"""
Simple script to test the Flask API endpoints
Run this while your Flask app is running on localhost:5000
"""

import requests
import json

BASE_URL = "http://localhost:5000"


def test_api():
    print("🧪 Testing Flask API Endpoints")
    print("=" * 50)

    # Test 1: Register a new parent
    print("\n1. Testing Parent Registration...")
    register_data = {
        "username": "testparent_api",
        "email": "testparent_api@example.com",
        "password": "password123",
        "role": "parent",
    }

    try:
        response = requests.post(f"{BASE_URL}/auth/api/register", json=register_data)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")

    # Test 2: Login with the parent
    print("\n2. Testing Parent Login...")
    login_data = {"email": "testparent_api@example.com", "password": "password123"}

    session = requests.Session()  # Use session to maintain cookies

    try:
        response = session.post(f"{BASE_URL}/auth/api/login", json=login_data)
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Response: {result}")

        if result.get("success"):
            print("✅ Login successful!")

            # Test 3: Get current user info
            print("\n3. Testing Get Current User...")
            response = session.get(f"{BASE_URL}/auth/api/me")
            print(f"Status: {response.status_code}")
            print(f"Response: {response.json()}")

            # Test 4: Get parent dashboard
            print("\n4. Testing Parent Dashboard...")
            response = session.get(f"{BASE_URL}/parent/api/dashboard")
            print(f"Status: {response.status_code}")
            print(f"Response: {response.json()}")

            # Test 5: Register a child (need parent code first)
            user_response = session.get(f"{BASE_URL}/auth/api/me")
            if user_response.status_code == 200:
                user_data = user_response.json()
                parent_code = user_data.get("user", {}).get("parent_code")

                if parent_code:
                    print(
                        f"\n5. Testing Child Registration with parent code: "
                        f"{parent_code}"
                    )
                    child_data = {
                        "username": "testchild_api",
                        "email": "testchild_api@example.com",
                        "password": "password123",
                        "role": "child",
                        "parent_code": parent_code,
                    }

                    response = requests.post(
                        f"{BASE_URL}/auth/api/register", json=child_data
                    )
                    print(f"Status: {response.status_code}")
                    print(f"Response: {response.json()}")

            # Test 6: Logout
            print("\n6. Testing Logout...")
            response = session.post(f"{BASE_URL}/auth/api/logout")
            print(f"Status: {response.status_code}")
            print(f"Response: {response.json()}")

        else:
            print("❌ Login failed!")

    except Exception as e:
        print(f"Error: {e}")

    print("\n" + "=" * 50)
    print("🎉 API Testing Complete!")
    print("\nTo test manually with curl:")
    print(
        f"curl -X POST {BASE_URL}/auth/api/login "
        f"-H 'Content-Type: application/json' "
        f"-d '{json.dumps(login_data)}'"
    )


if __name__ == "__main__":
    test_api()
