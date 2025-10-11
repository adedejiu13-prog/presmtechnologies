# Security Considerations

## Shopify OAuth Implementation

### Security Features Implemented

1. **CSRF Protection**
   - Uses cryptographically secure state tokens (`secrets.token_urlsafe(32)`)
   - State tokens stored server-side and validated in callback
   - Prevents cross-site request forgery attacks

2. **Secure Token Storage**
   - Access tokens stored server-side, NOT in client cookies
   - Only session ID sent to client in secure, HttpOnly cookie
   - Prevents token leakage through XSS attacks

3. **HMAC Verification**
   - Always enforces HMAC signature verification
   - Requires `SHOPIFY_API_SECRET` to be configured
   - Rejects all requests with invalid signatures

4. **Secure Session Management**
   - HttpOnly cookies prevent JavaScript access
   - Secure flag ensures HTTPS-only transmission
   - SameSite=Lax prevents CSRF
   - 30-day session expiration

### Important Production Notes

#### 🚨 Session Store (CRITICAL)

The current implementation uses **in-memory session storage** which is suitable for development but **NOT for production**.

**Current implementation:**
```python
# In-memory session store - DEVELOPMENT ONLY
oauth_states: Dict[str, str] = {}
shop_sessions: Dict[str, str] = {}
```

**For production, you MUST use a persistent session store:**

**Option 1: Redis (Recommended)**
```python
import redis
redis_client = redis.Redis(host='localhost', port=6379, db=0)

# Store session
redis_client.setex(
    f"session:{session_id}", 
    2592000,  # 30 days
    json.dumps(session_data)
)

# Retrieve session
session_data = json.loads(redis_client.get(f"session:{session_id}"))
```

**Option 2: Database**
- Create a `sessions` table in your database
- Store session_id, shop, access_token, created_at, expires_at
- Implement cleanup for expired sessions

**Why in-memory storage is dangerous in production:**
- Lost on server restart (users logged out)
- Not shared across multiple server instances
- Memory leaks if sessions aren't cleaned up
- No persistence or backup

### Environment Variables Security

**Required environment variables:**
```bash
SHOPIFY_API_KEY=your_key_here          # Public, can be exposed
SHOPIFY_API_SECRET=your_secret_here    # SECRET - Never expose!
SHOPIFY_WEBHOOK_SECRET=your_secret     # SECRET - For webhook verification
```

**Best practices:**
1. Never commit `.env` files to version control
2. Use Replit Secrets for environment variables
3. Rotate secrets regularly
4. Use different secrets for dev/staging/production

### API Security

#### Authentication
All Shopify-authenticated endpoints should check for valid session:

```python
def get_current_shop(request: Request) -> dict:
    session_id = request.cookies.get("shopify_session_id")
    if not session_id or session_id not in shop_sessions:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return shop_sessions[session_id]

@router.get("/protected-endpoint")
async def protected_route(shop_data: dict = Depends(get_current_shop)):
    # shop_data contains shop and access_token
    # Endpoint only accessible to authenticated Shopify stores
    pass
```

#### Webhook Verification
Already implemented in `routes/shopify.py`:
```python
def verify_shopify_webhook(data: bytes, signature: str) -> bool:
    expected_signature = base64.b64encode(
        hmac.new(
            SHOPIFY_WEBHOOK_SECRET.encode('utf-8'),
            data,
            digestmod=hashlib.sha256
        ).digest()
    ).decode('utf-8')
    return hmac.compare_digest(expected_signature, signature)
```

### HTTPS Requirements

**Production deployments MUST use HTTPS:**
- Shopify requires HTTPS for OAuth redirects
- Cookies with `secure=True` only work over HTTPS
- Protects tokens and session data in transit

Replit provides HTTPS automatically for all deployments.

### Rate Limiting

**TODO: Implement rate limiting**

Recommended implementation:
```python
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter

# Limit OAuth endpoints
@router.get("/install", dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def install_app(shop: str = None):
    ...
```

### Common Vulnerabilities Addressed

| Vulnerability | Status | Protection |
|--------------|--------|------------|
| CSRF | ✅ Fixed | State token validation |
| XSS token theft | ✅ Fixed | HttpOnly cookies, server-side storage |
| MITM attacks | ✅ Fixed | HTTPS enforcement |
| Replay attacks | ✅ Fixed | One-time state tokens |
| HMAC bypass | ✅ Fixed | Always enforces verification |
| Session hijacking | ⚠️ Partial | Secure cookies (add IP/UA validation) |
| Privilege escalation | ✅ Fixed | Each shop has isolated session |

### Recommendations for Production

1. **✅ MUST DO - Session Storage**
   - Replace in-memory storage with Redis or database
   - Implement session expiration and cleanup

2. **✅ MUST DO - Secret Management**
   - Use environment variables, never hardcode
   - Rotate secrets regularly
   - Different secrets for each environment

3. **🔒 SHOULD DO - Enhanced Security**
   - Add rate limiting to OAuth endpoints
   - Implement IP-based session validation
   - Add User-Agent validation for sessions
   - Enable audit logging for OAuth events

4. **📊 SHOULD DO - Monitoring**
   - Log failed HMAC verifications
   - Alert on suspicious OAuth patterns
   - Monitor session creation rates

5. **🧪 COULD DO - Additional Hardening**
   - Implement session rotation
   - Add 2FA for admin operations
   - Enable Content Security Policy headers
   - Add HSTS headers

### Security Checklist for Deployment

- [ ] Replace in-memory session storage with Redis/Database
- [ ] Set all environment variables in production
- [ ] Enable HTTPS (automatic on Replit)
- [ ] Review and rotate all secrets
- [ ] Test OAuth flow end-to-end
- [ ] Verify HMAC verification is working
- [ ] Test session expiration
- [ ] Add rate limiting
- [ ] Enable security headers
- [ ] Set up monitoring and alerts
- [ ] Document incident response plan

### Reporting Security Issues

If you discover a security vulnerability, please:
1. Do NOT create a public GitHub issue
2. Email security contact privately
3. Include detailed reproduction steps
4. Allow time for fix before disclosure

## Additional Resources

- [Shopify OAuth Documentation](https://shopify.dev/docs/apps/auth/oauth)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
