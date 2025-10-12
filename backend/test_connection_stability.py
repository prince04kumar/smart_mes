"""
Test Supabase connection stability and user operations
"""
from supabase_user_manager import SupabaseUserManager
import time

def test_connection_stability():
    """Test multiple connection attempts"""
    print("🧪 Testing Supabase Connection Stability")
    print("="*50)
    
    user_manager = SupabaseUserManager()
    
    # Test multiple calls to simulate real usage
    for i in range(5):
        print(f"\n🔄 Test {i+1}/5:")
        
        # Test user creation (if doesn't exist)
        test_email = f"test_user_{i}@example.com"
        result = user_manager.create_user(
            email=test_email,
            password="testpass123",
            name=f"Test User {i}",
            organization="Test Org"
        )
        
        if result['success']:
            print(f"✅ User created: {test_email}")
            
            # Test login
            login_result = user_manager.authenticate_user(test_email, "testpass123")
            if login_result['success']:
                print("✅ Login successful")
                
                # Test get user by ID
                user_id = login_result['user']['id']
                get_result = user_manager.get_user_by_id(user_id)
                if get_result['success']:
                    print("✅ Get user by ID successful")
                else:
                    print(f"❌ Get user by ID failed: {get_result['message']}")
            else:
                print(f"❌ Login failed: {login_result['message']}")
        else:
            if "already exists" in result['message']:
                print(f"ℹ️ User already exists: {test_email}")
                
                # Test login for existing user
                login_result = user_manager.authenticate_user(test_email, "testpass123")
                if login_result['success']:
                    print("✅ Existing user login successful")
                    
                    # Test get user by ID
                    user_id = login_result['user']['id']
                    get_result = user_manager.get_user_by_id(user_id)
                    if get_result['success']:
                        print("✅ Get existing user by ID successful")
                    else:
                        print(f"❌ Get existing user by ID failed: {get_result['message']}")
                else:
                    print(f"❌ Existing user login failed: {login_result['message']}")
            else:
                print(f"❌ User creation failed: {result['message']}")
        
        # Small delay between tests
        time.sleep(1)
    
    print("\n" + "="*50)
    print("🎯 Connection stability test completed")

if __name__ == "__main__":
    try:
        test_connection_stability()
    except KeyboardInterrupt:
        print("\n⚠️ Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()