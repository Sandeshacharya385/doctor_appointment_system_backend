#!/usr/bin/env python
"""
Quick test script to verify login functionality
"""
import requests
import json

BASE_URL = 'http://127.0.0.1:8000/api'

def test_login():
    print("=" * 50)
    print("Testing Login Functionality")
    print("=" * 50)
    
    # Test credentials
    credentials = {
        'username': 'drsmith',
        'password': 'doctor123'
    }
    
    print(f"\n1. Testing login with credentials:")
    print(f"   Username: {credentials['username']}")
    print(f"   Password: {credentials['password']}")
    
    try:
        # Attempt login
        response = requests.post(
            f'{BASE_URL}/auth/login/',
            json=credentials,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"\n2. Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("   ✅ Login successful!")
            print(f"   Access token: {data.get('access', 'N/A')[:50]}...")
            print(f"   Refresh token: {data.get('refresh', 'N/A')[:50]}...")
            
            # Test profile endpoint
            print("\n3. Testing profile endpoint...")
            access_token = data.get('access')
            profile_response = requests.get(
                f'{BASE_URL}/auth/profile/',
                headers={'Authorization': f'Bearer {access_token}'}
            )
            
            if profile_response.status_code == 200:
                profile = profile_response.json()
                print("   ✅ Profile fetched successfully!")
                print(f"   Username: {profile.get('username')}")
                print(f"   Name: {profile.get('first_name')} {profile.get('last_name')}")
                print(f"   Role: {profile.get('role')}")
                print(f"   Email: {profile.get('email')}")
            else:
                print(f"   ❌ Profile fetch failed: {profile_response.status_code}")
                print(f"   Response: {profile_response.text}")
        else:
            print(f"   ❌ Login failed!")
            print(f"   Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Cannot connect to backend server!")
        print("   Make sure Django is running at http://127.0.0.1:8000")
        print("   Run: python manage.py runserver")
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
    
    print("\n" + "=" * 50)

if __name__ == '__main__':
    test_login()
