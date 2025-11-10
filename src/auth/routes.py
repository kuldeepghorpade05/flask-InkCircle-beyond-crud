from flask import request
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import (
    create_access_token, 
    create_refresh_token, 
    jwt_required, 
    get_jwt_identity
)
from datetime import timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from src.config import Config
from src.auth.service import AuthService
from src.auth.schemas import (
    UserCreateSchema, UserLoginSchema, EmailSchema, 
    PasswordResetRequestSchema, PasswordResetConfirmSchema, UserSchema
)
from src.auth.dependencies import get_current_user, RoleChecker
from src.errors import UserAlreadyExists, UserNotFound, InvalidCredentials
from src.auth.utils import create_url_safe_token, decode_url_safe_token

# ========== NAMESPACE MUST COME FIRST ==========
auth_ns = Namespace('auth', description='Authentication operations')

# ========== THEN CELERY IMPORTS ==========
# Try to import celery, but have fallback
# In your routes.py
try:
    from celery_tasks import send_email
    CELERY_AVAILABLE = True
    print("✅ Celery is available for email tasks")
except Exception as e:
    CELERY_AVAILABLE = False
    print(f"⚠️  Celery not available: {e}")


# ========== THEN EMAIL FUNCTIONS ==========
def send_real_email_sync(recipients, subject, html_body, text_body=None):
    """Synchronous email sending as fallback"""
    try:
        from src.config import Config
        
        print(f"📧 [SYNC] Starting email send to {recipients}")
        
        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = Config.MAIL_DEFAULT_SENDER
        msg['To'] = ', '.join(recipients) if isinstance(recipients, list) else recipients

        # Create HTML body
        html_part = MIMEText(html_body, 'html')
        msg.attach(html_part)

        # Send email
        print(f"📧 [SYNC] Connecting to {Config.MAIL_SERVER}:{Config.MAIL_PORT}")
        
        with smtplib.SMTP(Config.MAIL_SERVER, Config.MAIL_PORT) as server:
            if Config.MAIL_USE_TLS:
                server.starttls()
                print("✅ [SYNC] TLS started")
            
            print(f"📧 [SYNC] Logging in as {Config.MAIL_USERNAME}")
            server.login(Config.MAIL_USERNAME, Config.MAIL_PASSWORD)
            print("✅ [SYNC] SMTP login successful")
            
            server.send_message(msg)
            print(f"✅ [SYNC] Email sent successfully to {recipients}")
        
        return True
        
    except Exception as e:
        print(f"❌ [SYNC] Failed to send email: {str(e)}")
        return False

def send_email_fallback(recipients, subject, html_body):
    """Fallback email function when Celery is not available"""
    print(f"📧 [FALLBACK] Using synchronous email fallback")
    return send_real_email_sync(recipients, subject, html_body)

# Use celery if available, otherwise fallback
def send_email_task(recipients, subject, html_body, text_body=None):
    if CELERY_AVAILABLE:
        try:
            task = send_email.delay(recipients, subject, html_body, text_body)
            print(f"✅ [APP] Email task queued with ID: {task.id}")
            return task
        except Exception as e:
            print(f"❌ [APP] Celery task failed, using sync fallback: {e}")
            return send_real_email_sync(recipients, subject, html_body, text_body)
    else:
        print("⚠️ [APP] Celery not available, using sync email")
        return send_real_email_sync(recipients, subject, html_body, text_body)

# Marshmallow schemas
user_create_schema = UserCreateSchema()
user_login_schema = UserLoginSchema()
email_schema = EmailSchema()
password_reset_request_schema = PasswordResetRequestSchema()
password_reset_confirm_schema = PasswordResetConfirmSchema()
user_schema = UserSchema()

# Flask-RESTX models for Swagger
user_model = auth_ns.model('User', {
    'uid': fields.String(description='User ID'),
    'username': fields.String(description='Username'),
    'email': fields.String(description='Email'),
    'first_name': fields.String(description='First Name'),
    'last_name': fields.String(description='Last Name'),
    'is_verified': fields.Boolean(description='Is Verified'),
    'role': fields.String(description='Role'),
    'created_at': fields.DateTime(description='Created At'),
    'updated_at': fields.DateTime(description='Updated At')
})

# ... continue with the rest of your routes.py code ...
user_create_model = auth_ns.model('UserCreate', {
    'first_name': fields.String(required=True, description='First Name'),
    'last_name': fields.String(required=True, description='Last Name'),
    'username': fields.String(required=True, description='Username'),
    'email': fields.String(required=True, description='Email'),
    'password': fields.String(required=True, description='Password')
})

user_login_model = auth_ns.model('UserLogin', {
    'email': fields.String(required=True, description='Email'),
    'password': fields.String(required=True, description='Password')
})

email_model = auth_ns.model('Email', {
    'addresses': fields.List(fields.String, required=True, description='Email addresses')
})

password_reset_request_model = auth_ns.model('PasswordResetRequest', {
    'email': fields.String(required=True, description='Email')
})

password_reset_confirm_model = auth_ns.model('PasswordResetConfirm', {
    'new_password': fields.String(required=True, description='New Password'),
    'confirm_new_password': fields.String(required=True, description='Confirm New Password')
})

token_model = auth_ns.model('Token', {
    'access_token': fields.String(description='Access Token'),
    'refresh_token': fields.String(description='Refresh Token'),
    'token_type': fields.String(description='Token Type')
})

# Service instance
user_service = AuthService()
role_checker = RoleChecker(["admin", "user"])
REFRESH_TOKEN_EXPIRY = 2  # days

def format_user_response(user_doc):
    """Format MongoDB document for response"""
    if not user_doc:
        return None
        
    user = user_doc.copy()
    user['uid'] = str(user['_id'])
    del user['_id']
    
    # Remove sensitive fields
    for field in ['password_hash', '_id', 'password']:
        if field in user:
            del user[field]
    
    # Convert datetime objects to ISO format strings
    for field in ['created_at', 'updated_at']:
        if field in user and hasattr(user[field], 'isoformat'):
            user[field] = user[field].isoformat()
    
    return user

# =========================
# Test Email Endpoint
# =========================
@auth_ns.route('/send_mail')
class SendMail(Resource):
    @auth_ns.expect(email_model)
    @auth_ns.response(200, 'Email sent successfully')
    @auth_ns.response(400, 'Validation error')
    def post(self):
        """Test endpoint to send an email using Celery"""
        data = request.get_json()
        errors = email_schema.validate(data)
        if errors:
            return {'errors': errors}, 400
        
        recipients = data['addresses']
        html = "<h1>Welcome to the app</h1>"
        subject = "Welcome to our app"

        send_email_task(recipients, subject, html)

        return {"message": "Email sent successfully"}, 200

# =========================
# Signup Endpoint
# =========================
@auth_ns.route('/signup')
class Signup(Resource):
    @auth_ns.expect(user_create_model)
    @auth_ns.response(201, 'User created successfully')
    @auth_ns.response(400, 'Validation error or user already exists')
    @auth_ns.response(500, 'Internal server error')
    def post(self):
        """Create user account"""
        data = request.get_json()
        
        # Validate input
        errors = user_create_schema.validate(data)
        if errors:
            return {'errors': errors}, 400
        
        email = data['email']
        
        # Check if user exists
        if user_service.user_exists(email):
            return {'message': 'User already exists'}, 400
        
        try:
            # Create user
            new_user = user_service.create_user(data)
            
            if not new_user:
                return {'message': 'Failed to create user'}, 500

            # Generate verification token
            token = create_url_safe_token({"email": email})
            link = f"{Config.DOMAIN}/api/v1/auth/verify/{token}"

            # Send verification email asynchronously via Celery
            subject = "Verify Your Email"
            html = f"""
            <h1>Verify your Email</h1>
            <p>Click this link to verify your account:</p>
            <a href="{link}">{link}</a>
            """
            send_email_task([email], subject, html)

            return {
                "message": "Account created! Verification email sent.",
                "user": format_user_response(new_user),
                "verification_link": link,  # optional, for testing
            }, 201
            
        except Exception as e:
            return {'message': f'Error creating user: {str(e)}'}, 500

# =========================
# Email Verification Endpoint
# =========================
@auth_ns.route('/verify/<string:token>')
class VerifyUser(Resource):
    @auth_ns.response(200, 'Account verified successfully')
    @auth_ns.response(400, 'Invalid token')
    @auth_ns.response(404, 'User not found')
    @auth_ns.response(500, 'Internal server error')
    def get(self, token):
        """Verify user account using token from email"""
        try:
            token_data = decode_url_safe_token(token)
            if not token_data:
                return {'message': 'Invalid or expired token'}, 400
            
            user_email = token_data.get("email")
            if not user_email:
                return {'message': 'Invalid token'}, 400

            user = user_service.get_user_by_email(user_email)
            if not user:
                return {'message': 'User not found'}, 404

            # Check if already verified
            if user.get('is_verified', False):
                return {'message': 'Account already verified'}, 200

            # Update user as verified - use '_id' from the user object
            user_id = str(user['_id'])  # Convert ObjectId to string
            success = user_service.verify_user(user_id)
            
            if success:
                # Send confirmation email asynchronously via Celery
                subject = "Your Account is Verified!"
                html = f"""
                <h1>Account Verified</h1>
                <p>Hi {user.get('first_name', 'User')},</p>
                <p>Your account has been successfully verified. You can now log in!</p>
                """
                send_email_task([user_email], subject, html)

                return {'message': 'Account verified successfully'}, 200
            else:
                return {'message': 'Error occurred during verification'}, 500
                
        except Exception as e:
            return {'message': f'Verification error: {str(e)}'}, 500

# =========================
# Login Endpoint (Fixed)
# =========================
@auth_ns.route('/login')
class Login(Resource):
    @auth_ns.expect(user_login_model)
    @auth_ns.response(200, 'Login successful')
    @auth_ns.response(400, 'Validation error')
    @auth_ns.response(401, 'Invalid credentials')
    @auth_ns.response(403, 'Account not verified')
    @auth_ns.response(404, 'User not found')
    @auth_ns.response(500, 'Internal server error')
    def post(self):
        """Login user"""
        data = request.get_json()
        
        # Validate input
        errors = user_login_schema.validate(data)
        if errors:
            return {'errors': errors}, 400
        
        email = data['email']
        password = data['password']

        try:
            user = user_service.get_user_by_email(email)
            if not user:
                return {'message': 'User not found'}, 404

            from src.auth.utils import verify_password
            if not verify_password(password, user['password_hash']):
                return {'message': 'Invalid credentials'}, 401

            # Check if user is verified
            if not user.get('is_verified', False):
                return {
                    'message': 'Account not verified. Please check your email.'
                }, 403

            # FIXED: Use email as string identity for JWT
            user_identity = email
            
            # Create tokens
            access_token = create_access_token(identity=user_identity)
            refresh_token = create_refresh_token(identity=user_identity)

            return {
                "message": "Login successful",
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer",
                "user": format_user_response(user),
            }, 200
            
        except Exception as e:
            return {'message': f'Login error: {str(e)}'}, 500

# =========================
# Refresh Token Endpoint
# =========================
@auth_ns.route('/refresh')
class RefreshToken(Resource):
    @jwt_required(refresh=True)
    @auth_ns.response(200, 'Token refreshed successfully')
    @auth_ns.response(401, 'Invalid refresh token')
    def post(self):
        """Refresh access token"""
        try:
            # FIXED: Get email from refresh token identity
            user_email = get_jwt_identity()
            
            # Create new access token
            new_access_token = create_access_token(identity=user_email)
            
            return {
                "message": "Token refreshed successfully",
                "access_token": new_access_token,
                "token_type": "bearer"
            }, 200
            
        except Exception as e:
            return {'message': f'Token refresh error: {str(e)}'}, 401

# =========================
# Logout Endpoint
# =========================
@auth_ns.route('/logout')
class Logout(Resource):
    @jwt_required()
    @auth_ns.response(200, 'Logout successful')
    def post(self):
        """Logout user (client should discard tokens)"""
        # In a real implementation, you might want to add tokens to a blacklist
        return {
            "message": "Logout successful. Please discard your tokens."
        }, 200

# =========================
# Password Reset Request
# =========================
@auth_ns.route('/password-reset-request')
class PasswordResetRequest(Resource):
    @auth_ns.expect(password_reset_request_model)
    @auth_ns.response(200, 'Password reset email sent')
    @auth_ns.response(400, 'Validation error')
    @auth_ns.response(500, 'Internal server error')
    def post(self):
        """Request password reset"""
        data = request.get_json()
        errors = password_reset_request_schema.validate(data)
        if errors:
            return {'errors': errors}, 400
        
        email = data['email']
        
        try:
            # Check if user exists
            user = user_service.get_user_by_email(email)
            if not user:
                # Still return 200 to prevent email enumeration
                return {'message': 'If the email exists, a reset link has been sent'}, 200

            token = create_url_safe_token({"email": email})
            link = f"{Config.DOMAIN}/api/v1/auth/password-reset-confirm/{token}"

            subject = "Reset Your Password"
            html_message = f"""
            <h1>Reset Your Password</h1>
            <p>Click this link to reset your password:</p>
            <a href="{link}">{link}</a>
            <p>This link will expire in 1 hour.</p>
            """
            send_email_task([email], subject, html_message)

            return {
                "message": "Password reset email sent! Check your inbox.",
                "reset_link": link,  # optional, for testing
            }, 200
            
        except Exception as e:
            return {'message': f'Error sending reset email: {str(e)}'}, 500

# =========================
# Password Reset Confirmation
# =========================
@auth_ns.route('/password-reset-confirm/<string:token>')
class PasswordResetConfirm(Resource):
    @auth_ns.expect(password_reset_confirm_model)
    @auth_ns.response(200, 'Password reset successfully')
    @auth_ns.response(400, 'Invalid token or passwords do not match')
    @auth_ns.response(404, 'User not found')
    @auth_ns.response(500, 'Internal server error')
    def post(self, token):
        """Confirm password reset"""
        data = request.get_json()
        errors = password_reset_confirm_schema.validate(data)
        if errors:
            return {'errors': errors}, 400
        
        new_password = data['new_password']
        confirm_password = data['confirm_new_password']
        
        if new_password != confirm_password:
            return {'message': 'Passwords do not match'}, 400

        try:
            token_data = decode_url_safe_token(token)
            if not token_data:
                return {'message': 'Invalid or expired token'}, 400
            
            user_email = token_data.get("email")
            if not user_email:
                return {'message': 'Invalid token'}, 400

            user = user_service.get_user_by_email(user_email)
            if not user:
                return {'message': 'User not found'}, 404

            # Update password
            from src.auth.utils import generate_passwd_hash
            new_password_hash = generate_passwd_hash(new_password)
            
            # Use the correct user ID field (_id converted to string)
            user_id = str(user['_id'])
            success = user_service.update_user(user_id, {'password_hash': new_password_hash})

            if success:
                # Send confirmation email
                subject = "Password Reset Successful"
                html = f"""
                <h1>Password Reset Successful</h1>
                <p>Hi {user.get('first_name', 'User')},</p>
                <p>Your password has been successfully reset.</p>
                """
                send_email_task([user_email], subject, html)
                
                return {'message': 'Password reset successfully'}, 200
            else:
                return {'message': 'Error occurred during password reset'}, 500
                
        except Exception as e:
            return {'message': f'Password reset error: {str(e)}'}, 500

# =========================
# Get Current User (Fixed)
# =========================
@auth_ns.route('/me')
class CurrentUser(Resource):
    @jwt_required()
    @auth_ns.response(200, 'Success', user_model)
    @auth_ns.response(401, 'Unauthorized')
    @auth_ns.response(404, 'User not found')
    def get(self):
        """Get current user information"""
        try:
            # FIXED: Get email from JWT identity
            user_email = get_jwt_identity()
            
            if not user_email:
                return {'message': 'Invalid token payload'}, 401
                
            user = user_service.get_user_by_email(user_email)
            if not user:
                return {'message': 'User not found'}, 404
                
            formatted_user = format_user_response(user)
            return formatted_user, 200
            
        except Exception as e:
            return {'message': f'Error fetching user: {str(e)}'}, 500

# =========================
# Update Current User
# =========================
@auth_ns.route('/me/update')
class UpdateCurrentUser(Resource):
    @auth_ns.expect(auth_ns.model('UserUpdate', {
        'first_name': fields.String(description='First Name'),
        'last_name': fields.String(description='Last Name'),
        'username': fields.String(description='Username')
    }))
    @auth_ns.response(200, 'User updated successfully', user_model)
    @auth_ns.response(400, 'Validation error')
    @auth_ns.response(401, 'Unauthorized')
    @auth_ns.response(500, 'Internal server error')
    @jwt_required()
    def put(self):
        """Update current user information"""
        data = request.get_json()
        
        # Remove fields that shouldn't be updated
        for field in ['email', 'password', 'role', 'is_verified']:
            if field in data:
                del data[field]
        
        if not data:
            return {'message': 'No valid fields to update'}, 400
            
        try:
            user_email = get_jwt_identity()
            user = user_service.get_user_by_email(user_email)
            
            if not user:
                return {'message': 'User not found'}, 404
                
            user_id = str(user['_id'])
            success = user_service.update_user(user_id, data)
            
            if success:
                updated_user = user_service.get_user_by_id(user_id)
                return format_user_response(updated_user), 200
            else:
                return {'message': 'Failed to update user'}, 500
                
        except Exception as e:
            return {'message': f'Update error: {str(e)}'}, 500

# =========================
# Debug Email Configuration
# =========================
@auth_ns.route('/debug_email')
class DebugEmail(Resource):
    def get(self):
        """Debug email configuration"""
        config_info = {
            "mail_server": Config.MAIL_SERVER,
            "mail_port": Config.MAIL_PORT,
            "mail_use_tls": Config.MAIL_USE_TLS,
            "mail_use_ssl": Config.MAIL_USE_SSL,
            "mail_username": Config.MAIL_USERNAME,
            "mail_password_set": bool(Config.MAIL_PASSWORD),
            "mail_default_sender": Config.MAIL_DEFAULT_SENDER,
            "celery_available": CELERY_AVAILABLE,
            "redis_url": Config.REDIS_URL
        }
        return config_info, 200            