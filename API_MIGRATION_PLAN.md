# Flask to API + React Frontend Migration Plan

## Overview
Transform the existing Flask app into a pure REST API backend and create a separate React frontend with modern authentication (Passkeys/WebAuthn).

## Phase 1: Flask API Backend ✅

### 1. API Endpoints Created

#### Authentication API (`/auth/api/`)
- `POST /auth/api/login` - User login
- `POST /auth/api/logout` - User logout
- `POST /auth/api/register` - User registration
- `GET /auth/api/me` - Get current user info
- `GET /auth/api/parent-code/<code>` - Validate parent code

#### Parent API (`/parent/api/`)
- `GET /parent/api/dashboard` - Parent dashboard data
- `GET /parent/api/children` - List all children
- `GET /parent/api/children/<id>` - Get specific child
- `DELETE /parent/api/children/<id>` - Remove child
- `GET /parent/api/profile` - Get parent profile
- `PUT /parent/api/profile` - Update parent profile

#### Child API (`/child/api/`)
- `GET /child/api/dashboard` - Child dashboard data
- `GET /child/api/profile` - Get child profile
- `PUT /child/api/profile` - Update child profile
- `GET /child/api/parent` - Get parent info

### 2. API Features
- ✅ JSON request/response format
- ✅ Proper HTTP status codes
- ✅ Error handling with consistent format
- ✅ CORS enabled for React frontend
- ✅ Session-based authentication (can be upgraded to JWT later)

## Phase 2: React Frontend Setup

### 1. Create New Repository
```bash
# Create new React app repository
npx create-react-app family-point-system-frontend
cd family-point-system-frontend

# Install additional dependencies
npm install axios react-router-dom @heroicons/react
npm install @simplewebauthn/browser  # For Passkeys/WebAuthn
```

### 2. Project Structure
```
family-point-system-frontend/
├── public/
├── src/
│   ├── components/
│   │   ├── auth/
│   │   │   ├── LoginForm.js
│   │   │   ├── RegisterForm.js
│   │   │   └── PasskeyAuth.js
│   │   ├── parent/
│   │   │   ├── Dashboard.js
│   │   │   ├── ChildrenList.js
│   │   │   └── Profile.js
│   │   ├── child/
│   │   │   ├── Dashboard.js
│   │   │   └── Profile.js
│   │   └── common/
│   │       ├── Header.js
│   │       ├── Navigation.js
│   │       └── ProtectedRoute.js
│   ├── services/
│   │   ├── api.js
│   │   ├── auth.js
│   │   └── webauthn.js
│   ├── hooks/
│   │   ├── useAuth.js
│   │   └── useApi.js
│   ├── context/
│   │   └── AuthContext.js
│   ├── utils/
│   │   └── constants.js
│   └── App.js
├── package.json
└── README.md
```

### 3. Authentication Strategy

#### Primary: Passkeys (WebAuthn)
- Modern, secure, passwordless authentication
- Better UX - no passwords to remember
- Phishing resistant
- Works with biometrics, security keys, etc.

#### Fallback: Email/Password + OTP
- Traditional email/password for legacy support
- Optional email OTP for additional security
- Graceful degradation for unsupported browsers

## Phase 3: Implementation Steps

### Backend (Current Repository)
1. ✅ Create API routes
2. ✅ Add CORS support
3. ✅ Update error handling
4. 🔄 Add WebAuthn endpoints (next step)
5. 🔄 Add JWT token support (optional upgrade)

### Frontend (New Repository)
1. 🔄 Set up React app structure
2. 🔄 Implement authentication context
3. 🔄 Create API service layer
4. 🔄 Build authentication components
5. 🔄 Implement Passkey authentication
6. 🔄 Create dashboard components
7. 🔄 Add routing and navigation

## Phase 4: WebAuthn/Passkey Implementation

### Backend Extensions Needed
```python
# Add to pyproject.toml
webauthn = "^1.11.1"

# New endpoints to add:
POST /auth/api/webauthn/register/begin
POST /auth/api/webauthn/register/complete
POST /auth/api/webauthn/authenticate/begin
POST /auth/api/webauthn/authenticate/complete
```

### Frontend WebAuthn Flow
1. Check browser support
2. Show "Sign in with Passkey" if supported
3. Fall back to email/password if not supported
4. Progressive enhancement approach

## Phase 5: Deployment Strategy

### Backend (API)
- Deploy to Heroku, Railway, or similar
- Environment variables for production config
- Database migrations

### Frontend
- Deploy to Vercel, Netlify, or similar
- Environment variables for API endpoints
- CI/CD pipeline

## Next Steps

1. **Install Flask-CORS**: `poetry add flask-cors`
2. **Test API endpoints** with Postman or curl
3. **Create React repository** on GitHub
4. **Implement basic authentication flow**
5. **Add WebAuthn support**

## API Testing Commands

```bash
# Test login
curl -X POST http://localhost:5000/auth/api/login \
  -H "Content-Type: application/json" \
  -d '{"email": "parent@example.com", "password": "password123"}'

# Test registration
curl -X POST http://localhost:5000/auth/api/register \
  -H "Content-Type: application/json" \
  -d '{"username": "testparent", "email": "test@example.com", "password": "password123", "role": "parent"}'

# Test parent dashboard
curl -X GET http://localhost:5000/parent/api/dashboard \
  -H "Content-Type: application/json" \
  --cookie-jar cookies.txt --cookie cookies.txt
```
