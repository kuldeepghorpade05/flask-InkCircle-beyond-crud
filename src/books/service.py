from bson import ObjectId
from datetime import datetime
from src.db.models import get_db

class BookService:
    def __init__(self):
        self.db = get_db()
    
    def get_all_books(self):
        """Get all books with user relationships"""
        books = list(self.db.books.find().sort('created_at', -1))
        
        # Populate user information for each book
        for book in books:
            user = self.db.users.find_one({'_id': ObjectId(book['user_uid'])})
            if user:
                book['user'] = {
                    'uid': str(user['_id']),
                    'username': user.get('username'),
                    'email': user.get('email'),
                    'first_name': user.get('first_name'),
                    'last_name': user.get('last_name')
                }
        
        return books
    
    def get_user_books(self, user_uid: str):
        """Get all books for a specific user"""
        try:
            books = list(self.db.books.find({'user_uid': user_uid}).sort('created_at', -1))
            return books
        except:
            return []
    
    def get_book(self, book_uid: str):
        """Get a single book by ID with relationships"""
        try:
            book = self.db.books.find_one({'_id': ObjectId(book_uid)})
            if not book:
                return None
            
            # Get user information
            user = self.db.users.find_one({'_id': ObjectId(book['user_uid'])})
            if user:
                book['user'] = {
                    'uid': str(user['_id']),
                    'username': user.get('username'),
                    'email': user.get('email')
                }
            
            # Get reviews for this book (if you have a reviews collection)
            reviews = list(self.db.reviews.find({'book_uid': book_uid}))
            book['reviews'] = []
            for review in reviews:
                review_user = self.db.users.find_one({'_id': ObjectId(review['user_uid'])})
                book['reviews'].append({
                    'uid': str(review['_id']),
                    'rating': review.get('rating'),
                    'comment': review.get('comment'),
                    'user': {
                        'uid': str(review_user['_id']) if review_user else None,
                        'username': review_user.get('username') if review_user else 'Unknown'
                    } if review_user else None,
                    'created_at': review.get('created_at')
                })
            
            # Get tags for this book (if you have a tags collection)
            book_tags = list(self.db.book_tags.find({'book_uid': book_uid}))
            book['tags'] = []
            for book_tag in book_tags:
                tag = self.db.tags.find_one({'_id': ObjectId(book_tag['tag_uid'])})
                if tag:
                    book['tags'].append({
                        'uid': str(tag['_id']),
                        'name': tag.get('name'),
                        'color': tag.get('color')
                    })
            
            return book
        except Exception as e:
            print(f"Error getting book: {e}")
            return None
    
    def create_book(self, book_data: dict, user_uid: str):
        """Create a new book with user relationship"""
        try:
            # Parse published_date string to datetime
            published_date = datetime.strptime(book_data['published_date'], "%Y-%m-%d")
            
            book_doc = {
                'title': book_data['title'],
                'author': book_data['author'],
                'publisher': book_data['publisher'],
                'published_date': published_date,
                'page_count': book_data['page_count'],
                'language': book_data['language'],
                'user_uid': user_uid,  # This maintains the relationship
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            }
            
            result = self.db.books.insert_one(book_doc)
            book_doc['_id'] = result.inserted_id
            
            return book_doc
        except Exception as e:
            print(f"Error creating book: {e}")
            return None
    
    def update_book(self, book_uid: str, update_data: dict):
        """Update a book - only allow if user owns the book"""
        try:
            # Remove None values
            update_data = {k: v for k, v in update_data.items() if v is not None}
            
            # Parse published_date if it exists
            if 'published_date' in update_data:
                update_data['published_date'] = datetime.strptime(update_data['published_date'], "%Y-%m-%d")
            
            update_data['updated_at'] = datetime.utcnow()
            
            result = self.db.books.update_one(
                {'_id': ObjectId(book_uid)},
                {'$set': update_data}
            )
            
            if result.matched_count > 0:
                return self.get_book(book_uid)
            return None
        except Exception as e:
            print(f"Error updating book: {e}")
            return None
    
    def delete_book(self, book_uid: str):
        """Delete a book - only allow if user owns the book"""
        try:
            result = self.db.books.delete_one({'_id': ObjectId(book_uid)})
            return result.deleted_count > 0
        except Exception as e:
            print(f"Error deleting book: {e}")
            return None
    
    def user_owns_book(self, user_uid: str, book_uid: str) -> bool:
        """Check if user owns the book"""
        try:
            book = self.db.books.find_one({
                '_id': ObjectId(book_uid),
                'user_uid': user_uid
            })
            return book is not None
        except:
            return False