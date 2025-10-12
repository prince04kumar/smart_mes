from functools import wraps
from flask import request, jsonify
from user_manager import user_manager

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
        
        # Add user info to request context
        request.current_user = result['user']
        return f(*args, **kwargs)
    
    return decorated_function

def optional_auth(f):
    """Decorator for optional authentication (backward compatibility)"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None
        
        # Get token from Authorization header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]  # Bearer TOKEN
                result = user_manager.verify_token(token)
                if result['success']:
                    request.current_user = result['user']
                else:
                    request.current_user = None
            except (IndexError, Exception):
                request.current_user = None
        else:
            request.current_user = None
        
        return f(*args, **kwargs)
    
    return decorated_function

def get_current_user():
    """Get current authenticated user from request context"""
    return getattr(request, 'current_user', None)