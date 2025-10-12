from datetime import datetime, timedelta
import bcrypt
import jwt
import os
from supabase_manager import SupabaseManager
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class SupabaseUserManager:
    def __init__(self):
        self.supabase_manager = SupabaseManager()
        self.secret_key = os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-in-production-2024')
        
    def connect(self):
        """Test Supabase connection"""
        try:
            return self.supabase_manager.test_connection()
        except Exception as e:
            print(f"❌ User manager connection failed: {e}")
            return False
    
    def create_users_table(self):
        """Create users table in Supabase (run this SQL in Supabase dashboard)"""
        sql = """
        -- Create users table
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            email VARCHAR(255) UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            name VARCHAR(255) NOT NULL,
            organization VARCHAR(255),
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW(),
            last_login TIMESTAMP,
            is_active BOOLEAN DEFAULT true,
            scan_count INTEGER DEFAULT 0
        );

        -- Create indexes
        CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
        CREATE INDEX IF NOT EXISTS idx_users_active ON users(is_active);

        -- Enable RLS
        ALTER TABLE users ENABLE ROW LEVEL SECURITY;

        -- Create policy
        CREATE POLICY "Enable all operations for anon users" ON users
            FOR ALL USING (true);
        """
        return sql
    
    def hash_password(self, password):
        """Hash password using bcrypt"""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def verify_password(self, password, hashed):
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    
    def create_user(self, email, password, name, organization=None):
        """Create a new user account"""
        try:
            # Check if user already exists
            existing_user = self.supabase_manager.supabase.table('users').select('id').eq('email', email).execute()
            
            if existing_user.data and len(existing_user.data) > 0:
                return {"success": False, "message": "User already exists with this email"}
            
            # Hash password
            hashed_password = self.hash_password(password)
            
            # Create user data
            user_data = {
                "email": email,
                "password_hash": hashed_password,
                "name": name,
                "organization": organization,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "is_active": True,
                "scan_count": 0
            }
            
            # Insert user into Supabase
            result = self.supabase_manager.supabase.table('users').insert(user_data).execute()
            
            if result.data and len(result.data) > 0:
                user_id = result.data[0]['id']
                print(f"✅ Created user: {name} ({email}) with ID: {user_id}")
                
                return {
                    "success": True, 
                    "message": "User created successfully",
                    "user_id": user_id
                }
            else:
                return {"success": False, "message": "Failed to create user"}
                
        except Exception as e:
            print(f"❌ Error creating user: {str(e)}")
            return {"success": False, "message": f"Database error: {str(e)}"}
    
    def authenticate_user(self, email, password):
        """Authenticate user login"""
        try:
            # Get user from database
            result = self.supabase_manager.supabase.table('users').select('*').eq('email', email).eq('is_active', True).execute()
            
            if not result.data or len(result.data) == 0:
                return {"success": False, "message": "Invalid email or password"}
            
            user = result.data[0]
            
            # Verify password
            if not self.verify_password(password, user['password_hash']):
                return {"success": False, "message": "Invalid email or password"}
            
            # Update last login
            self.supabase_manager.supabase.table('users').update({
                'last_login': datetime.now().isoformat()
            }).eq('id', user['id']).execute()
            
            # Generate JWT token
            token = self.generate_token(user['id'], user['email'])
            
            return {
                "success": True,
                "message": "Login successful",
                "token": token,
                "user": {
                    "id": user['id'],
                    "email": user['email'],
                    "name": user['name'],
                    "organization": user.get('organization'),
                    "scan_count": user.get('scan_count', 0)
                }
            }
            
        except Exception as e:
            print(f"❌ Error authenticating user: {str(e)}")
            return {"success": False, "message": f"Authentication error: {str(e)}"}
    
    def generate_token(self, user_id, email):
        """Generate JWT token for user"""
        payload = {
            'user_id': user_id,
            'email': email,
            'exp': datetime.utcnow() + timedelta(days=7),  # Token expires in 7 days
            'iat': datetime.utcnow()
        }
        
        token = jwt.encode(payload, self.secret_key, algorithm='HS256')
        return token
    
    def verify_token(self, token):
        """Verify JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            return {"success": True, "payload": payload}
        except jwt.ExpiredSignatureError:
            return {"success": False, "message": "Token has expired"}
        except jwt.InvalidTokenError:
            return {"success": False, "message": "Invalid token"}
    
    def get_user_by_id(self, user_id):
        """Get user information by ID with retry logic"""
        max_retries = 3
        retry_delay = 1
        
        for attempt in range(max_retries):
            try:
                # Reinitialize Supabase manager if needed
                if not hasattr(self, 'supabase_manager') or not self.supabase_manager:
                    from supabase_manager import SupabaseManager
                    self.supabase_manager = SupabaseManager()
                
                result = self.supabase_manager.supabase.table('users').select('id,email,name,organization,scan_count,created_at,last_login').eq('id', user_id).eq('is_active', True).execute()
                
                if result.data and len(result.data) > 0:
                    return {"success": True, "user": result.data[0]}
                else:
                    return {"success": False, "message": "User not found"}
                    
            except Exception as e:
                print(f"❌ Error getting user (attempt {attempt + 1}/{max_retries}): {str(e)}")
                if attempt < max_retries - 1:
                    import time
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                else:
                    # Last attempt failed, return error
                    return {"success": False, "message": f"Database connection failed after {max_retries} attempts"}
    
    def increment_scan_count(self, user_id):
        """Increment user's scan count"""
        try:
            # Get current count
            result = self.supabase_manager.supabase.table('users').select('scan_count').eq('id', user_id).execute()
            
            if result.data and len(result.data) > 0:
                current_count = result.data[0].get('scan_count', 0)
                new_count = current_count + 1
                
                # Update count
                self.supabase_manager.supabase.table('users').update({
                    'scan_count': new_count
                }).eq('id', user_id).execute()
                
                print(f"✅ Incremented scan count for user {user_id}: {current_count} -> {new_count}")
                return new_count
            
            return 0
            
        except Exception as e:
            print(f"❌ Error incrementing scan count: {str(e)}")
            return 0
    
    def update_email_settings(self, user_id, smtp_settings):
        """Update user's email settings (can be extended later)"""
        try:
            # For now, just return success
            # In future, can store user-specific email settings
            return {
                "success": True,
                "message": "Email settings updated successfully"
            }
        except Exception as e:
            print(f"❌ Error updating email settings: {str(e)}")
            return {"success": False, "message": f"Error: {str(e)}"}
    
    def get_user_stats(self, user_id):
        """Get user statistics"""
        try:
            result = self.supabase_manager.supabase.table('users').select('scan_count,created_at,last_login').eq('id', user_id).execute()
            
            if result.data and len(result.data) > 0:
                user_data = result.data[0]
                return {
                    "success": True,
                    "stats": {
                        "scan_count": user_data.get('scan_count', 0),
                        "member_since": user_data.get('created_at'),
                        "last_login": user_data.get('last_login')
                    }
                }
            else:
                return {"success": False, "message": "User not found"}
                
        except Exception as e:
            print(f"❌ Error getting user stats: {str(e)}")
            return {"success": False, "message": f"Database error: {str(e)}"}

# Test function
def test_supabase_user_manager():
    """Test the Supabase user manager"""
    try:
        user_mgr = SupabaseUserManager()
        
        print("🔍 Testing Supabase User Manager...")
        
        if user_mgr.connect():
            print("✅ User manager connected successfully!")
            
            print("\n📋 SQL to create users table:")
            print(user_mgr.create_users_table())
            
            return True
        else:
            print("❌ User manager connection failed!")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return False

if __name__ == "__main__":
    test_supabase_user_manager()