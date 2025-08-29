# SyriaGPT API Documentation

A comprehensive FastAPI-based authentication and session management system for SyriaGPT.

## Table of Contents

- [Overview](#overview)
- [Getting Started](#getting-started)
- [Authentication](#authentication)
- [API Endpoints](#api-endpoints)
  - [Root Endpoints](#root-endpoints)
  - [Authentication Endpoints](#authentication-endpoints)
  - [Session Management Endpoints](#session-management-endpoints)
- [Data Models](#data-models)
- [Error Handling](#error-handling)
- [Configuration](#configuration)
- [Recent Improvements](#recent-improvements)

## Overview

SyriaGPT API is a FastAPI-based backend service that provides comprehensive authentication, user management, and session handling capabilities. The API supports traditional email/password authentication, OAuth social login (Google and Facebook), two-factor authentication (2FA), and advanced session management.

### Features

- 🔐 **Multi-factor Authentication**: Email/password + optional 2FA
- 🌐 **OAuth Integration**: Google and Facebook social login
- 📧 **Email Verification**: Secure email verification system
- 🔄 **Password Reset**: Forgot password functionality
- 📱 **Session Management**: Multi-device session tracking
- 🛡️ **Security**: JWT tokens, password strength validation
- 🌍 **Internationalization**: Arabic language support
- 📊 **Structured Logging**: Comprehensive logging with rotation
- 🔧 **Health Checks**: Application and database health monitoring
- 🚀 **Performance Optimized**: Connection pooling and caching

## Getting Started

### Prerequisites

- Python 3.8+
- PostgreSQL database
- SMTP server for email functionality

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd SyriaGPT
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   Copy the example environment file and configure it:
   ```bash
   cp env.example .env
   ```
   
   Update the `.env` file with your configuration:
   ```env
   DATABASE_URL=postgresql://user:password@localhost/syriagpt
   SECRET_KEY=your-secret-key
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   SMTP_HOST=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USERNAME=your-email@gmail.com
   SMTP_PASSWORD=your-app-password
   GOOGLE_CLIENT_ID=your-google-client-id
   GOOGLE_CLIENT_SECRET=your-google-client-secret
   FACEBOOK_CLIENT_ID=your-facebook-client-id
   FACEBOOK_CLIENT_SECRET=your-facebook-client-secret
   ```

4. **Run database migrations**
   ```bash
   alembic upgrade head
   ```

5. **Start the server**
   ```bash
   uvicorn main:app --reload
   ```

The API will be available at `http://localhost:8000`

### Docker Setup

1. **Build and run with Docker Compose**
   ```bash
   docker-compose up --build
   ```

2. **Access the services**
   - API: http://localhost:9000
   - API Documentation: http://localhost:9000/docs
   - PgAdmin: http://localhost:5050

### API Documentation

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## Recent Improvements

### Security Enhancements
- ✅ **Removed hardcoded credentials** from Docker Compose
- ✅ **Enhanced JWT security** with proper secret key validation
- ✅ **Improved password validation** with comprehensive strength checks
- ✅ **Fixed database model duplication** issues

### Performance Optimizations
- ✅ **Database connection pooling** for better performance
- ✅ **Structured logging** with rotation and multiple handlers
- ✅ **Health checks** for application and database monitoring
- ✅ **CORS middleware** for proper cross-origin handling

### Code Quality Improvements
- ✅ **Integrated session management** into main application
- ✅ **Updated dependencies** with pinned versions
- ✅ **Enhanced error handling** across services
- ✅ **Improved configuration management**

### Infrastructure Improvements
- ✅ **Docker health checks** for all services
- ✅ **Environment variable templates** for easy setup
- ✅ **Better service dependencies** with health check conditions
- ✅ **Comprehensive logging** configuration

## Authentication

The API uses JWT (JSON Web Tokens) for authentication. Most endpoints require authentication via Bearer token in the Authorization header:

```
Authorization: Bearer <your-jwt-token>
```

### Token Types

- **Access Token**: Short-lived token for API access (default: 30 minutes)
- **Refresh Token**: Long-lived token for obtaining new access tokens
- **Session Token**: Unique identifier for each user session

## API Endpoints

### Root Endpoints

#### GET `/`
Welcome endpoint that returns basic API information.

**Response:**
```json
{
  "message": "Welcome to Syria GPT!",
  "version": "1.0.0"
}
```

#### GET `/hello/{name}`
Simple greeting endpoint.

**Parameters:**
- `name` (string, path): Name to greet

**Response:**
```json
{
  "message": "Hello, {name}! Welcome to Syria GPT."
}
```

#### GET `/health`
Health check endpoint for monitoring.

**Response:**
```json
{
  "status": "healthy",
  "service": "SyriaGPT API",
  "version": "1.0.0"
}
```

### Authentication Endpoints

All authentication endpoints are prefixed with `/auth`.

#### POST `/auth/register`
Register a new user account.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!",
  "phone_number": "+1234567890",
  "first_name": "John",
  "last_name": "Doe"
}
```

**Response (201 Created):**
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "phone_number": "+1234567890",
  "full_name": "John Doe",
  "profile_picture": null,
  "oauth_provider": null,
  "status": "pending_verification",
  "is_email_verified": false,
  "is_phone_verified": false,
  "created_at": "2024-01-01T00:00:00Z",
  "registration_token": "token-string",
  "message": "Registration successful. Please check your email for verification."
}
```

#### GET `/auth/verify-email/{token}`
Verify user email address using verification token.

**Parameters:**
- `token` (string, path): Email verification token

**Response:**
```json
{
  "message": "Email verified successfully",
  "verified": true,
  "user_id": "uuid",
  "email": "user@example.com"
}
```

#### POST `/auth/login`
Authenticate user with email and password.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!",
  "remember_me": false,
  "two_factor_code": "123456"
}
```

**Response:**
```json
{
  "access_token": "jwt-token",
  "token_type": "bearer",
  "user_id": "uuid",
  "email": "user@example.com",
  "full_name": "John Doe",
  "two_factor_required": false,
  "message": "Login successful"
}
```

#### POST `/auth/forgot-password`
Request password reset email.

**Request Body:**
```json
{
  "email": "user@example.com"
}
```

**Response:**
```json
{
  "msg": "تم إرسال رابط إعادة التعيين إلى بريدك الإلكتروني"
}
```

#### POST `/auth/reset-password`
Reset password using reset token.

**Request Body:**
```json
{
  "token": "reset-token",
  "new_password": "NewSecurePassword123!",
  "confirm_password": "NewSecurePassword123!"
}
```

**Response:**
```json
{
  "msg": "تمت إعادة تعيين كلمة المرور بنجاح، وتم تسجيل خروجك من جميع الأجهزة"
}
```

#### GET `/auth/oauth/providers`
Get available OAuth providers.

**Response:**
```json
{
  "providers": ["google", "facebook"],
  "configured_providers": {
    "google": true,
    "facebook": true
  }
}
```

#### POST `/auth/oauth/{provider}/authorize`
Get OAuth authorization URL.

**Parameters:**
- `provider` (string, path): OAuth provider ("google" or "facebook")

**Request Body:**
```json
{
  "provider": "google",
  "redirect_uri": "https://yourapp.com/callback"
}
```

**Response:**
```json
{
  "authorization_url": "https://accounts.google.com/oauth/authorize?...",
  "redirect_uri": "https://yourapp.com/callback",
  "state": "random-state-string",
  "provider": "google"
}
```

#### POST `/auth/oauth/{provider}/login`
Complete OAuth login with authorization code.

**Parameters:**
- `provider` (string, path): OAuth provider ("google" or "facebook")

**Query Parameters:**
- `code` (string, required): Authorization code from OAuth provider
- `redirect_uri` (string, optional): Redirect URI used in authorization

**Response:**
```json
{
  "access_token": "jwt-token",
  "token_type": "bearer",
  "user_id": "uuid",
  "email": "user@gmail.com",
  "full_name": "John Doe",
  "two_factor_required": false,
  "message": "OAuth login successful"
}
```

#### GET `/auth/oauth/{provider}/callback`
OAuth callback endpoint for registration.

**Parameters:**
- `provider` (string, path): OAuth provider ("google" or "facebook")

**Query Parameters:**
- `code` (string, required): Authorization code
- `state` (string, optional): State parameter
- `error` (string, optional): Error from OAuth provider

**Response:**
```json
{
  "id": "uuid",
  "email": "user@gmail.com",
  "phone_number": null,
  "full_name": "John Doe",
  "profile_picture": "https://...",
  "oauth_provider": "google",
  "status": "active",
  "is_email_verified": true,
  "is_phone_verified": false,
  "created_at": "2024-01-01T00:00:00Z",
  "registration_token": null,
  "message": "OAuth registration successful"
}
```

#### GET `/auth/health`
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "service": "SyriaGPT Authentication Service",
  "email_configured": true,
  "oauth_providers": ["google", "facebook"],
  "database_connected": true,
  "version": "1.0.0"
}
```

### Two-Factor Authentication Endpoints

#### POST `/auth/2fa/setup`
Setup 2FA for the current user.

**Headers:**
- `Authorization: Bearer <token>` (required)

**Response:**
```json
{
  "secret_key": "JBSWY3DPEHPK3PXP",
  "qr_code": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA..."
}
```

#### POST `/auth/2fa/verify`
Verify and enable 2FA.

**Headers:**
- `Authorization: Bearer <token>` (required)

**Request Body:**
```json
{
  "code": "123456"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "2FA has been enabled successfully."
}
```

#### POST `/auth/2fa/disable`
Disable 2FA for the current user.

**Headers:**
- `Authorization: Bearer <token>` (required)

**Response:**
```json
{
  "status": "success",
  "message": "2FA has been disabled."
}
```

### Test Endpoints

#### POST `/auth/test/generate-token`
Generate a test JWT token for development/testing.

**Response:**
```json
{
  "access_token": "test-jwt-token",
  "token_type": "bearer",
  "expires_in": 3600,
  "usage": "Copy the access_token above, click 'Authorize' in Swagger UI, and paste: Bearer YOUR_ACCESS_TOKEN"
}
```

### Session Management Endpoints

#### GET `/sessions/`
Get all sessions for the current user.

**Headers:**
- `Authorization: Bearer <token>` (required)

**Response:**
```json
{
  "sessions": [
    {
      "id": "session-uuid",
      "device_info": "Chrome on Windows",
      "ip_address": "192.168.1.1",
      "user_agent": "Mozilla/5.0...",
      "location": "New York, US",
      "is_active": true,
      "is_mobile": false,
      "last_activity_at": "2024-01-01T12:00:00Z"
    }
  ],
  "total_sessions": 1,
  "active_sessions": 1
}
```

#### POST `/sessions/logout`
Logout from specific session or all sessions.

**Headers:**
- `Authorization: Bearer <token>` (required)

**Request Body:**
```json
{
  "session_id": "session-uuid",
  "logout_all": false
}
```

**Response:**
```json
{
  "message": "Successfully logged out from 1 session(s)",
  "logged_out_sessions": 1
}
```

#### POST `/sessions/refresh`
Refresh access token using refresh token.

**Request Body:**
```json
{
  "refresh_token": "refresh-token-string"
}
```

**Response:**
```json
{
  "access_token": "new-jwt-token",
  "token_type": "bearer",
  "expires_in": 1800
}
```

#### DELETE `/sessions/cleanup`
Clean up expired sessions (admin endpoint).

**Response:**
```json
{
  "message": "Successfully cleaned up 5 expired sessions",
  "cleaned_sessions": 5
}
```

#### GET `/sessions/current`
Get current session information.

**Headers:**
- `Authorization: Bearer <token>` (required)

**Response:**
```json
{
  "user_id": "user-uuid",
  "email": "user@example.com",
  "message": "Current session information - session tracking via JWT tokens"
}
```

## Data Models

### Request Models

#### UserRegistrationRequest
```python
{
  "email": "string (email)",
  "password": "string (min_length=8)",
  "phone_number": "string (optional, phone format)",
  "first_name": "string (optional, max_length=100)",
  "last_name": "string (optional, max_length=100)"
}
```

#### UserLoginRequest
```python
{
  "email": "string (email)",
  "password": "string",
  "remember_me": "boolean (optional, default=false)",
  "two_factor_code": "string (optional)"
}
```

#### ForgotPasswordRequest
```python
{
  "email": "string (email)"
}
```

#### ResetPasswordRequest
```python
{
  "token": "string",
  "new_password": "string",
  "confirm_password": "string"
}
```

#### TwoFactorVerifyRequest
```python
{
  "code": "string (length=6)"
}
```

#### OAuthAuthorizationRequest
```python
{
  "provider": "string (google|facebook)",
  "redirect_uri": "string (optional)"
}
```

#### SocialLoginRequest
```python
{
  "provider": "string (google|facebook)",
  "code": "string",
  "redirect_uri": "string (optional)"
}
```

### Response Models

#### UserRegistrationResponse
```python
{
  "id": "string (uuid)",
  "email": "string",
  "phone_number": "string (optional)",
  "full_name": "string (optional)",
  "profile_picture": "string (optional)",
  "oauth_provider": "string (optional)",
  "status": "string",
  "is_email_verified": "boolean",
  "is_phone_verified": "boolean",
  "created_at": "datetime",
  "registration_token": "string (optional)",
  "message": "string"
}
```

#### LoginResponse
```python
{
  "access_token": "string",
  "token_type": "string (default: bearer)",
  "user_id": "string (uuid)",
  "email": "string",
  "full_name": "string (optional)",
  "two_factor_required": "boolean (default: false)",
  "message": "string (optional)"
}
```

#### EmailVerificationResponse
```python
{
  "message": "string",
  "verified": "boolean",
  "user_id": "string (uuid)",
  "email": "string"
}
```

#### OAuthProvidersResponse
```python
{
  "providers": "array of strings",
  "configured_providers": "object"
}
```

#### OAuthAuthorizationResponse
```python
{
  "authorization_url": "string",
  "redirect_uri": "string",
  "state": "string",
  "provider": "string"
}
```

#### HealthResponse
```python
{
  "status": "string",
  "service": "string",
  "email_configured": "boolean",
  "oauth_providers": "array of strings",
  "database_connected": "boolean",
  "version": "string"
}
```

#### TwoFactorSetupResponse
```python
{
  "secret_key": "string",
  "qr_code": "string (base64 encoded image)"
}
```

#### GeneralResponse
```python
{
  "status": "string",
  "message": "string"
}
```

#### ErrorResponse
```python
{
  "error": "string",
  "message": "string",
  "details": "object (optional)",
  "status_code": "integer"
}
```

## Error Handling

The API uses standard HTTP status codes and returns detailed error messages in Arabic and English.

### Common Error Codes

- **400 Bad Request**: Invalid request data
- **401 Unauthorized**: Authentication required or invalid credentials
- **403 Forbidden**: Insufficient permissions
- **404 Not Found**: Resource not found
- **422 Unprocessable Entity**: Validation errors
- **500 Internal Server Error**: Server error

### Error Response Format
```json
{
  "error": "VALIDATION_ERROR",
  "message": "Invalid email format",
  "details": {
    "field": "email",
    "value": "invalid-email"
  },
  "status_code": 422
}
```

## Configuration

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `DATABASE_URL` | PostgreSQL connection string | Yes | - |
| `POSTGRES_USER` | PostgreSQL username | No | admin |
| `POSTGRES_PASSWORD` | PostgreSQL password | No | admin123 |
| `POSTGRES_DB` | PostgreSQL database name | No | syriagpt |
| `SECRET_KEY` | JWT secret key | Yes | - |
| `ALGORITHM` | JWT algorithm | No | HS256 |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Access token expiry | No | 30 |
| `SMTP_HOST` | SMTP server host | Yes | - |
| `SMTP_PORT` | SMTP server port | No | 587 |
| `SMTP_USERNAME` | SMTP username | Yes | - |
| `SMTP_PASSWORD` | SMTP password | Yes | - |
| `EMAIL_FROM` | From email address | No | noreply@syriagpt.com |
| `EMAIL_FROM_NAME` | From email name | No | Syria GPT |
| `GOOGLE_CLIENT_ID` | Google OAuth client ID | No | - |
| `GOOGLE_CLIENT_SECRET` | Google OAuth client secret | No | - |
| `FACEBOOK_CLIENT_ID` | Facebook OAuth client ID | No | - |
| `FACEBOOK_CLIENT_SECRET` | Facebook OAuth client secret | No | - |
| `FRONTEND_URL` | Frontend application URL | No | http://localhost:3000 |
| `BACKEND_URL` | Backend application URL | No | http://localhost:9000 |
| `LOG_LEVEL` | Logging level | No | INFO |
| `PGADMIN_EMAIL` | PgAdmin email | No | admin@admin.com |
| `PGADMIN_PASSWORD` | PgAdmin password | No | admin123 |

### Database Schema

The application uses PostgreSQL with the following main tables:

- **users**: User accounts and profiles
- **sessions**: User session management
- **verification_tokens**: Email verification and password reset tokens

### Security Features

- **Password Strength Validation**: Enforces strong password requirements
- **JWT Token Security**: Secure token generation and validation
- **Session Management**: Multi-device session tracking
- **Rate Limiting**: Protection against brute force attacks
- **Input Validation**: Comprehensive request validation
- **SQL Injection Protection**: Parameterized queries
- **Connection Pooling**: Optimized database connections
- **Structured Logging**: Comprehensive audit trail

## Development

### Running Tests
```bash
# Run tests (if test suite is implemented)
pytest

# Run with coverage
pytest --cov=app
```

### Code Quality
```bash
# Run linting
flake8

# Run type checking
mypy .
```

### Database Migrations
```bash
# Create new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

### Logging

The application uses structured logging with the following features:

- **Console Output**: Real-time logging to console
- **File Rotation**: Automatic log file rotation (10MB max, 5 backups)
- **Multiple Levels**: DEBUG, INFO, WARNING, ERROR, CRITICAL
- **JSON Format**: Optional JSON formatting for production
- **SQL Query Logging**: Configurable SQL query logging

### Monitoring

- **Health Checks**: Application and database health monitoring
- **Metrics**: Request/response metrics (can be extended)
- **Error Tracking**: Comprehensive error logging and tracking

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions, please contact the development team or create an issue in the repository.
