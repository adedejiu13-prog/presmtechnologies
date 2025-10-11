# Shopify App Setup Guide for PRESM DTF

This guide explains the Shopify App integration setup that has been configured for your PRESM DTF application.

## What Has Been Configured

### 1. Backend Shopify OAuth Support
- **New Route**: `/api/auth/shopify` - Handles Shopify OAuth flow
  - `/install` - Initiates OAuth authorization
  - `/callback` - Handles OAuth callback and stores access token
  - `/verify` - Verifies current Shopify session
  - `/logout` - Clears Shopify session

### 2. Environment Variables
Two `.env.example` files have been created:

**Backend** (`backend/.env.example`):
- `SHOPIFY_API_KEY` - Your Shopify App API key
- `SHOPIFY_API_SECRET` - Your Shopify App secret
- `SHOPIFY_SCOPES` - Requested permissions
- `SHOPIFY_WEBHOOK_SECRET` - For webhook verification
- `MONGO_URL` - MongoDB connection string
- `DB_NAME` - Database name

**Frontend** (`frontend/.env.example`):
- `REACT_APP_BACKEND_URL` - Backend API URL
- `REACT_APP_SHOPIFY_API_KEY` - Shopify API key for frontend

### 3. Frontend Shopify Integration
**New Hooks**:
- `useShopifyAuth` - Hook for managing Shopify authentication
- `ShopifyAuthContext` - React context for auth state

### 4. Shopify CLI Configuration
- `shopify.toml` - Configuration file for Shopify CLI deployment
  - Configured for Replit deployment
  - Includes webhook subscriptions
  - Sets up OAuth redirect URLs

### 5. Build Configuration
- Updated `start.sh` to:
  - Build React frontend for production
  - Serve both frontend and backend on port 5000
  - Use Replit environment variables for public URL

## Next Steps

### 1. Set Up Shopify Partner Account
1. Go to [Shopify Partners](https://partners.shopify.com/)
2. Create a new app
3. Get your API Key and API Secret

### 2. Configure Environment Variables  
Create a `backend/.env` file with your actual credentials:
```bash
SHOPIFY_API_KEY=your_actual_api_key
SHOPIFY_API_SECRET=your_actual_api_secret
SHOPIFY_SCOPES=read_products,write_products,read_orders,write_orders,read_customers
MONGO_URL=your_mongodb_connection_string
DB_NAME=presm_dtf
```

### 3. Set Up Database
You have two options:

**Option A: Use Replit's Built-in PostgreSQL**
- Click "Database" in the left sidebar
- Create a new PostgreSQL database
- Update backend to use PostgreSQL instead of MongoDB

**Option B: Use External MongoDB**
- Sign up for [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
- Create a free cluster
- Get your connection string
- Add it to `backend/.env` as `MONGO_URL`

### 4. Update Shopify App Settings
In your Shopify Partner dashboard:
1. Set App URL to: `https://[your-repl-name].[your-username].repl.co`
2. Set Allowed redirection URLs to: `https://[your-repl-name].[your-username].repl.co/api/auth/shopify/callback`
3. Set webhook URLs based on `shopify.toml`

### 5. Install & Test
1. Restart your Replit app
2. Visit: `https://[your-repl-name].[your-username].repl.co/api/auth/shopify/install?shop=your-test-store`
3. Complete OAuth flow
4. App should be installed in your test Shopify store

## File Structure

```
├── backend/
│   ├── routes/
│   │   ├── auth.py           # NEW: Shopify OAuth routes
│   │   ├── shopify.py         # Existing: Shopify webhooks
│   │   └── ...
│   ├── .env.example           # NEW: Environment variables template
│   ├── .env                   # NEW: Your actual environment variables
│   └── server.py              # UPDATED: Serves React build files
├── frontend/
│   ├── src/
│   │   ├── hooks/
│   │   │   └── useShopifyAuth.js  # NEW: Shopify auth hook
│   │   ├── context/
│   │   │   └── ShopifyAuthContext.js  # NEW: Auth context
│   │   └── ...
│   └── .env.example           # NEW: Frontend env template
├── shopify.toml               # NEW: Shopify CLI config
└── start.sh                   # UPDATED: Production build script
```

## API Endpoints

### Authentication
- `GET /api/auth/shopify/install?shop={shop_name}` - Start OAuth
- `GET /api/auth/shopify/callback` - OAuth callback
- `GET /api/auth/shopify/verify` - Check auth status
- `POST /api/auth/shopify/logout` - Clear session

### Existing Endpoints
- `GET /api/products` - Get all products
- `POST /api/cart/items` - Add to cart
- `POST /api/shopify/webhooks/order/created` - Order webhook
- And all other existing endpoints...

## Deployment

### Using Shopify CLI
```bash
shopify app deploy
```

### Manual Deployment
The app is configured to run on Replit with:
- Frontend: Built to `frontend/build/`
- Backend: Serves both API and static files on port 5000

## Troubleshooting

### Database Connection Issues
If you see MongoDB connection errors:
1. Make sure `MONGO_URL` is set in `backend/.env`
2. Or set up Replit's PostgreSQL database
3. The app will run in limited mode without database (Shopify auth will still work)

### OAuth Redirect Issues
Make sure your redirect URI in Shopify matches exactly:
```
https://[your-repl-name].[your-username].repl.co/api/auth/shopify/callback
```

### Environment Variables
The app uses Replit's automatic environment variables:
- `REPL_SLUG` - Your repl name
- `REPL_OWNER` - Your username
- These are used to construct the public URL automatically

## Security Notes

### ⚠️ CRITICAL: Production Session Storage

The current OAuth implementation uses **in-memory session storage** which is suitable for development/testing but **MUST be replaced for production**. 

See `SECURITY.md` for detailed instructions on implementing Redis or database-backed session storage.

### Security Features

1. ✅ CSRF Protection - State token validation
2. ✅ Secure Token Storage - Server-side storage (not in cookies)
3. ✅ HMAC Verification - Always enforced
4. ✅ Secure Cookies - HttpOnly, Secure, SameSite
5. ⚠️ Session Persistence - In-memory (MUST upgrade for production)

### Best Practices

1. Never commit `.env` files to Git
2. Always use HTTPS in production (automatic on Replit)
3. Set `SHOPIFY_API_SECRET` before enabling OAuth
4. Implement Redis or database session storage before production deployment
5. Review `SECURITY.md` for complete security guidelines

## Resources

- [Shopify App Documentation](https://shopify.dev/docs/apps)
- [Shopify Python SDK](https://github.com/Shopify/shopify_python_api)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
