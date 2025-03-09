import requests
import time
import json

def test_server():
    """Test all endpoints of the tracking server"""
    base_url = "https://rsc00cwwwckcw8g44kgk0k0s.develdeep.com"
    
    print("\n🔍 Testing Tracking Server")
    print("=" * 50)
    
    # Test root endpoint
    try:
        print("\n1. Testing root endpoint (/)")
        response = requests.get(base_url)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test health endpoint
    try:
        print("\n2. Testing health endpoint (/health)")
        response = requests.get(f"{base_url}/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test tracking endpoint
    try:
        print("\n3. Testing tracking endpoint (/track/open)")
        response = requests.get(
            f"{base_url}/track/open",
            params={
                "uid": "test123",
                "m": "test@email.com",
                "t": str(int(time.time()))
            },
            stream=True  # Handle binary response properly
        )
        print(f"Status: {response.status_code}")
        print(f"Content-Type: {response.headers.get('content-type')}")
        if response.status_code == 200:
            print("✅ Tracking pixel received successfully")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_server() 