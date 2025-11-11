from flask import request
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required

from src.tags.service import TagService
from src.tags.schemas import TagCreateSchema, TagAddSchema, TagSchema
from src.auth.dependencies import RoleChecker

# Create namespace
tags_ns = Namespace('tags', description='Tag operations')

# Service instance
tag_service = TagService()

# Marshmallow schemas
tag_create_schema = TagCreateSchema()
tag_add_schema = TagAddSchema()
tag_schema = TagSchema()

# Flask-RESTX models for Swagger
tag_model = tags_ns.model('Tag', {
    'uid': fields.String(description='Tag ID'),
    'name': fields.String(description='Tag Name'),
    'created_at': fields.DateTime(description='Created At'),
    'updated_at': fields.DateTime(description='Updated At')
})

tag_create_model = tags_ns.model('TagCreate', {
    'name': fields.String(required=True, description='Tag Name')
})

tag_add_model = tags_ns.model('TagAdd', {
    'tags': fields.List(fields.Nested(tag_create_model), required=True, description='List of tags')
})

def format_tag_response(tag_doc):
    """Format MongoDB document for response"""
    if not tag_doc:
        return None
        
    tag = tag_doc.copy()
    tag['uid'] = str(tag['_id'])
    del tag['_id']
    
    # Convert datetime objects to ISO format strings
    for field in ['created_at', 'updated_at']:
        if field in tag and hasattr(tag[field], 'isoformat'):
            tag[field] = tag[field].isoformat()
    
    return tag

# =========================
# Get All Tags & Create Tag
# =========================
@tags_ns.route('/')
class TagList(Resource):
    @tags_ns.marshal_list_with(tag_model)
    @jwt_required()
    @RoleChecker(['admin', 'user'])
    def get(self):
        """Get all tags"""
        try:
            tags = tag_service.get_all_tags()
            formatted_tags = [format_tag_response(tag) for tag in tags]
            return formatted_tags, 200
        except Exception as e:
            return {'message': f'Error fetching tags: {str(e)}'}, 500

    @tags_ns.expect(tag_create_model)
    @tags_ns.marshal_with(tag_model)
    @jwt_required()
    @RoleChecker(['admin', 'user'])
    def post(self):
        """Create a new tag"""
        data = request.get_json()
        
        # Validate input
        errors = tag_create_schema.validate(data)
        if errors:
            return {'errors': errors}, 400
        
        try:
            result, status_code = tag_service.create_tag(data)
            
            if status_code == 201:
                return format_tag_response(result), 201
            else:
                return result, status_code
                
        except Exception as e:
            return {'message': f'Error creating tag: {str(e)}'}, 500

# =========================
# Add Tags to Book & Get Book Tags
# =========================
@tags_ns.route('/book/<string:book_uid>')
class BookTags(Resource):
    @tags_ns.expect(tag_add_model)
    @jwt_required()
    @RoleChecker(['admin', 'user'])
    def post(self, book_uid):
        """Add tags to a book"""
        data = request.get_json()
        
        # Validate input
        errors = tag_add_schema.validate(data)
        if errors:
            return {'errors': errors}, 400
        
        try:
            result, status_code = tag_service.add_tags_to_book(book_uid, data)
            return result, status_code
        except Exception as e:
            return {'message': f'Error adding tags to book: {str(e)}'}, 500

    @tags_ns.marshal_list_with(tag_model)
    @jwt_required()
    @RoleChecker(['admin', 'user'])
    def get(self, book_uid):
        """Get all tags for a specific book"""
        try:
            tags = tag_service.get_book_tags(book_uid)
            formatted_tags = [format_tag_response(tag) for tag in tags]
            return formatted_tags, 200
        except Exception as e:
            return {'message': f'Error fetching book tags: {str(e)}'}, 500

# =========================
# Delete Tag
# =========================
@tags_ns.route('/<string:tag_uid>')
class DeleteTag(Resource):
    @jwt_required()
    @RoleChecker(['admin', 'user'])
    def delete(self, tag_uid):
        """Delete a tag"""
        try:
            result, status_code = tag_service.delete_tag(tag_uid)
            return result, status_code
        except Exception as e:
            return {'message': f'Error deleting tag: {str(e)}'}, 500