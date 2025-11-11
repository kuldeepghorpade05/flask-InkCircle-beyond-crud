from flask import request
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity

from src.reviews.service import ReviewService
from src.reviews.schemas import ReviewCreateSchema, ReviewSchema, ReviewWithUserSchema
from src.auth.dependencies import RoleChecker

# Create namespace
reviews_ns = Namespace('reviews', description='Review operations')

# Service instance
review_service = ReviewService()

# Marshmallow schemas
review_create_schema = ReviewCreateSchema()
review_schema = ReviewSchema()
review_with_user_schema = ReviewWithUserSchema()

# Flask-RESTX models for Swagger
review_model = reviews_ns.model('Review', {
    'uid': fields.String(description='Review ID'),
    'rating': fields.Integer(description='Rating (1-5)'),
    'review_text': fields.String(description='Review Text'),
    'user_uid': fields.String(description='User ID'),
    'book_uid': fields.String(description='Book ID'),
    'created_at': fields.DateTime(description='Created At'),
    'updated_at': fields.DateTime(description='Updated At')
})

review_with_user_model = reviews_ns.model('ReviewWithUser', {
    'uid': fields.String(description='Review ID'),
    'rating': fields.Integer(description='Rating (1-5)'),
    'review_text': fields.String(description='Review Text'),
    'user_uid': fields.String(description='User ID'),
    'book_uid': fields.String(description='Book ID'),
    'created_at': fields.DateTime(description='Created At'),
    'updated_at': fields.DateTime(description='Updated At'),
    'user': fields.Raw(description='User Information')
})

review_create_model = reviews_ns.model('ReviewCreate', {
    'rating': fields.Integer(required=True, description='Rating (1-5)'),
    'review_text': fields.String(required=True, description='Review Text')
})

def format_review_response(review_doc):
    """Format MongoDB document for response"""
    if not review_doc:
        return None
        
    review = review_doc.copy()
    review['uid'] = str(review['_id'])
    del review['_id']
    
    # Convert datetime objects to ISO format strings
    for field in ['created_at', 'updated_at']:
        if field in review and hasattr(review[field], 'isoformat'):
            review[field] = review[field].isoformat()
    
    return review

# =========================
# Get All Reviews (Admin only)
# =========================
@reviews_ns.route('/')
class ReviewList(Resource):
    @reviews_ns.marshal_list_with(review_with_user_model)
    @jwt_required()
    @RoleChecker(['admin'])
    def get(self):
        """Get all reviews (Admin only)"""
        try:
            reviews = review_service.get_all_reviews()
            formatted_reviews = [format_review_response(review) for review in reviews]
            return formatted_reviews, 200
        except Exception as e:
            return {'message': f'Error fetching reviews: {str(e)}'}, 500

# =========================
# Get Single Review
# =========================
@reviews_ns.route('/<string:review_uid>')
class ReviewDetail(Resource):
    @reviews_ns.marshal_with(review_with_user_model)
    @jwt_required()
    @RoleChecker(['admin', 'user'])
    def get(self, review_uid):
        """Get a single review by ID"""
        try:
            review = review_service.get_review(review_uid)
            if not review:
                return {'message': 'Review not found'}, 404
            
            return format_review_response(review), 200
        except Exception as e:
            return {'message': f'Error fetching review: {str(e)}'}, 500

# =========================
# Add Review to Book
# =========================
@reviews_ns.route('/book/<string:book_uid>')
class BookReviews(Resource):
    @reviews_ns.expect(review_create_model)
    @reviews_ns.marshal_with(review_model)
    @jwt_required()
    @RoleChecker(['admin', 'user'])
    def post(self, book_uid):
        """Add a review to a book"""
        data = request.get_json()
        
        # Validate input
        errors = review_create_schema.validate(data)
        if errors:
            return {'errors': errors}, 400
        
        try:
            user_email = get_jwt_identity()
            result, status_code = review_service.add_review_to_book(user_email, book_uid, data)
            
            if status_code == 201:
                return format_review_response(result), 201
            else:
                return result, status_code
                
        except Exception as e:
            return {'message': f'Error creating review: {str(e)}'}, 500

    @reviews_ns.marshal_list_with(review_with_user_model)
    @jwt_required()
    @RoleChecker(['admin', 'user'])
    def get(self, book_uid):
        """Get all reviews for a specific book"""
        try:
            reviews = review_service.get_book_reviews(book_uid)
            formatted_reviews = [format_review_response(review) for review in reviews]
            return formatted_reviews, 200
        except Exception as e:
            return {'message': f'Error fetching book reviews: {str(e)}'}, 500

# =========================
# Delete Review
# =========================
@reviews_ns.route('/<string:review_uid>')
class DeleteReview(Resource):
    @jwt_required()
    @RoleChecker(['admin', 'user'])
    def delete(self, review_uid):
        """Delete a review - only if user owns it"""
        try:
            user_email = get_jwt_identity()
            result, status_code = review_service.delete_review(review_uid, user_email)
            return result, status_code
        except Exception as e:
            return {'message': f'Error deleting review: {str(e)}'}, 500