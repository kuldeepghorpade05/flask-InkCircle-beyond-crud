from functools import wraps
from flask import request, jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt, get_jwt_identity
from src.auth.service import AuthService
from src.errors import (
    InvalidToken,
    RefreshTokenRequired,
    AccessTokenRequired,
    InsufficientPermission,
    AccountNotVerified,
)

class RoleChecker:
    def __init__(self, allowed_roles: list):
        self.allowed_roles = allowed_roles
    
    def __call__(self, f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            current_user_id = get_jwt_identity()
            
            # Get user from database
            user_service = AuthService()
            user = user_service.get_user_by_id(current_user_id)
            
            if not user:
                return jsonify({"message": "User not found"}), 404
            
            if not user.get('is_verified', False):
                return jsonify({"message": "Account not verified"}), 403
            
            if user.get('role') not in self.allowed_roles:
                return jsonify({"message": "Insufficient permissions"}), 403
            
            request.current_user = user
            return f(*args, **kwargs)
        return decorated_function

def get_current_user(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        verify_jwt_in_request()
        current_user_id = get_jwt_identity()
        
        user_service = AuthService()
        user = user_service.get_user_by_id(current_user_id)
        
        if not user:
            return jsonify({"message": "User not found"}), 404
        
        request.current_user = user
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        verify_jwt_in_request()
        current_user_id = get_jwt_identity()
        
        user_service = AuthService()
        user = user_service.get_user_by_id(current_user_id)
        
        if not user or user.get('role') != 'admin':
            return jsonify({"message": "Admin access required"}), 403
        
        request.current_user = user
        return f(*args, **kwargs)
    return decorated_function