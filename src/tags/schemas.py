from marshmallow import Schema, fields, validate, ValidationError
from datetime import datetime

class TagCreateSchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=1, max=50))
    
    class Meta:
        strict = True

class TagAddSchema(Schema):
    tags = fields.List(fields.Nested(TagCreateSchema), required=True)
    
    class Meta:
        strict = True

class TagSchema(Schema):
    uid = fields.Str(dump_only=True)
    name = fields.Str(required=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    
    class Meta:
        strict = True