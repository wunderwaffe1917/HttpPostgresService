import jwt
import os
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify, current_app
from models import ApiToken, db

def generate_token(payload):
    """Generate a JWT token with the given payload"""
    try:
        # Add expiration time (24 hours from now)
        payload['exp'] = datetime.utcnow() + timedelta(days=1)
        payload['iat'] = datetime.utcnow()
        
        token = jwt.encode(
            payload,
            current_app.config['JWT_SECRET_KEY'],
            algorithm='HS256'
        )
        return token
    except Exception as e:
        current_app.logger.error(f"Error generating token: {str(e)}")
        return None

def decode_token(token):
    """Decode and validate a JWT token"""
    try:
        payload = jwt.decode(
            token,
            current_app.config['JWT_SECRET_KEY'],
            algorithms=['HS256']
        )
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def require_auth(f):
    """Decorator to require Bearer token authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Get token from Authorization header
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            return jsonify({
                'error': 'Authorization header is required',
                'message': 'Please provide a Bearer token in the Authorization header'
            }), 401
        
        # Check if header starts with 'Bearer '
        if not auth_header.startswith('Bearer '):
            return jsonify({
                'error': 'Invalid authorization header format',
                'message': 'Authorization header must start with "Bearer "'
            }), 401
        
        # Extract token
        token = auth_header.split(' ')[1]
        
        # Validate token in database
        db_token = ApiToken.query.filter_by(token=token, is_active=True).first()
        if not db_token:
            return jsonify({
                'error': 'Invalid or inactive token',
                'message': 'The provided token is not valid or has been deactivated'
            }), 401
        
        # Decode JWT token
        payload = decode_token(token)
        if not payload:
            return jsonify({
                'error': 'Invalid token',
                'message': 'The provided token is invalid or expired'
            }), 401
        
        # Update last used timestamp
        db_token.last_used = datetime.utcnow()
        db.session.commit()
        
        # Add payload to request context
        request.current_user = payload
        
        return f(*args, **kwargs)
    
    return decorated_function

def validate_json_input(required_fields=None):
    """Decorator to validate JSON input"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not request.is_json:
                return jsonify({
                    'error': 'Content-Type must be application/json'
                }), 400
            
            data = request.get_json()
            if not data:
                return jsonify({
                    'error': 'Request body must contain valid JSON'
                }), 400
            
            if required_fields:
                missing_fields = [field for field in required_fields if field not in data]
                if missing_fields:
                    return jsonify({
                        'error': 'Missing required fields',
                        'missing_fields': missing_fields
                    }), 400
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator
