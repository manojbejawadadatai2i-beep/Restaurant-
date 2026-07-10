# Login Endpoints Documentation

This document describes the API endpoints used for user authentication in the Restaurant Management System.

## Base Path: `/auth`

---

### 1. Standard Login
**Endpoint**: `POST /auth/login`
**Description**: Authenticates a user using their email and password and returns a JWT access token.

**Request**:
- Content-Type: `application/x-www-form-urlencoded`
- Body Parameters:
  - `username` (string, required): The user's email address.
  - `password` (string, required): The user's password.

**Response (Success - 200 OK)**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1...",
  "token_type": "bearer"
}
```

**Responses (Error)**:
- `401 Unauthorized`: "Incorrect email or password"

---

### 2. Google OAuth Login
**Endpoint**: `POST /auth/google`
**Description**: Authenticates a user via Google OAuth using an ID token and returns a JWT access token.

**Request**:
- Content-Type: `application/json`
- Body:
```json
{
  "id_token": "string"
}
```

**Response (Success - 200 OK)**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1...",
  "token_type": "bearer"
}
```

**Responses (Error)**:
- `400 Bad Request`: "Failed to verify Google Token: {error}" or "Google account email is not verified or could not be retrieved"
- `401 Unauthorized`: "User with email '{email}' is not registered in the system database."
