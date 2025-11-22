from flask import request
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity

from src.books.service import BookService
from src.books.schemas import BookCreateSchema, BookUpdateSchema, BookSchema, BookDetailSchema
from src.auth.dependencies import get_current_user, RoleChecker

# namespace
books_ns = Namespace('books', description='Book operations')

# Service instance
book_service = BookService()

# Marshmallow schemas
book_create_schema = BookCreateSchema()
book_update_schema = BookUpdateSchema()
book_schema = BookSchema()
book_detail_schema = BookDetailSchema()

# Flask-RESTX models for Swagger
book_model = books_ns.model('Book', {
    'uid': fields.String(description='Book ID'),
    'title': fields.String(description='Title'),
    'author': fields.String(description='Author'),
    'publisher': fields.String(description='Publisher'),
    'published_date': fields.String(description='Published Date'),
    'page_count': fields.Integer(description='Page Count'),
    'language': fields.String(description='Language'),
    'user_uid': fields.String(description='User ID'),
    'created_at': fields.DateTime(description='Created At'),
    'updated_at': fields.DateTime(description='Updated At')
})

book_detail_model = books_ns.model('BookDetail', {
    'uid': fields.String(description='Book ID'),
    'title': fields.String(description='Title'),
    'author': fields.String(description='Author'),
    'publisher': fields.String(description='Publisher'),
    'published_date': fields.String(description='Published Date'),
    'page_count': fields.Integer(description='Page Count'),
    'language': fields.String(description='Language'),
    'user_uid': fields.String(description='User ID'),
    'created_at': fields.DateTime(description='Created At'),
    'updated_at': fields.DateTime(description='Updated At'),
    'reviews': fields.List(fields.Raw, description='Book Reviews'),
    'tags': fields.List(fields.Raw, description='Book Tags')
})

book_create_model = books_ns.model('BookCreate', {
    'title': fields.String(required=True, description='Title'),
    'author': fields.String(required=True, description='Author'),
    'publisher': fields.String(required=True, description='Publisher'),
    'published_date': fields.String(required=True, description='Published Date (YYYY-MM-DD)'),
    'page_count': fields.Integer(required=True, description='Page Count'),
    'language': fields.String(required=True, description='Language')
})

book_update_model = books_ns.model('BookUpdate', {
    'title': fields.String(description='Title'),
    'author': fields.String(description='Author'),
    'publisher': fields.String(description='Publisher'),
    'published_date': fields.String(description='Published Date (YYYY-MM-DD)'),
    'page_count': fields.Integer(description='Page Count'),
    'language': fields.String(description='Language')
})

def format_book_response(book_doc):
    """Format MongoDB document for response"""
    if not book_doc:
        return None
        
    book = book_doc.copy()
    book['uid'] = str(book['_id'])
    del book['_id']
    
    # Convert datetime objects to ISO format strings
    for field in ['created_at', 'updated_at', 'published_date']:
        if field in book and hasattr(book[field], 'isoformat'):
            book[field] = book[field].isoformat()
    
    return book

def get_current_user_id():
    """Get current user ID from JWT"""
    user_email = get_jwt_identity()
    from src.auth.service import AuthService
    auth_service = AuthService()
    user = auth_service.get_user_by_email(user_email)
    
    # FIX: Check if user exists and has _id before accessing it
    if user and user.get('_id'):
        return str(user['_id'])
    return None  # Return None if user doesn't exist

# =========================
# Get All Books
# =========================
@books_ns.route('/')
class BookList(Resource):
    @books_ns.marshal_list_with(book_model)
    @jwt_required()
    @RoleChecker(['admin', 'user'])
    def get(self):
        """Get all books"""
        try:
            books = book_service.get_all_books()
            formatted_books = [format_book_response(book) for book in books]
            return formatted_books, 200
        except Exception as e:
            return {'message': f'Error fetching books: {str(e)}'}, 500

    @books_ns.expect(book_create_model)
    @books_ns.marshal_with(book_model)
    @jwt_required()
    @RoleChecker(['admin', 'user'])
    def post(self):
        """Create a new book"""
        data = request.get_json()
        
        # Validate input
        errors = book_create_schema.validate(data)
        if errors:
            return {'errors': errors}, 400
        
        try:
            user_uid = get_current_user_id()
            if not user_uid:
                return {'message': 'User not found'}, 404
            
            # Create book
            new_book = book_service.create_book(data, user_uid)
            
            if not new_book:
                return {'message': 'Failed to create book'}, 500
            
            return format_book_response(new_book), 201
            
        except Exception as e:
            return {'message': f'Error creating book: {str(e)}'}, 500

# =========================
# Get User Books
# =========================
@books_ns.route('/user/<string:user_uid>')
class UserBooks(Resource):
    @books_ns.marshal_list_with(book_model)
    @jwt_required()
    @RoleChecker(['admin', 'user'])
    def get(self, user_uid):
        """Get all books for a specific user"""
        try:
            books = book_service.get_user_books(user_uid)
            formatted_books = [format_book_response(book) for book in books]
            return formatted_books, 200
        except Exception as e:
            return {'message': f'Error fetching user books: {str(e)}'}, 500

# =========================
# Get Single Book
# =========================
@books_ns.route('/<string:book_uid>')
class BookDetail(Resource):
    @books_ns.marshal_with(book_detail_model)
    @jwt_required()
    @RoleChecker(['admin', 'user'])
    def get(self, book_uid):
        """Get a single book by ID with relationships"""
        try:
            book = book_service.get_book(book_uid)
            if not book:
                return {'message': 'Book not found'}, 404
            
            return format_book_response(book), 200
        except Exception as e:
            return {'message': f'Error fetching book: {str(e)}'}, 500

    @books_ns.expect(book_update_model)
    @books_ns.marshal_with(book_model)
    @jwt_required()
    @RoleChecker(['admin', 'user'])
    def patch(self, book_uid):
        """Update a book - only if user owns it"""
        data = request.get_json()
        
        # Validate input
        errors = book_update_schema.validate(data)
        if errors:
            return {'errors': errors}, 400
        
        try:
            user_uid = get_current_user_id()
            if not user_uid:
                return {'message': 'User not found'}, 404
            
            # Check if user owns the book
            if not book_service.user_owns_book(user_uid, book_uid):
                return {'message': 'You can only update your own books'}, 403
            
            updated_book = book_service.update_book(book_uid, data)
            if not updated_book:
                return {'message': 'Book not found'}, 404
            
            return format_book_response(updated_book), 200
        except Exception as e:
            return {'message': f'Error updating book: {str(e)}'}, 500

    @jwt_required()
    @RoleChecker(['admin', 'user'])
    def delete(self, book_uid):
        """Delete a book - only if user owns it"""
        try:
            user_uid = get_current_user_id()
            if not user_uid:
                return {'message': 'User not found'}, 404
            
            # Check if user owns the book
            if not book_service.user_owns_book(user_uid, book_uid):
                return {'message': 'You can only delete your own books'}, 403
            
            deleted = book_service.delete_book(book_uid)
            if not deleted:
                return {'message': 'Book not found'}, 404
            
            return {'message': 'Book deleted successfully'}, 204
        except Exception as e:
            return {'message': f'Error deleting book: {str(e)}'}, 500

# =========================
# Get My Books (Current User)
# =========================
@books_ns.route('/me/books')
class MyBooks(Resource):
    @books_ns.marshal_list_with(book_model)
    @jwt_required()
    @RoleChecker(['admin', 'user'])
    def get(self):
        """Get current user's books"""
        try:
            user_uid = get_current_user_id()
            if not user_uid:
                return {'message': 'User not found'}, 404
            
            books = book_service.get_user_books(user_uid)
            formatted_books = [format_book_response(book) for book in books]
            return formatted_books, 200
        except Exception as e:
            return {'message': f'Error fetching your books: {str(e)}'}, 500