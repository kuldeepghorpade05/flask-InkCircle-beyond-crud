from marshmallow import Schema, fields, validate, validates_schema, ValidationError
from datetime import datetime
import uuid

class UserCreateSchema(Schema):
    first_name = fields.Str(required=True, validate=validate.Length(max=25))
    last_name = fields.Str(required=True, validate=validate.Length(max=25))
    username = fields.Str(required=True, validate=validate.Length(max=20))
    email = fields.Email(required=True, validate=validate.Length(max=40))
    password = fields.Str(required=True, validate=validate.Length(min=6))
    
    class Meta:
        strict = True

class UserSchema(Schema):
    uid = fields.Str(dump_only=True)
    username = fields.Str(required=True)
    email = fields.Email(required=True)
    first_name = fields.Str(required=True)
    last_name = fields.Str(required=True)
    is_verified = fields.Bool(required=True)
    role = fields.Str(required=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    
    class Meta:
        strict = True

class UserLoginSchema(Schema):
    email = fields.Email(required=True, validate=validate.Length(max=40))
    password = fields.Str(required=True, validate=validate.Length(min=6))
    
    class Meta:
        strict = True

class EmailSchema(Schema):
    addresses = fields.List(fields.Email(), required=True)
    
    class Meta:
        strict = True

class PasswordResetRequestSchema(Schema):
    email = fields.Email(required=True)
    
    class Meta:
        strict = True

class PasswordResetConfirmSchema(Schema):
    new_password = fields.Str(required=True, validate=validate.Length(min=6))
    confirm_new_password = fields.Str(required=True, validate=validate.Length(min=6))
    
    @validates_schema
    def validate_passwords(self, data, **kwargs):
        if data['new_password'] != data['confirm_new_password']:
            raise ValidationError('Passwords do not match')
    
    class Meta:
        strict = True