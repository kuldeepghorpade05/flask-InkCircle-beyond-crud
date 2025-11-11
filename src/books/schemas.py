from marshmallow import Schema, fields, validate, ValidationError
from datetime import datetime

class BookCreateSchema(Schema):
    title = fields.Str(required=True, validate=validate.Length(max=200))
    author = fields.Str(required=True, validate=validate.Length(max=100))
    publisher = fields.Str(required=True, validate=validate.Length(max=100))
    published_date = fields.Str(required=True)
    page_count = fields.Int(required=True, validate=validate.Range(min=1))
    language = fields.Str(required=True, validate=validate.Length(max=20))
    
    class Meta:
        strict = True

class BookUpdateSchema(Schema):
    title = fields.Str(validate=validate.Length(max=200))
    author = fields.Str(validate=validate.Length(max=100))
    publisher = fields.Str(validate=validate.Length(max=100))
    published_date = fields.Str()
    page_count = fields.Int(validate=validate.Range(min=1))
    language = fields.Str(validate=validate.Length(max=20))
    
    class Meta:
        strict = True

class BookSchema(Schema):
    uid = fields.Str(dump_only=True)
    title = fields.Str(required=True)
    author = fields.Str(required=True)
    publisher = fields.Str(required=True)
    published_date = fields.Str(required=True)
    page_count = fields.Int(required=True)
    language = fields.Str(required=True)
    user_uid = fields.Str(required=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    
    class Meta:
        strict = True

class BookDetailSchema(Schema):
    uid = fields.Str(dump_only=True)
    title = fields.Str(required=True)
    author = fields.Str(required=True)
    publisher = fields.Str(required=True)
    published_date = fields.Str(required=True)
    page_count = fields.Int(required=True)
    language = fields.Str(required=True)
    user_uid = fields.Str(required=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    # For relationships - we'll populate these in service
    reviews = fields.List(fields.Dict(), dump_only=True)
    tags = fields.List(fields.Dict(), dump_only=True)
    
    class Meta:
        strict = True