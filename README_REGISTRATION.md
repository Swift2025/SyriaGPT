# Syria GPT Registration API

## US-005 Implementation: New Registration (Sign Up)

### Overview
Complete implementation of user registration with email and OAuth social media authentication following clean architecture principles.

### Features Implemented ✅

#### 1. Email Registration
- **Endpoint**: `POST /auth/register`
- Email validation with Pydantic EmailStr
- Strong password requirements (8+ chars, uppercase, lowercase, numbers, symbols)
- Phone number validation (optional)
- Name fields (first_name, last_name)
- Email verification with secure tokens (24-hour expiry)

#### 2. OAuth Social Media Registration
- **Google OAuth**: Complete integration with Google OAuth 2.0
- **Facebook OAuth**: Complete integration with Facebook OAuth 2.0
- **Endpoints**:
  - `GET /auth/oauth/providers` - List available providers
  - `POST /auth/oauth/{provider}/authorize` - Get authorization URL
  - `GET /auth/oauth/{provider}/callback` - Handle OAuth callback

#### 3. Email Verification System
- **Endpoint**: `GET /auth/verify-email/{token}`
- Professional HTML email templates
- Automatic welcome email after verification
- SMTP configuration with Gmail/custom providers

#### 4. Clear Error Messages
- Structured error responses with HTTP status codes
- Field-specific validation errors
- User-friendly error messages
- Detailed error logging

### API Endpoints

#### Registration
```http
POST /auth/register
Content-Type: application/json

{
    "email": "user@example.com",
    "password": "StrongP@ssw0rd",
    "phone_number": "+1234567890",
    "first_name": "John",
    "last_name": "Doe"
}
```

#### OAuth Authorization
```http
POST /auth/oauth/google/authorize
```

#### Email Verification
```http
GET /auth/verify-email/{verification_token}
```

#### Health Check
```http
GET /auth/health
```

### Database Schema

#### Enhanced User Model
- **Core Fields**: id, email, password_hash, phone_number
- **Profile Fields**: first_name, last_name, full_name, profile_picture
- **OAuth Fields**: oauth_provider, oauth_provider_id, oauth_data
- **Verification Fields**: is_email_verified, is_phone_verified, status, token, token_expiry
- **Timestamps**: created_at, updated_at, last_login_at

### Architecture

#### Clean Architecture Layers

1. **Presentation Layer** (`requests/authentication/registeration.py`)
   - FastAPI routers and endpoints
   - Request/Response models
   - HTTP error handling

2. **Business Logic Layer** (`services/`)
   - `RegistrationService`: Core registration logic
   - `AuthService`: Password hashing, token management
   - `EmailService`: Email templates and SMTP
   - `OAuthService`: OAuth provider integration

3. **Data Access Layer** (`services/user_repository.py`)
   - Repository pattern implementation
   - Database operations
   - SQLAlchemy ORM integration

4. **Domain Layer** (`models/user.py`)
   - User entity definition
   - Database schema

### Security Features

#### Password Security
- BCrypt hashing with salt
- Minimum 8 characters
- Complexity requirements (uppercase, lowercase, numbers, symbols)
- Secure password validation

#### Token Security
- Cryptographically secure random tokens
- 24-hour expiry for verification tokens
- JWT tokens for authentication
- Secure token generation with secrets module

#### OAuth Security
- State parameter for CSRF protection
- Secure authorization flow
- Token validation
- Provider-specific security measures

### Configuration

#### Environment Variables
```env
# Database
DATABASE_URL=postgresql+psycopg2://admin:admin123@db:5432/syriagpt

# Authentication
SECRET_KEY=your-super-secret-key-change-in-production-min-32-chars
ACCESS_TOKEN_EXPIRE_MINUTES=30

# OAuth
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
FACEBOOK_CLIENT_ID=your-facebook-client-id
FACEBOOK_CLIENT_SECRET=your-facebook-client-secret

# Email
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
EMAIL_FROM=noreply@syriagpt.com
EMAIL_FROM_NAME=Syria GPT

# URLs
FRONTEND_URL=http://localhost:3000
BACKEND_URL=http://localhost:8000
```

### Dependencies Added
- `authlib==1.3.0` - OAuth 2.0 integration
- `httpx==0.25.2` - HTTP client for OAuth
- `fastapi-users[oauth]==12.1.3` - FastAPI OAuth utilities
- `emails==0.6.0` - Email handling
- `jinja2==3.1.2` - Email templating
- `aiosmtplib==3.0.1` - Async SMTP client
- `python-dotenv==1.0.0` - Environment configuration

### Testing

#### Manual Testing Flow

1. **Email Registration**
   ```bash
   curl -X POST "http://localhost:8000/auth/register" \
   -H "Content-Type: application/json" \
   -d '{
     "email": "test@example.com",
     "password": "StrongP@ssw0rd123!",
     "first_name": "Test",
     "last_name": "User"
   }'
   ```

2. **OAuth Registration**
   ```bash
   curl -X POST "http://localhost:8000/auth/oauth/google/authorize"
   ```

3. **Email Verification**
   ```bash
   curl -X GET "http://localhost:8000/auth/verify-email/{token}"
   ```

### Deployment

#### Database Migration
```bash
# Run migration to create tables
alembic upgrade head
```

#### Docker Setup
The existing Docker configuration supports the registration system. Ensure environment variables are properly configured.

### Error Handling

#### Common Error Responses
- `400 Bad Request` - Invalid input, weak password
- `409 Conflict` - Email/phone already exists
- `500 Internal Server Error` - System errors

#### Example Error Response
```json
{
    "detail": "Email already registered",
    "error": "registration_conflict",
    "status_code": 409
}
```

### OAuth Provider Setup

#### Google OAuth
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create/select project
3. Enable Google+ API
4. Create OAuth 2.0 credentials
5. Add authorized redirect URIs

#### Facebook OAuth
1. Go to [Facebook Developers](https://developers.facebook.com/)
2. Create app
3. Add Facebook Login product
4. Configure OAuth redirect URIs
5. Get App ID and App Secret

### Production Considerations

#### Security
- Use strong SECRET_KEY (minimum 32 characters)
- Enable HTTPS for all OAuth redirects
- Validate all OAuth redirect URIs
- Implement rate limiting
- Add CORS configuration

#### Monitoring
- Log all registration attempts
- Monitor OAuth callback failures
- Track email delivery rates
- Alert on security events

#### Scalability
- Database connection pooling
- Email queue for high volume
- OAuth token caching
- Horizontal scaling support

### Implementation Status

✅ **Complete**: All US-005 acceptance criteria implemented  
✅ **Email Registration**: Full implementation with validation  
✅ **OAuth Integration**: Google and Facebook providers  
✅ **Email Verification**: Professional email system  
✅ **Strong Passwords**: Comprehensive validation  
✅ **Clear Errors**: User-friendly error messages  
✅ **Clean Architecture**: SOLID principles followed  
✅ **Security**: Best practices implemented  
✅ **Documentation**: Complete API documentation