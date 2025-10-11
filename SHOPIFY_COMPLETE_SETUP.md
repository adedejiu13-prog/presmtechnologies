# Complete Shopify Setup Guide for PRESM DTF App

## 📋 Prerequisites
- Shopify Partner account (sign up at https://partners.shopify.com/)
- Development or production Shopify store
- Your Replit app URL: `https://2b8b652b-df3e-445c-8ae6-0dcad3d08a2a-00-1arlrmopahkmr.worf.replit.dev`

## Step 1: Create Shopify App

### 1.1 Create New App in Shopify Partners
1. Go to [Shopify Partners Dashboard](https://partners.shopify.com/)
2. Click **Apps** → **Create app**
3. Choose **Create app manually**
4. Enter app name: **Presm DTF Shopify App**
5. Click **Create**

### 1.2 Get Your API Credentials
After creating the app:
1. Go to **App setup** → **Configuration**
2. Copy your **API key** (also called Client ID)
3. Copy your **API secret** (click "Reveal" to see it)
4. **IMPORTANT**: Save these securely - you'll need them for Replit

## Step 2: Configure App URLs

### 2.1 Set App URL
In your Shopify app configuration:
```
App URL: https://2b8b652b-df3e-445c-8ae6-0dcad3d08a2a-00-1arlrmopahkmr.worf.replit.dev
```

### 2.2 Set Allowed Redirection URLs
Add this OAuth callback URL:
```
https://2b8b652b-df3e-445c-8ae6-0dcad3d08a2a-00-1arlrmopahkmr.worf.replit.dev/api/auth/shopify/callback
```

## Step 3: Configure API Scopes

### 3.1 Essential Scopes (Select These First)
In **Configuration** → **API scopes**, select:

✅ **Products** (Admin API)
- `read_products` - View products
- `write_products` - Create/update products

✅ **Orders** (Admin API)
- `read_orders` - View order details  
- `write_orders` - Update orders

✅ **Customer** (Admin API)
- `read_customers` - Access customer info

### 3.2 Recommended Additional Scopes
For enhanced functionality, also select:

✅ **Inventory** (Admin API)
- `read_inventory` - View inventory levels
- `write_inventory` - Update stock

✅ **Fulfillment services** (Admin API)
- `read_fulfillments` - View fulfillment status
- `write_fulfillments` - Mark orders fulfilled

### 3.3 Optional Scopes (Add Later if Needed)
✅ **Files** (Admin API)
- `read_files` - Access design files
- `write_files` - Upload gang sheets

✅ **Draft orders** (Admin API)
- `read_draft_orders` - Create custom quotes
- `write_draft_orders` - Save order drafts

## Step 4: Configure Webhooks

### 4.1 Add Webhook Subscriptions
In **Configuration** → **Webhooks**, add:

**Webhook 1: Order Created**
```
Event: orders/create
Format: JSON
URL: https://2b8b652b-df3e-445c-8ae6-0dcad3d08a2a-00-1arlrmopahkmr.worf.replit.dev/api/shopify/webhooks/order/created
API version: 2024-10
```

**Webhook 2: Order Updated**
```
Event: orders/update
Format: JSON
URL: https://2b8b652b-df3e-445c-8ae6-0dcad3d08a2a-00-1arlrmopahkmr.worf.replit.dev/api/shopify/webhooks/order/updated
API version: 2024-10
```

### 4.2 Get Webhook Secret
After adding webhooks:
1. Shopify will generate a **webhook signing secret**
2. Copy this secret - you'll need it for webhook verification

## Step 5: Add Credentials to Replit

### Option 1: Use Replit Secrets (Recommended) ⭐
1. In Replit, click **Tools** → **Secrets**
2. Add these secrets:

```
SHOPIFY_API_KEY = paste_your_api_key_here
SHOPIFY_API_SECRET = paste_your_api_secret_here
SHOPIFY_WEBHOOK_SECRET = paste_your_webhook_secret_here
SHOPIFY_SCOPES = read_products,write_products,read_orders,write_orders,read_customers,read_inventory,write_inventory,read_fulfillments,write_fulfillments
```

### Option 2: Use .env File (Alternative)
1. Create `backend/.env` file (copy from `backend/.env.example`)
2. Fill in your credentials:

```bash
SHOPIFY_API_KEY=your_actual_api_key
SHOPIFY_API_SECRET=your_actual_api_secret  
SHOPIFY_WEBHOOK_SECRET=your_actual_webhook_secret
SHOPIFY_SCOPES=read_products,write_products,read_orders,write_orders,read_customers,read_inventory,write_inventory,read_fulfillments,write_fulfillments
SHOPIFY_API_VERSION=2024-10
```

**⚠️ IMPORTANT:** Never commit `.env` file to Git!

## Step 6: Test Your Integration

### 6.1 Restart Your Replit App
After adding credentials, restart the workflow to apply changes.

### 6.2 Install App to Your Store
Visit this URL (replace with your store name):
```
https://2b8b652b-df3e-445c-8ae6-0dcad3d08a2a-00-1arlrmopahkmr.worf.replit.dev/api/auth/shopify/install?shop=your-store-name
```

Example:
```
https://2b8b652b-df3e-445c-8ae6-0dcad3d08a2a-00-1arlrmopahkmr.worf.replit.dev/api/auth/shopify/install?shop=presm-test-store
```

### 6.3 Complete OAuth Flow
1. You'll be redirected to Shopify
2. Review the permissions requested
3. Click **Install app**
4. You'll be redirected back to your app (logged in)

### 6.4 Verify Integration
Check these endpoints to verify everything works:

**Verify Session:**
```
GET /api/auth/shopify/verify
```

**Get Store Info:**
```
GET /api/shopify/store/info
```

## Step 7: Update Shopify Configuration (If Needed)

### Update Scopes in Code
The scopes are configured in `backend/routes/auth.py` line 19:
```python
SHOPIFY_SCOPES = os.getenv("SHOPIFY_SCOPES", "read_products,write_products,read_orders").split(",")
```

And in `shopify.toml` line 10:
```toml
scopes = "read_products,write_products,read_orders,write_orders,read_customers"
```

## 🔒 Security Best Practices

### ✅ DO:
- Store credentials in Replit Secrets (not in code)
- Use HTTPS for all communication (automatic on Replit)
- Verify webhook signatures (already implemented)
- Use CSRF protection with state tokens (already implemented)

### ⚠️ DON'T:
- Don't commit `.env` files to Git
- Don't expose API secrets in frontend code
- Don't skip HMAC verification in production

## 📊 Scope Summary

### Current Configuration:
```
read_products, write_products, read_orders, write_orders, read_customers
```

### Recommended for Full Features:
```
read_products, write_products
read_orders, write_orders
read_customers
read_inventory, write_inventory
read_fulfillments, write_fulfillments
```

### Optional for Advanced Features:
```
read_files, write_files
read_draft_orders, write_draft_orders
read_checkouts, write_checkouts
```

## 🚀 Next Steps

1. ✅ Create Shopify Partner app
2. ✅ Add credentials to Replit Secrets
3. ✅ Configure webhooks
4. ✅ Test OAuth installation
5. ✅ Set up database (MongoDB Atlas or PostgreSQL)
6. ✅ Start processing real orders!

## 📞 Support Resources

- [Shopify App Documentation](https://shopify.dev/docs/apps)
- [Shopify API Reference](https://shopify.dev/api)
- [OAuth Implementation Guide](https://shopify.dev/docs/apps/auth/oauth)
- [Webhook Documentation](https://shopify.dev/docs/apps/webhooks)

## 🔍 Troubleshooting

### Error: "Invalid HMAC signature"
- Make sure `SHOPIFY_API_SECRET` is set correctly
- Verify the secret matches your Shopify Partner dashboard

### Error: "OAuth redirect URI mismatch"
- Ensure redirect URI in Shopify matches exactly:
  `https://2b8b652b-df3e-445c-8ae6-0dcad3d08a2a-00-1arlrmopahkmr.worf.replit.dev/api/auth/shopify/callback`

### Error: "Missing scopes"
- Update scopes in Replit Secrets or `.env`
- Uninstall and reinstall app to refresh permissions

### Webhook not receiving events
- Verify webhook URL is accessible (HTTPS)
- Check webhook secret is configured correctly
- Test webhook delivery in Shopify admin
