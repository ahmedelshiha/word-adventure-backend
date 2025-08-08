import requests

# Test the API endpoints manually
backend_url = "https://web-production-e17b.up.railway.app"

print("Testing Word Adventure Backend API")
print("=" * 50)

# Test health endpoint
try:
    print("1. Testing health endpoint...")
    response = requests.get(f"{backend_url}/api/health", timeout=10)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   Message: {data.get('message', 'No message')}")
        print(f"   Word Count: {data.get('word_count', 'Unknown')}")
    else:
        print(f"   Error Response: {response.text}")
    print()
except Exception as e:
    print(f"   Error: {str(e)}")
    print()

# Test init-db endpoint
try:
    print("2. Testing database initialization...")
    response = requests.post(f"{backend_url}/api/init-db", timeout=30)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   Message: {data.get('message', 'No message')}")
    else:
        print(f"   Error Response: {response.text}")
    print()
except Exception as e:
    print(f"   Error: {str(e)}")
    print()

# Test words endpoint (this might fail if no auth)
try:
    print("3. Testing words endpoint...")
    response = requests.get(f"{backend_url}/api/words", timeout=10)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        words = response.json()
        print(f"   Word Count: {len(words) if isinstance(words, list) else 'Not a list'}")
    else:
        print(f"   Error Response: {response.text}")
    print()
except Exception as e:
    print(f"   Error: {str(e)}")
    print()

# Test categories endpoint  
try:
    print("4. Testing categories endpoint...")
    response = requests.get(f"{backend_url}/api/categories", timeout=10)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        categories = response.json()
        print(f"   Categories: {categories}")
    else:
        print(f"   Error Response: {response.text}")
    print()
except Exception as e:
    print(f"   Error: {str(e)}")
    print()

print("API testing complete.")
