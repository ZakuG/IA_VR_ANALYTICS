"""Marshmallow schemas for API serialization and validation."""
from marshmallow import Schema, fields, validate, validates, ValidationError, EXCLUDE
from datetime import datetime


class BaseSchema(Schema):
    """Base schema with common configuration."""
    class Meta:
        unknown = EXCLUDE  # Ignore unknown fields
        ordered = True


class TimestampSchema(BaseSchema):
    """Schema for timestamp fields."""
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


class PaginationSchema(BaseSchema):
    """Schema for pagination parameters."""
    page = fields.Integer(missing=1, validate=validate.Range(min=1))
    per_page = fields.Integer(missing=20, validate=validate.Range(min=1, max=100))
    

class PaginatedResponseSchema(BaseSchema):
    """Schema for paginated responses."""
    items = fields.List(fields.Dict(), required=True)
    total = fields.Integer(required=True)
    page = fields.Integer(required=True)
    per_page = fields.Integer(required=True)
    pages = fields.Integer(required=True)
    has_prev = fields.Boolean(required=True)
    has_next = fields.Boolean(required=True)


class ErrorSchema(BaseSchema):
    """Schema for error responses."""
    error = fields.String(required=True)
    message = fields.String(required=True)
    status_code = fields.Integer(required=True)
    timestamp = fields.DateTime(missing=datetime.utcnow)


class SuccessSchema(BaseSchema):
    """Schema for success responses."""
    message = fields.String(required=True)
    data = fields.Dict(missing=None)
