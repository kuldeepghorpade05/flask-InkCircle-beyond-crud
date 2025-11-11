from marshmallow import Schema, fields, validate, ValidationError
from datetime import datetime

class ReviewCreateSchema(Schema):
    rating = fields.Int(required=True, validate=validate.Range(min=1, max=5))
    review_text = fields.Str(required=True, validate=validate.Length(min=1, max=1000))
    
    class Meta:
        strict = True

class ReviewSchema(Schema):
    uid = fields.Str(dump_only=True)
    rating = fields.Int(required=True, validate=validate.Range(min=1, max=5))
    review_text = fields.Str(required=True)
    user_uid = fields.Str(required=True)
    book_uid = fields.Str(required=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    
    class Meta:
        strict = True

class ReviewWithUserSchema(Schema):
    uid = fields.Str(dump_only=True)
    rating = fields.Int(required=True)
    review_text = fields.Str(required=True)
    user_uid = fields.Str(required=True)
    book_uid = fields.Str(required=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    user = fields.Dict(dump_only=True) 
    
    class Meta:
        strict = True