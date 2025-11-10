from bson import ObjectId
from datetime import datetime
from src.db.models import get_db
from src.auth.utils import generate_passwd_hash

class AuthService:
    def __init__(self):
        self.db = get_db()
    
    def get_user_by_email(self, email: str):
        """Get user by email"""
        return self.db.users.find_one({'email': email})
    
    def get_user_by_id(self, user_id: str):
        """Get user by ID"""
        return self.db.users.find_one({'_id': ObjectId(user_id)})
    
    def user_exists(self, email: str):
        """Check if user exists"""
        user = self.get_user_by_email(email)
        return user is not None
    
    def create_user(self, user_data: dict):
        """Create new user"""
        user_data_dict = user_data.copy()
        
        # Create user document
        user_doc = {
            'first_name': user_data_dict['first_name'],
            'last_name': user_data_dict['last_name'],
            'username': user_data_dict['username'],
            'email': user_data_dict['email'],
            'password_hash': generate_passwd_hash(user_data_dict['password']),
            'role': 'user',
            'is_verified': False,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        
        # Insert into MongoDB
        result = self.db.users.insert_one(user_doc)
        user_doc['_id'] = result.inserted_id
        return user_doc
    
    def update_user(self, user_id: str, user_data: dict):
        """Update user data"""
        user_data['updated_at'] = datetime.utcnow()
        
        result = self.db.users.update_one(
            {'_id': ObjectId(user_id)},
            {'$set': user_data}
        )
        return result.modified_count > 0
    
    def verify_user(self, user_id: str):
        """Mark user as verified"""
        return self.update_user(user_id, {'is_verified': True})