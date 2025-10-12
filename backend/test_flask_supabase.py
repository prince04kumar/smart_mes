"""
Test the Flask app with Supabase integration
"""
import requests
import json

BASE_URL = "http://localhost:5000"

def test_health():
    """Test health endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/health")
        print("🔍 Health Check:")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_persons():
    """Test persons endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/persons")
        print("\n🔍 Persons Endpoint:")
        print(f"Status: {response.status_code}")
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Persons test failed: {e}")
        return False

def test_create_person():
    """Test creating a person"""
    try:
        new_person = {
            "name": "Test Student",
            "roll_number": "TEST123",
            "branch": "Computer Science",
            "email": "test@example.com",
            "phone": "1234567890"
        }
        
        response = requests.post(f"{BASE_URL}/persons", json=new_person)
        print("\n🔍 Create Person:")
        print(f"Status: {response.status_code}")
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Create person test failed: {e}")
        return False

def test_setup_sample_data():
    """Test setting up sample data"""
    try:
        response = requests.post(f"{BASE_URL}/setup-sample-data")
        print("\n🔍 Setup Sample Data:")
        print(f"Status: {response.status_code}")
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Setup sample data test failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Flask App with Supabase Integration")
    print("=" * 60)
    
    tests = [
        ("Health Check", test_health),
        ("Setup Sample Data", test_setup_sample_data),
        ("Get Persons", test_persons),
        ("Create Person", test_create_person),
        ("Get Persons Again", test_persons)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔬 Running: {test_name}")
        if test_func():
            print(f"✅ {test_name} PASSED")
            passed += 1
        else:
            print(f"❌ {test_name} FAILED")
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Supabase integration is working perfectly!")
    else:
        print("⚠️ Some tests failed. Please check the Flask server logs.")