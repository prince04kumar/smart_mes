"""
Setup users table in Supabase
Run this after creating the users table manually in Supabase dashboard
"""

from supabase_user_manager import SupabaseUserManager

def create_users_table_sql():
    """Get SQL to create users table"""
    user_mgr = SupabaseUserManager()
    print("📋 Run this SQL in your Supabase SQL Editor:")
    print("=" * 60)
    print(user_mgr.create_users_table())
    print("=" * 60)

def test_user_operations():
    """Test user operations after table creation"""
    try:
        user_mgr = SupabaseUserManager()
        
        print("🧪 Testing User Operations...")
        
        # Test creating a user
        result = user_mgr.create_user(
            email="test@example.com",
            password="testpass123",
            name="Test User",
            organization="Test Org"
        )
        
        print(f"Create User: {result}")
        
        if result['success']:
            # Test authentication
            auth_result = user_mgr.authenticate_user("test@example.com", "testpass123")
            print(f"Authentication: {auth_result}")
            
            if auth_result['success']:
                user_id = auth_result['user']['id']
                
                # Test token verification
                token = auth_result['token']
                verify_result = user_mgr.verify_token(token)
                print(f"Token Verification: {verify_result}")
                
                # Test increment scan count
                new_count = user_mgr.increment_scan_count(user_id)
                print(f"New Scan Count: {new_count}")
                
                # Test get user stats
                stats = user_mgr.get_user_stats(user_id)
                print(f"User Stats: {stats}")
                
                print("✅ All user operations working!")
                return True
        
        return False
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("🔧 Supabase Users Table Setup")
    print("=" * 50)
    
    create_users_table_sql()
    
    print("\n💡 After running the SQL in Supabase dashboard:")
    print("1. Come back and run: python setup_users_table.py test")
    print("2. Or test manually with the Flask app")
    
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == 'test':
        print("\n🧪 Running tests...")
        if test_user_operations():
            print("🎉 Users table setup complete!")
        else:
            print("❌ Setup failed. Check Supabase dashboard.")