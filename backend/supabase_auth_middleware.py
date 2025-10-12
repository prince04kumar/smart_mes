from functools import wraps
from flask import request, jsonify
from supabase_user_manager import SupabaseUserManager

# Initialize user manager
user_manager = SupabaseUserManager()

def require_auth(f):
    """Decorator to require authentication for protected routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None
        
        # Get token from Authorization header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]  # Bearer TOKEN
            except IndexError:
                return jsonify({'message': 'Invalid token format'}), 401
        
        if not token:
            return jsonify({'message': 'Token is missing'}), 401
        
        # Verify token
        result = user_manager.verify_token(token)
        if not result['success']:
            return jsonify({'message': result['message']}), 401
        
        # Get user details
        user_result = user_manager.get_user_by_id(result['payload']['user_id'])
        if not user_result['success']:
            print(f"❌ Auth middleware: {user_result['message']}")
            if "connection" in user_result['message'].lower():
                return jsonify({'message': 'Database connection error. Please try again.'}), 503
            return jsonify({'message': 'User not found'}), 401
        
        # Add user info to request context
        request.current_user = {
            'user_id': result['payload']['user_id'],
            'email': result['payload']['email'],
            **user_result['user']
        }
        return f(*args, **kwargs)
    
    return decorated_function

def optional_auth(f):
    """Decorator for optional authentication (backward compatibility)"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None
        request.current_user = None
        
        # Get token from Authorization header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]  # Bearer TOKEN
                result = user_manager.verify_token(token)
                if result['success']:
                    # Get user details
                    user_result = user_manager.get_user_by_id(result['payload']['user_id'])
                    if user_result['success']:
                        request.current_user = {
                            'user_id': result['payload']['user_id'],
                            'email': result['payload']['email'],
                            **user_result['user']
                        }
                    else:
                        print(f"⚠️ Optional auth - user lookup failed: {user_result['message']}")
                        request.current_user = None
                else:
                    print(f"⚠️ Optional auth - token verification failed: {result['message']}")
                    request.current_user = None
            except (IndexError, Exception) as e:
                print(f"⚠️ Optional auth error: {e}")
                request.current_user = None
        
        return f(*args, **kwargs)
    
    return decorated_function

def get_current_user():
    """Get current user from request context"""
    return getattr(request, 'current_user', None)