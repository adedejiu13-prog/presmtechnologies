# Shopify API Scopes Summary for PRESM DTF App

## ✅ Currently Configured Scopes

Your app is configured with these essential scopes:

### Core Scopes (Already Set)
```
read_products
write_products
read_orders
write_orders
read_customers
read_inventory
write_inventory
read_fulfillments
write_fulfillments
```

## 📋 What You Need to Configure in Shopify Partner Dashboard

When setting up your Shopify app, **select these scopes** in the Shopify Partner dashboard:

### 1. Products (Admin API) ✅ REQUIRED
- ☑️ `read_products` - View product catalog
- ☑️ `write_products` - Create/update DTF transfer products

### 2. Orders (Admin API) ✅ REQUIRED
- ☑️ `read_orders` - View customer orders
- ☑️ `write_orders` - Update order status, add notes

### 3. Customer (Admin API) ✅ REQUIRED
- ☑️ `read_customers` - Access customer information for personalized service

### 4. Inventory (Admin API) ✅ REQUIRED
- ☑️ `read_inventory` - Check stock levels
- ☑️ `write_inventory` - Update inventory when gang sheets are produced

### 5. Fulfillment services (Admin API) ✅ REQUIRED
- ☑️ `read_fulfillments` - Check fulfillment status
- ☑️ `write_fulfillments` - Mark orders as fulfilled when shipped

## 🎯 Optional Scopes (Add Later for Advanced Features)

### Files (Admin API) - For Design Management
- ☐ `read_files` - Access uploaded design files
- ☐ `write_files` - Upload gang sheet PDFs

**Use case:** Store and retrieve customer design files and generated gang sheets

### Draft Orders (Admin API) - For Custom Quotes
- ☐ `read_draft_orders` - View draft orders
- ☐ `write_draft_orders` - Create custom quotes for bulk orders

**Use case:** Create custom pricing for large gang sheet orders

### Checkouts (Admin API) - For Advanced Cart Features
- ☐ `read_checkouts` - View checkout data
- ☐ `write_checkouts` - Modify checkout process

**Use case:** Custom checkout modifications for DTF transfer configuration

## 📊 Scope Configuration Locations

### 1. Replit Secrets (Active Configuration)
```
SHOPIFY_SCOPES=read_products,write_products,read_orders,write_orders,read_customers,read_inventory,write_inventory,read_fulfillments,write_fulfillments
```

### 2. Code Configuration (`backend/routes/auth.py`)
```python
SHOPIFY_SCOPES = os.getenv("SHOPIFY_SCOPES", "read_products,write_products,read_orders").split(",")
```

### 3. Shopify CLI Config (`shopify.toml`)
```toml
scopes = "read_products,write_products,read_orders,write_orders,read_customers,read_inventory,write_inventory,read_fulfillments,write_fulfillments"
```

## 🔄 How to Update Scopes

### If You Need to Add More Scopes:

1. **Update in Replit Secrets:**
   - Go to Tools → Secrets
   - Edit `SHOPIFY_SCOPES`
   - Add new scopes (comma-separated, no spaces)

2. **Update in Shopify Partner Dashboard:**
   - Go to your app configuration
   - Add new API scopes
   - Save changes

3. **Reinstall App:**
   - Users must reinstall the app to grant new permissions
   - Visit: `/api/auth/shopify/install?shop=your-store-name`

## 🚀 Quick Setup Checklist

### In Shopify Partner Dashboard:
- [x] Create Shopify Partner app
- [ ] Set App URL to your Replit domain
- [ ] Add OAuth redirect URL
- [ ] Select these 9 scopes:
  - Products: read_products, write_products
  - Orders: read_orders, write_orders  
  - Customer: read_customers
  - Inventory: read_inventory, write_inventory
  - Fulfillment: read_fulfillments, write_fulfillments

### In Replit:
- [x] Add SHOPIFY_API_KEY to Secrets ✅
- [x] Add SHOPIFY_API_SECRET to Secrets ✅
- [x] Add SHOPIFY_WEBHOOK_SECRET to Secrets ✅
- [x] Configure SHOPIFY_SCOPES ✅

## 📝 Notes

- **Comma-separated format:** Scopes must be comma-separated with NO spaces
- **Case-sensitive:** Use exact scope names (lowercase with underscores)
- **Re-authentication required:** When adding new scopes, users must reinstall the app
- **Minimal by default:** Start with essential scopes, add more as needed

## 🔗 References

- [Shopify API Scopes Documentation](https://shopify.dev/docs/api/usage/access-scopes)
- [OAuth Implementation Guide](https://shopify.dev/docs/apps/auth/oauth)
- [Admin API Reference](https://shopify.dev/docs/api/admin)

---

**Current Status:** ✅ Shopify integration configured and ready to use!

**Next Step:** Install the app to your Shopify store by visiting:
```
https://2b8b652b-df3e-445c-8ae6-0dcad3d08a2a-00-1arlrmopahkmr.worf.replit.dev/api/auth/shopify/install?shop=your-store-name
```
