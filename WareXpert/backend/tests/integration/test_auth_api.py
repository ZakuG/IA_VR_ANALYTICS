"""
Integration tests for authentication endpoints.
Tests the complete authentication flow including login, token refresh, and logout.
"""

import pytest
import json


@pytest.mark.integration
@pytest.mark.auth
class TestAuthEndpoints:
    """Test cases for authentication API endpoints."""
    
    def test_login_success(self, client, sample_admin_user):
        """Test successful login."""
        response = client.post('/api/auth/login', json={
            'email': 'admin@test.com',
            'password': 'admin123'
        })
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert 'access_token' in data
        assert 'refresh_token' in data
        assert 'user' in data
        assert data['user']['email'] == 'admin@test.com'
        assert data['user']['role'] == 'ADMIN'
    
    def test_login_invalid_email(self, client):
        """Test login with invalid email."""
        response = client.post('/api/auth/login', json={
            'email': 'nonexistent@test.com',
            'password': 'password123'
        })
        
        assert response.status_code == 401
        data = response.get_json()
        assert 'error' in data
    
    def test_login_invalid_password(self, client, sample_admin_user):
        """Test login with invalid password."""
        response = client.post('/api/auth/login', json={
            'email': 'admin@test.com',
            'password': 'wrongpassword'
        })
        
        assert response.status_code == 401
        data = response.get_json()
        assert 'error' in data
    
    def test_login_inactive_user(self, client, sample_admin_user, db_session):
        """Test login with inactive user account."""
        # Deactivate user
        sample_admin_user.is_active = False
        db_session.commit()
        
        response = client.post('/api/auth/login', json={
            'email': 'admin@test.com',
            'password': 'admin123'
        })
        
        assert response.status_code == 403
        data = response.get_json()
        assert 'error' in data
        assert 'deactivated' in data['error'].lower()
    
    def test_login_missing_fields(self, client):
        """Test login with missing fields."""
        response = client.post('/api/auth/login', json={
            'email': 'admin@test.com'
            # Missing password
        })
        
        assert response.status_code == 400
    
    def test_get_current_user(self, client, auth_headers, sample_admin_user):
        """Test getting current user information."""
        response = client.get('/api/auth/me', headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert data['email'] == 'admin@test.com'
        assert data['role'] == 'ADMIN'
        assert 'password_hash' not in data
    
    def test_get_current_user_unauthorized(self, client):
        """Test getting current user without token."""
        response = client.get('/api/auth/me')
        
        assert response.status_code == 401
    
    def test_get_current_user_invalid_token(self, client):
        """Test getting current user with invalid token."""
        headers = {
            'Authorization': 'Bearer invalid_token_here',
            'Content-Type': 'application/json'
        }
        response = client.get('/api/auth/me', headers=headers)
        
        assert response.status_code == 422  # Unprocessable entity (invalid JWT)
    
    def test_refresh_token(self, client, sample_admin_user):
        """Test refreshing access token."""
        # First login to get refresh token
        login_response = client.post('/api/auth/login', json={
            'email': 'admin@test.com',
            'password': 'admin123'
        })
        
        refresh_token = login_response.get_json()['refresh_token']
        
        # Use refresh token to get new access token
        headers = {
            'Authorization': f'Bearer {refresh_token}',
            'Content-Type': 'application/json'
        }
        response = client.post('/api/auth/refresh', headers=headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'access_token' in data
    
    def test_change_password(self, client, auth_headers, sample_admin_user, db_session):
        """Test changing password."""
        response = client.post('/api/auth/change-password', 
            headers=auth_headers,
            json={
                'current_password': 'admin123',
                'new_password': 'newpassword123',
                'confirm_password': 'newpassword123'
            }
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['message'] == 'Password changed successfully'
        
        # Verify old password no longer works
        login_response = client.post('/api/auth/login', json={
            'email': 'admin@test.com',
            'password': 'admin123'
        })
        assert login_response.status_code == 401
        
        # Verify new password works
        login_response = client.post('/api/auth/login', json={
            'email': 'admin@test.com',
            'password': 'newpassword123'
        })
        assert login_response.status_code == 200
    
    def test_change_password_wrong_old_password(self, client, auth_headers):
        """Test changing password with wrong old password."""
        response = client.post('/api/auth/change-password',
            headers=auth_headers,
            json={
                'old_password': 'wrongpassword',
                'new_password': 'newpassword123'
            }
        )
        
        assert response.status_code == 400
    
    def test_logout(self, client, auth_headers):
        """Test logout endpoint."""
        response = client.post('/api/auth/logout', headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'message' in data
