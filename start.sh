#!/bin/bash

# Get Replit domain or use localhost for development
if [ -n "$REPLIT_DEV_DOMAIN" ]; then
    PUBLIC_URL="https://${REPLIT_DEV_DOMAIN}"
elif [ -n "$REPL_SLUG" ] && [ -n "$REPL_OWNER" ]; then
    PUBLIC_URL="https://${REPL_SLUG}.${REPL_OWNER}.repl.co"
else
    PUBLIC_URL="http://localhost:5000"
fi

# Set environment variables
export REACT_APP_BACKEND_URL="${PUBLIC_URL}"
export SHOPIFY_REDIRECT_URI="${PUBLIC_URL}/api/auth/shopify/callback"
export PUBLIC_URL="${PUBLIC_URL}"

echo "========================================="
echo "Building PRESM DTF Shopify App"
echo "Public URL: ${PUBLIC_URL}"
echo "========================================="

# Build the React frontend for production
echo "Building React frontend..."
cd frontend
npm run build
cd ..

# Start the backend server on port 5000 (serves both API and static files)
echo "Starting FastAPI backend on port 5000..."
cd backend
python3 -m uvicorn server:app --host 0.0.0.0 --port 5000 --reload
