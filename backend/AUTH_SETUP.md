# Authentication System Setup Guide

## Overview

The authentication system has been completely rebuilt with:
- ✅ JWT token-based authentication
- ✅ Bcrypt password hashing
- ✅ SQLite database storage
- ✅ Proper error handling and logging

## Endpoints

### 1. POST `/auth/signup`
Register a new user.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response (201):**
```json
{
  "success": true,
  "user": {
    "id": 1,
    "email": "user@example.com",
    "created_at": "2024-01-01T00:00:00"
  }
}
```

**Error (400):**
```json
{
  "error": "Email already registered"
}
```

### 2. POST `/auth/login`
Login with email and password.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response (200):**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "created_at": "2024-01-01T00:00:00"
  }
}
```

**Error (401):**
```json
{
  "error": "Invalid credentials"
}
```

### 3. GET `/auth/me`
Get current authenticated user information.

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200):**
```json
{
  "id": 1,
  "email": "user@example.com",
  "created_at": "2024-01-01T00:00:00"
}
```

**Error (401):**
```json
{
  "error": "Invalid token"
}
```

## Installation

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Set environment variables** (create `.env` file):
```env
OPENAI_API_KEY=your_openai_key
SECRET_KEY=your-secret-key-for-jwt-min-32-chars
DATABASE_URL=sqlite:///./aidesk.db
```

3. **Start the server:**
```bash
uvicorn main:app --reload --port 8000
```

The database (`aidesk.db`) will be created automatically on first run.

## Testing with cURL

### Signup
```bash
curl -X POST http://localhost:8000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "password123"}'
```

### Login
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "password123"}'
```

### Get Current User
```bash
curl -X GET http://localhost:8000/auth/me \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

## Frontend Integration

### Signup Example
```typescript
const response = await fetch('http://localhost:8000/auth/signup', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: 'user@example.com',
    password: 'password123'
  })
});

const data = await response.json();
if (data.success) {
  console.log('User created:', data.user);
}
```

### Login Example
```typescript
const response = await fetch('http://localhost:8000/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: 'user@example.com',
    password: 'password123'
  })
});

const data = await response.json();
if (data.token) {
  localStorage.setItem('token', data.token);
  console.log('Logged in:', data.user);
}
```

### Authenticated Request Example
```typescript
const token = localStorage.getItem('token');
const response = await fetch('http://localhost:8000/auth/me', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});

const user = await response.json();
console.log('Current user:', user);
```

## Security Features

1. **Password Hashing**: Uses bcrypt with automatic salt generation
2. **JWT Tokens**: Secure token-based authentication
3. **Token Expiration**: Tokens expire after 30 minutes (configurable)
4. **Email Validation**: Email format validation using Pydantic
5. **Password Requirements**: Minimum 8 characters
6. **Error Logging**: Comprehensive logging for debugging

## Database Schema

The `users` table is automatically created with:
- `id` (Integer, Primary Key)
- `email` (String, Unique, Indexed)
- `password_hash` (String)
- `created_at` (DateTime)

## Error Handling

All endpoints return clean error messages:
- `400 Bad Request`: Invalid input (email already exists, password too short)
- `401 Unauthorized`: Invalid credentials or expired token
- `500 Internal Server Error`: Server errors (logged for debugging)

## CORS Configuration

The API allows requests from:
- `http://localhost:3000` (development)
- `http://127.0.0.1:3000` (development)
- Any Vercel domain (if `NEXT_PUBLIC_SITE_URL` is set)
- Custom origins via `CORS_ORIGINS` environment variable

In development mode, all origins are allowed. In production, only specific origins are allowed.

## Troubleshooting

### "Database not initialized"
- The database is created automatically on first request
- Check that SQLite has write permissions in the backend directory

### "Invalid token"
- Token may have expired (default: 30 minutes)
- Check that `SECRET_KEY` matches between token creation and validation
- Ensure token is sent in `Authorization: Bearer <token>` header

### "Email already registered"
- User already exists in database
- Use login endpoint instead

### "Invalid credentials"
- Email or password is incorrect
- Check that password matches the one used during signup

