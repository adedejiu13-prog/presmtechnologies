# PRESM DTF Shopify App

## Project Overview
A full-stack web application for PRESM Technologies' Direct-to-Film (DTF) transfer platform, now configured for deployment as a Shopify App.

## Tech Stack
- **Frontend**: React 19, TailwindCSS, shadcn/ui components, React Router
- **Backend**: FastAPI (Python), Motor (async MongoDB driver)
- **Database**: MongoDB (configurable)
- **Shopify Integration**: ShopifyAPI Python SDK v12.7.0

## Project Structure

```
├── backend/                    # FastAPI backend
│   ├── routes/                # API endpoints
│   │   ├── auth.py           # Shopify OAuth routes
│   │   ├── products.py       # Product management
│   │   ├── gang_sheets.py    # Gang sheet builder
│   │   ├── cart.py           # Shopping cart
│   │   └── shopify.py        # Shopify webhooks
│   ├── services/              # Business logic
│   ├── models/                # Data models
│   ├── server.py              # Main app (serves React build in production)
│   └── requirements.txt       # Python dependencies
├── frontend/                   # React frontend
│   ├── src/
│   │   ├── components/        # React components
│   │   ├── pages/             # Page components
│   │   ├── hooks/             # Custom hooks (including useShopifyAuth)
│   │   ├── context/           # React contexts (including ShopifyAuthContext)
│   │   └── services/          # API client
│   └── package.json           # Node dependencies
├── shopify.toml               # Shopify CLI configuration
└── start.sh                   # Production startup script
```

## Key Features

### Core Features
- Product catalog with categories
- Gang sheet builder with drag-and-drop
- Shopping cart with real-time totals
- Responsive design with dark mode

### Shopify Integration
- OAuth authentication flow
- Webhook support for orders
- Secure session management
- API integration ready

## Environment Setup

### Required Environment Variables

**Backend** (create `backend/.env`):
```bash
# MongoDB
MONGO_URL=mongodb://localhost:27017
DB_NAME=presm_dtf

# Shopify
SHOPIFY_API_KEY=your_shopify_api_key
SHOPIFY_API_SECRET=your_shopify_api_secret
SHOPIFY_SCOPES=read_products,write_products,read_orders,write_orders,read_customers
SHOPIFY_WEBHOOK_SECRET=your_webhook_secret
SHOPIFY_API_VERSION=2024-10

# App
ENVIRONMENT=development
APP_SECRET_KEY=your-secret-key
```

**Frontend** (create `frontend/.env`):
```bash
REACT_APP_BACKEND_URL=http://localhost:8081
REACT_APP_SHOPIFY_API_KEY=your_shopify_api_key
```

### Automatic Environment Variables (Replit)
These are automatically available:
- `REPL_SLUG` - Your repl name
- `REPL_OWNER` - Your username

## Development

### Running Locally
```bash
# Backend
cd backend
python3 -m uvicorn server:app --host 0.0.0.0 --port 5000 --reload

# Frontend (separate terminal)
cd frontend
npm start
```

### Production Build
```bash
bash start.sh
```

This script:
1. Builds React frontend to `frontend/build/`
2. Starts FastAPI server on port 5000
3. Serves both API (`/api/*`) and React app (`/*`)

## Deployment

### On Replit
1. Set environment variables in Secrets
2. Click "Run" - uses `start.sh`
3. App will be available at `https://[repl-name].[username].repl.co`

### Shopify App Setup
1. Create app in Shopify Partners dashboard
2. Set App URL to your Replit URL
3. Configure OAuth redirect: `https://[your-url]/api/auth/shopify/callback`
4. Add webhook URLs from `shopify.toml`
5. Install: Visit `/api/auth/shopify/install?shop=your-store.myshopify.com`

## API Endpoints

### Shopify Auth
- `GET /api/auth/shopify/install?shop={shop}` - Start OAuth
- `GET /api/auth/shopify/callback` - OAuth callback  
- `GET /api/auth/shopify/verify` - Verify session
- `POST /api/auth/shopify/logout` - Logout

### Products
- `GET /api/products/` - List products
- `GET /api/products/categories` - Get categories
- `GET /api/products/{id}` - Get product
- `POST /api/products/` - Create product
- `PUT /api/products/{id}` - Update product
- `DELETE /api/products/{id}` - Delete product

### Gang Sheets
- `GET /api/gang-sheets/templates` - Get templates
- `POST /api/gang-sheets/` - Create gang sheet
- `POST /api/gang-sheets/{id}/designs` - Add design
- `POST /api/gang-sheets/{id}/auto-nest` - Auto-nest designs

### Cart
- `GET /api/cart/` - Get cart
- `POST /api/cart/items` - Add item
- `DELETE /api/cart/clear` - Clear cart

### Shopify Webhooks
- `POST /api/shopify/webhooks/order/created` - Order created
- `POST /api/shopify/webhooks/order/updated` - Order updated

## Database

The app currently supports MongoDB. To use a different database:

### Option 1: MongoDB Atlas (Recommended)
1. Create free cluster at [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Get connection string
3. Set `MONGO_URL` in `backend/.env`

### Option 2: Replit PostgreSQL
1. Enable PostgreSQL in Replit
2. Update backend to use PostgreSQL instead of MongoDB
3. Modify `services/database.py`

### Option 3: No Database (Limited Mode)
The app can run without a database for testing OAuth flow.
Some features will be disabled.

## Troubleshooting

### Frontend Build Issues
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install --legacy-peer-deps
npm run build
```

### Backend Import Errors
```bash
cd backend
pip install -r requirements.txt
```

### MongoDB Connection Errors
- Check `MONGO_URL` in `backend/.env`
- Or run without database (limited mode)
- The app will log warnings but continue running

### Port 5000 Issues
- Make sure no other process is using port 5000
- Kill existing processes: `pkill -f uvicorn`

## Recent Changes

### October 11, 2025
- Added Shopify OAuth authentication flow
- Created Shopify authentication hooks for React
- Configured backend to serve React build files
- Created `shopify.toml` for Shopify CLI
- Updated `start.sh` for production deployment
- Added environment variable templates
- Configured webhooks for order management
- Updated documentation

## User Preferences
- Prefer clear, step-by-step instructions
- Focus on Shopify app deployment
- Use environment variables for all configuration
- Serve frontend and backend together in production

## Next Steps
1. Set up MongoDB or PostgreSQL database
2. Add Shopify API credentials to environment variables
3. Test OAuth flow with development store
4. Configure webhooks in Shopify dashboard
5. Deploy to production
6. Test with real Shopify store

## Support Resources
- Shopify Setup Guide: `SHOPIFY_SETUP_GUIDE.md`
- Environment Examples: `backend/.env.example`, `frontend/.env.example`
- Shopify Config: `shopify.toml`
