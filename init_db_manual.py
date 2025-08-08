#!/usr/bin/env python3
"""
Manual database initialization script using Python requests
"""

import requests
import sys

# Backend URL from AGENTS.md
BACKEND_URL = "https://web-production-e17b.up.railway.app"

def check_health():
    """Check if the backend is healthy and get word count"""
    try:
        print("🔄 Checking backend health...")
        response = requests.get(f"{BACKEND_URL}/api/health", timeout=30)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Backend is healthy: {data.get('message', 'Running')}")
            print(f"📊 Current word count: {data.get('word_count', 'Unknown')}")
            return data
        else:
            print(f"❌ Backend health check failed: {response.status_code}")
            print(response.text)
            return None
    except Exception as e:
        print(f"❌ Failed to connect to backend: {str(e)}")
        return None

def initialize_database():
    """Initialize the database by calling the init-db endpoint"""
    try:
        print("🔄 Initializing database with 200 words...")
        response = requests.post(f"{BACKEND_URL}/api/init-db", timeout=120)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ {data.get('message', 'Database initialized successfully')}")
            return True
        else:
            print(f"❌ Database initialization failed: {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print(f"❌ Failed to initialize database: {str(e)}")
        return False

def verify_words():
    """Verify that the database now has words"""
    try:
        print("🔄 Verifying database contents...")
        response = requests.get(f"{BACKEND_URL}/api/words", timeout=30)
        if response.status_code == 200:
            words = response.json()
            print(f"✅ Database now contains {len(words)} words")
            
            # Show some categories
            categories = {}
            for word in words:
                cat = word.get('category', 'unknown')
                categories[cat] = categories.get(cat, 0) + 1
            
            print("📊 Words by category:")
            for cat, count in categories.items():
                print(f"  - {cat}: {count} words")
            
            return len(words) > 0
        else:
            print(f"❌ Failed to fetch words: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Failed to verify words: {str(e)}")
        return False

def test_categories():
    """Test the categories endpoint"""
    try:
        print("🔄 Testing categories endpoint...")
        response = requests.get(f"{BACKEND_URL}/api/categories", timeout=30)
        if response.status_code == 200:
            categories = response.json()
            print(f"✅ Available categories: {[cat.get('name', cat) if isinstance(cat, dict) else cat for cat in categories]}")
            return True
        else:
            print(f"❌ Failed to fetch categories: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Failed to test categories: {str(e)}")
        return False

def main():
    print("=== Word Adventure Database Initialization ===\n")
    
    # Step 1: Check current status
    print("1. Checking backend health...")
    health_data = check_health()
    if not health_data:
        print("❌ Cannot proceed - backend is not accessible")
        sys.exit(1)
    
    current_word_count = health_data.get('word_count', 0)
    print(f"   Current word count: {current_word_count}\n")
    
    # Step 2: Initialize database
    print("2. Initializing database...")
    if initialize_database():
        print("   ✅ Database initialization completed\n")
    else:
        print("   ❌ Database initialization failed")
        sys.exit(1)
    
    # Step 3: Verify the result
    print("3. Verifying database contents...")
    if verify_words():
        print("   ✅ Database verification successful\n")
    else:
        print("   ❌ Database verification failed")
        sys.exit(1)
    
    # Step 4: Test categories endpoint
    print("4. Testing categories endpoint...")
    if test_categories():
        print("   ✅ Categories endpoint working\n")
    else:
        print("   ❌ Categories endpoint failed")
    
    print("🎉 Database initialization complete!")
    print(f"🔗 Backend URL: {BACKEND_URL}")
    print("📱 Frontend URL: https://words-adventure.netlify.app")

if __name__ == "__main__":
    main()
