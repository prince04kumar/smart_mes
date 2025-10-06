from datetime import datetime, timedelta
from bson import ObjectId
import bcrypt
import jwt
import os
from database import db_manager

class UserManager:
    def __init__(self):
        self.collection = None
        self.secret_key = os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-in-production-2024')
        
    def connect(self):
        """Connect to users collection"""
        if db_manager.client is not None:
            self.collection = db_manager.client[db_manager.database_name]['users']
            return True
        return False
    
    def hash_password(self, password):
        """Hash password using bcrypt"""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    
    def verify_password(self, password, hashed):
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed)
    
    def create_user(self, email, password, name, organization=None):
        """Create a new user account"""
        try:
            if self.collection is None:
                if not self.connect():
                    return {"success": False, "message": "Database connection failed"}
            
            # Check if user already exists
            if self.collection.find_one({"email": email}):
                return {"success": False, "message": "User already exists with this email"}
            
            # Hash password
            hashed_password = self.hash_password(password)
            
            # Create user document
            user_doc = {
                "email": email,
                "password": hashed_password,
                "name": name,
                "organization": organization,
                "created_at": datetime.utcnow(),
                "last_login": None,
                "is_active": True,
                "scan_count": 0,
                "email_settings": {
                    "smtp_host": None,
                    "smtp_port": None,
                    "smtp_email": None,
                    "smtp_password": None,
                    "smtp_enabled": False
                }
            }
            
            result = self.collection.insert_one(user_doc)
            
            if result.inserted_id:
                return {
                    "success": True, 
                    "message": "User created successfully",
                    "user_id": str(result.inserted_id)
                }
            else:
                return {"success": False, "message": "Failed to create user"}
                
        except Exception as e:
            print(f"Error creating user: {str(e)}")
            return {"success": False, "message": f"Error creating user: {str(e)}"}
    
    def authenticate_user(self, email, password):
        """Authenticate user and return JWT token"""
        try:
            if self.collection is None:
                if not self.connect():
                    return {"success": False, "message": "Database connection failed"}
            
            # Find user by email
            user = self.collection.find_one({"email": email, "is_active": True})
            
            if not user:
                return {"success": False, "message": "Invalid credentials"}
            
            # Verify password
            if not self.verify_password(password, user['password']):
                return {"success": False, "message": "Invalid credentials"}
            
            # Update last login
            self.collection.update_one(
                {"_id": user['_id']},
                {"$set": {"last_login": datetime.utcnow()}}
            )
            
            # Generate JWT token
            payload = {
                "user_id": str(user['_id']),
                "email": user['email'],
                "name": user['name'],
                "exp": datetime.utcnow() + timedelta(days=7)  # Token valid for 7 days
            }
            
            token = jwt.encode(payload, self.secret_key, algorithm='HS256')
            
            return {
                "success": True,
                "message": "Login successful",
                "token": token,
                "user": {
                    "id": str(user['_id']),
                    "email": user['email'],
                    "name": user['name'],
                    "organization": user.get('organization'),
                    "scan_count": user.get('scan_count', 0)
                }
            }
            
        except Exception as e:
            print(f"Error authenticating user: {str(e)}")
            return {"success": False, "message": f"Authentication error: {str(e)}"}
    
    def verify_token(self, token):
        """Verify JWT token and return user data"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            return {"success": True, "user": payload}
        except jwt.ExpiredSignatureError:
            return {"success": False, "message": "Token has expired"}
        except jwt.InvalidTokenError:
            return {"success": False, "message": "Invalid token"}
    
    def get_user_by_id(self, user_id):
        """Get user by ID"""
        try:
            if self.collection is None:
                if not self.connect():
                    return {"success": False, "message": "Database connection failed"}
            
            user = self.collection.find_one({"_id": ObjectId(user_id)})
            if user:
                user['_id'] = str(user['_id'])
                # Remove password from response
                user.pop('password', None)
                return {"success": True, "user": user}
            else:
                return {"success": False, "message": "User not found"}
                
        except Exception as e:
            print(f"Error getting user: {str(e)}")
            return {"success": False, "message": f"Error getting user: {str(e)}"}
    
    def update_email_settings(self, user_id, smtp_settings):
        """Update user's SMTP email settings"""
        try:
            if self.collection is None:
                if not self.connect():
                    return {"success": False, "message": "Database connection failed"}
            
            result = self.collection.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": {"email_settings": smtp_settings}}
            )
            
            if result.modified_count > 0:
                return {"success": True, "message": "Email settings updated successfully"}
            else:
                return {"success": False, "message": "Failed to update email settings"}
                
        except Exception as e:
            print(f"Error updating email settings: {str(e)}")
            return {"success": False, "message": f"Error updating email settings: {str(e)}"}
    
    def increment_scan_count(self, user_id):
        """Increment user's scan count"""
        try:
            if self.collection is None:
                if not self.connect():
                    return
            
            self.collection.update_one(
                {"_id": ObjectId(user_id)},
                {"$inc": {"scan_count": 1}}
            )
            
        except Exception as e:
            print(f"Error incrementing scan count: {str(e)}")

# Create global user manager instance
user_manager = UserManager()