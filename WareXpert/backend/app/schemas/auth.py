"""Authentication schemas for login, registration, and token management."""
from marshmallow import Schema, fields, validate, validates, ValidationError
from app.schemas import BaseSchema, TimestampSchema


class LoginSchema(BaseSchema):
    """Schema for user login."""
    email = fields.Email(required=True, validate=validate.Length(max=255))
    password = fields.String(required=True, validate=validate.Length(min=6, max=255))
    remember_me = fields.Boolean(missing=False)


class TokenSchema(BaseSchema):
    """Schema for JWT token response."""
    access_token = fields.String(required=True)
    refresh_token = fields.String(required=True)
    token_type = fields.String(missing="Bearer")
    expires_in = fields.Integer(required=True)  # seconds


class RefreshTokenSchema(BaseSchema):
    """Schema for token refresh request."""
    refresh_token = fields.String(required=True)


class ChangePasswordSchema(BaseSchema):
    """Schema for password change."""
    current_password = fields.String(required=True)
    new_password = fields.String(
        required=True,
        validate=validate.Length(min=8, max=255)
    )
    confirm_password = fields.String(required=True)

    @validates('confirm_password')
    def validate_passwords_match(self, value, **kwargs):
        """Validate that new passwords match."""
        if 'new_password' in self.context and value != self.context['new_password']:
            raise ValidationError("Passwords do not match")


class UserSchema(TimestampSchema):
    """Schema for user data."""
    id = fields.Integer(dump_only=True)
    tenant_id = fields.Integer(dump_only=True)
    email = fields.Email(required=True)
    full_name = fields.String(required=True, validate=validate.Length(max=255))
    role = fields.String(
        required=True,
        validate=validate.OneOf([
            'SUPER_ADMIN', 'ADMIN', 'MANAGER', 
            'SELLER', 'WAREHOUSE', 'VIEWER'
        ])
    )
    is_active = fields.Boolean(missing=True)
    is_verified = fields.Boolean(dump_only=True)
    last_login = fields.DateTime(dump_only=True)
    
    # Never expose password hash
    # password is write-only during creation


class UserCreateSchema(BaseSchema):
    """Schema for creating a new user."""
    email = fields.Email(required=True)
    password = fields.String(
        required=True,
        load_only=True,
        validate=validate.Length(min=8, max=255)
    )
    full_name = fields.String(required=True, validate=validate.Length(max=255))
    role = fields.String(
        required=True,
        validate=validate.OneOf([
            'SUPER_ADMIN', 'ADMIN', 'MANAGER', 
            'SELLER', 'WAREHOUSE', 'VIEWER'
        ])
    )


class UserUpdateSchema(BaseSchema):
    """Schema for updating user data."""
    email = fields.Email()
    full_name = fields.String(validate=validate.Length(max=255))
    role = fields.String(
        validate=validate.OneOf([
            'SUPER_ADMIN', 'ADMIN', 'MANAGER', 
            'SELLER', 'WAREHOUSE', 'VIEWER'
        ])
    )
    is_active = fields.Boolean()
