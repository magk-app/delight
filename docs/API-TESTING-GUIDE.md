# API Testing Guide - Story 1.3

## Testing Protected Endpoints

The `/api/v1/users/me` endpoint requires authentication via Clerk session token.

### Method 1: Get Token from Browser (Recommended for Testing)

#### Step 1: Sign In to Frontend

1. Start frontend:
   ```bash
   cd C:\Users\Jack Luo\Desktop\(local) github software\delight\packages\frontend
   npm run dev
   ```

2. Open http://localhost:3000
3. Sign in with your test account

#### Step 2: Extract Session Token

**Option A: From DevTools (Chrome/Edge)**

1. Open DevTools (F12)
2. Go to **Application** tab
3. Expand **Cookies** → `http://localhost:3000`
4. Find `__session` cookie
5. Copy the **Value** (this is your session token)

**Option B: From Network Tab**

1. Stay signed in
2. Open DevTools (F12) → **Network** tab
3. Make any request to the backend (or refresh page)
4. Click on any request
5. Look at **Request Headers**
6. Find `Authorization: Bearer <token>`
7. Copy everything after "Bearer " (that's your token)

#### Step 3: Test with curl (Windows Command Prompt)

```bash
# Replace YOUR_TOKEN_HERE with the actual token from step 2
curl -H "Authorization: Bearer YOUR_TOKEN_HERE" http://localhost:8000/api/v1/users/me
```

**Expected Response:**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "clerk_user_id": "user_2abcdef1234567890",
  "email": "test@example.com",
  "display_name": "Test User",
  "timezone": "UTC",
  "created_at": "2025-11-11T12:00:00",
  "updated_at": "2025-11-11T12:00:00"
}
```

#### Step 4: Test Error Cases

**Without Authorization header (403 Forbidden):**
```bash
curl http://localhost:8000/api/v1/users/me
```
Expected: `{"detail": "Not authenticated"}`

**With invalid token (401 Unauthorized):**
```bash
curl -H "Authorization: Bearer invalid_token_12345" http://localhost:8000/api/v1/users/me
```
Expected: `{"detail": "Invalid token"}`

### Method 2: Using Postman

1. Download Postman from https://www.postman.com/downloads/
2. Create new request:
   - Method: `GET`
   - URL: `http://localhost:8000/api/v1/users/me`
3. Go to **Authorization** tab
4. Type: "Bearer Token"
5. Token: Paste your session token from browser
6. Click "Send"

### Method 3: Using Thunder Client (VS Code Extension)

1. Install "Thunder Client" extension in VS Code
2. Create new request:
   - Method: `GET`
   - URL: `http://localhost:8000/api/v1/users/me`
3. Headers tab:
   - Add header: `Authorization`
   - Value: `Bearer YOUR_TOKEN_HERE`
4. Click "Send"

## Testing Swagger UI

Your backend has built-in API docs with authentication:

1. Go to http://localhost:8000/docs
2. Click the **"Authorize"** button (top right)
3. Paste your token (without "Bearer " prefix)
4. Click "Authorize"
5. Now you can test endpoints directly from the UI

## Quick Test Script

Save this as `test-api.bat` in your backend folder:

```batch
@echo off
echo Testing Delight API Authentication
echo.
echo 1. Testing without auth (should get 403):
curl http://localhost:8000/api/v1/users/me
echo.
echo.
echo 2. Testing with auth (replace TOKEN below):
set /p TOKEN="Enter your session token: "
curl -H "Authorization: Bearer %TOKEN%" http://localhost:8000/api/v1/users/me
echo.
pause
```

Run: `test-api.bat`

## Understanding the 403 Errors in Your Logs

The logs you posted:
```
INFO:     127.0.0.1:65119 - "GET /api/v1/users/me HTTP/1.1" 403 Forbidden
INFO:     127.0.0.1:57371 - "GET /api/v1/users/me HTTP/1.1" 403 Forbidden
```

These are **CORRECT behavior** - you made requests without Authorization headers.

The endpoint is working properly by rejecting unauthenticated requests!

## Troubleshooting

### "Invalid token" with valid-looking token

**Issue**: Token might be expired or malformed

**Solution**:
1. Sign out and sign in again to get fresh token
2. Make sure you copied the ENTIRE token (they can be very long, 500+ characters)
3. Make sure no extra spaces before/after the token

### Token works in browser but not curl

**Issue**: Token includes special characters that need escaping in Windows CMD

**Solution**: Use PowerShell instead of CMD, or wrap token in quotes:
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:8000/api/v1/users/me
```

### Can't find __session cookie

**Issue**: Not signed in, or cookies not being set

**Solution**:
1. Make sure you're signed in (see user menu in top-right)
2. Check browser console for errors
3. Make sure frontend is running on localhost:3000 (not a different port)

## Expected Request Flow

```
Frontend (localhost:3000)
  ↓ User signs in via Clerk
  ↓ Clerk sets __session cookie
  ↓
Frontend makes API request
  ↓ Includes: Authorization: Bearer <token>
  ↓
Backend (localhost:8000)
  ↓ Extracts token from header
  ↓ Validates with Clerk
  ↓ Queries Supabase for user
  ↓
Returns user data (200 OK)
```

## Testing Checklist

- [ ] Backend running on localhost:8000
- [ ] Frontend running on localhost:3000
- [ ] Signed in to frontend successfully
- [ ] Can extract session token from browser cookies
- [ ] curl with token returns 200 + user data
- [ ] curl without token returns 403
- [ ] curl with invalid token returns 401
- [ ] Swagger UI authentication works
