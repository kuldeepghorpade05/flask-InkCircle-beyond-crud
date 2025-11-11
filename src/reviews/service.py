from bson import ObjectId
from datetime import datetime
from src.db.models import get_db

class ReviewService:
    def __init__(self):
        self.db = get_db()
    
    def get_all_reviews(self):
        """Get all reviews with user and book information"""
        reviews = list(self.db.reviews.find().sort('created_at', -1))
        
        # Populate user and book information
        for review in reviews:
            # Get user information
            user = self.db.users.find_one({'_id': ObjectId(review['user_uid'])})
            if user:
                review['user'] = {
                    'uid': str(user['_id']),
                    'username': user.get('username'),
                    'email': user.get('email'),
                    'first_name': user.get('first_name'),
                    'last_name': user.get('last_name')
                }
            
            # Get book information
            book = self.db.books.find_one({'_id': ObjectId(review['book_uid'])})
            if book:
                review['book'] = {
                    'uid': str(book['_id']),
                    'title': book.get('title'),
                    'author': book.get('author')
                }
        
        return reviews
    
    def get_review(self, review_uid: str):
        """Get a single review by ID"""
        try:
            review = self.db.reviews.find_one({'_id': ObjectId(review_uid)})
            if review:
                # Populate user information
                user = self.db.users.find_one({'_id': ObjectId(review['user_uid'])})
                if user:
                    review['user'] = {
                        'uid': str(user['_id']),
                        'username': user.get('username'),
                        'email': user.get('email')
                    }
            return review
        except:
            return None
    
    def get_book_reviews(self, book_uid: str):
        """Get all reviews for a specific book"""
        try:
            reviews = list(self.db.reviews.find({'book_uid': book_uid}).sort('created_at', -1))
            
            # Populate user information
            for review in reviews:
                user = self.db.users.find_one({'_id': ObjectId(review['user_uid'])})
                if user:
                    review['user'] = {
                        'uid': str(user['_id']),
                        'username': user.get('username'),
                        'email': user.get('email'),
                        'first_name': user.get('first_name'),
                        'last_name': user.get('last_name')
                    }
            
            return reviews
        except:
            return []
    
    def add_review_to_book(self, user_email: str, book_uid: str, review_data: dict):
        """Add a review to a book"""
        try:
            # Get user by email
            from src.auth.service import AuthService
            auth_service = AuthService()
            user = auth_service.get_user_by_email(user_email)
            
            if not user:
                return {'error': 'User not found'}, 404
            
            # Check if book exists
            from src.books.service import BookService
            book_service = BookService()
            book = book_service.get_book(book_uid)
            
            if not book:
                return {'error': 'Book not found'}, 404
            
            # Check if user already reviewed this book
            existing_review = self.db.reviews.find_one({
                'user_uid': str(user['_id']),
                'book_uid': book_uid
            })
            
            if existing_review:
                return {'error': 'You have already reviewed this book'}, 400
            
            # Create review document
            review_doc = {
                'rating': review_data['rating'],
                'review_text': review_data['review_text'],
                'user_uid': str(user['_id']),
                'book_uid': book_uid,
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            }
            
            result = self.db.reviews.insert_one(review_doc)
            review_doc['_id'] = result.inserted_id
            
            return review_doc, 201
            
        except Exception as e:
            return {'error': f'Error creating review: {str(e)}'}, 500
    
    def delete_review(self, review_uid: str, user_email: str):
        """Delete a review - only if user owns it"""
        try:
            # Get user by email
            from src.auth.service import AuthService
            auth_service = AuthService()
            user = auth_service.get_user_by_email(user_email)
            
            if not user:
                return {'error': 'User not found'}, 404
            
            # Check if review exists and user owns it
            review = self.db.reviews.find_one({
                '_id': ObjectId(review_uid),
                'user_uid': str(user['_id'])
            })
            
            if not review:
                return {'error': 'Review not found or you do not own this review'}, 404
            
            # Delete the review
            result = self.db.reviews.delete_one({'_id': ObjectId(review_uid)})
            
            if result.deleted_count > 0:
                return {'message': 'Review deleted successfully'}, 200
            else:
                return {'error': 'Failed to delete review'}, 500
                
        except Exception as e:
            return {'error': f'Error deleting review: {str(e)}'}, 500
    
    def user_owns_review(self, user_uid: str, review_uid: str) -> bool:
        """Check if user owns the review"""
        try:
            review = self.db.reviews.find_one({
                '_id': ObjectId(review_uid),
                'user_uid': user_uid
            })
            return review is not None
        except:
            return False