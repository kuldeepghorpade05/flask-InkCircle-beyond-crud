import logging
import uuid
from datetime import datetime, timedelta
from itsdangerous import URLSafeTimedSerializer
from jose import JWTError, jwt
from passlib.context import CryptContext
from flask import current_app

passwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def generate_passwd_hash(password: str) -> str:
    """Generates a bcrypt hash for the password."""
    return passwd_context.hash(password)

def verify_password(password: str, password_hash: str) -> bool:
    """Verifies a password against a bcrypt hash."""
    return passwd_context.verify(password, password_hash)

def create_access_token(user_data: dict, expires_delta: timedelta = None, refresh: bool = False):
    """Create JWT access token"""
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=1)
    
    payload = {
        "user": user_data,
        "exp": expire,
        "jti": str(uuid.uuid4()),
        "refresh": refresh,
    }
    
    token = jwt.encode(
        payload,
        current_app.config['JWT_SECRET_KEY'],
        algorithm='HS256'
    )
    return token

def decode_token(token: str) -> dict:
    """Decode JWT token"""
    try:
        payload = jwt.decode(
            token,
            current_app.config['JWT_SECRET_KEY'],
            algorithms=['HS256']
        )
        return payload
    except JWTError as e:
        logging.exception(e)
        return None

# Email token serializer
def get_serializer():
    return URLSafeTimedSerializer(
        secret_key=current_app.config['SECRET_KEY'],
        salt='email-configuration'
    )

def create_url_safe_token(data: dict) -> str:
    """Create URL-safe token for email verification"""
    serializer = get_serializer()
    return serializer.dumps(data)

def decode_url_safe_token(token: str, max_age: int = 3600) -> dict:
    """Decode URL-safe token for email verification"""
    try:
        serializer = get_serializer()
        return serializer.loads(token, max_age=max_age)
    except Exception as e:
        logging.error(str(e))
        return None