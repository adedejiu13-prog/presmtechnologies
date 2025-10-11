# PRESM Technologies - API Contracts & Integration Plan

## Frontend Mock Data Integration Points

### 1. Products (mockData.js)
**Current Mock**: 6 products with categories (dtf-transfers, gang-sheets, heat-presses, supplies, accessories, custom-designs)

**API Contract**:
```
GET /api/products
GET /api/products?category={category}
GET /api/products/{id}
POST /api/products (admin)
PUT /api/products/{id} (admin)
DELETE /api/products/{id} (admin)
```

**Model Fields**:
- id, name, category, price, image, description
- features[], sizes[], minQuantity, maxQuantity
- createdAt, updatedAt

### 2. Cart Management
**Current**: Local state with CartContext

**API Contract**:
```
POST /api/cart/items
GET /api/cart/items
PUT /api/cart/items/{id}
DELETE /api/cart/items/{id}
DELETE /api/cart/clear
```

### 3. Gang Sheet Builder
**Current**: Frontend-only canvas with design management

**API Contract**:
```
POST /api/gang-sheets/create
GET /api/gang-sheets/{id}
POST /api/gang-sheets/{id}/designs
PUT /api/gang-sheets/{id}/designs/{designId}
DELETE /api/gang-sheets/{id}/designs/{designId}
POST /api/gang-sheets/{id}/auto-nest
POST /api/gang-sheets/{id}/export
```

**Model Fields**:
- Gang Sheet: id, templateId, width, height, price, designs[], userId, createdAt
- Design: id, name, src, width, height, x, y, rotation, quantity

### 4. Education Content
**Current**: Static content in mockData.js

**API Contract**:
```
GET /api/education/content
GET /api/education/content?category={category}
GET /api/education/content/{id}
```

### 5. Testimonials & Reviews
**Current**: Static testimonials array

**API Contract**:
```
GET /api/testimonials
POST /api/testimonials
GET /api/reviews/product/{productId}
```

## Shopify Integration Requirements

### 1. Product Sync
- Sync PRESM products with Shopify store
- Update inventory levels
- Handle price changes
- Manage product variants (sizes, options)

### 2. Order Processing
- Create Shopify orders from cart
- Handle order status updates
- Integrate with Shopify checkout
- Process payments through Shopify

### 3. Customer Management
- Sync customer data with Shopify
- Handle authentication via Shopify
- Manage customer orders and history

### 4. Webhook Handling
```
POST /api/shopify/webhooks/order/created
POST /api/shopify/webhooks/order/updated
POST /api/shopify/webhooks/product/updated
```

## Database Schema

### Products Collection
```
{
  _id: ObjectId,
  shopifyId: String,
  name: String,
  category: String,
  price: Number,
  image: String,
  images: [String],
  description: String,
  features: [String],
  sizes: [String],
  minQuantity: Number,
  maxQuantity: Number,
  inventory: Number,
  status: String, // active, inactive, archived
  createdAt: Date,
  updatedAt: Date
}
```

### Gang Sheets Collection
```
{
  _id: ObjectId,
  userId: String,
  templateId: String,
  templateName: String,
  width: Number,
  height: Number,
  basePrice: Number,
  designs: [
    {
      id: String,
      name: String,
      src: String,
      width: Number,
      height: Number,
      x: Number,
      y: Number,
      rotation: Number,
      quantity: Number
    }
  ],
  totalPrice: Number,
  status: String, // draft, ordered, processing, completed
  createdAt: Date,
  updatedAt: Date
}
```

### Orders Collection
```
{
  _id: ObjectId,
  shopifyOrderId: String,
  customerId: String,
  items: [
    {
      productId: String,
      gangSheetId: String, // if gang sheet order
      quantity: Number,
      price: Number,
      options: {}
    }
  ],
  subtotal: Number,
  shipping: Number,
  tax: Number,
  total: Number,
  status: String,
  shippingAddress: {},
  createdAt: Date,
  updatedAt: Date
}
```

### Users Collection
```
{
  _id: ObjectId,
  shopifyCustomerId: String,
  email: String,
  name: String,
  orders: [ObjectId],
  gangSheets: [ObjectId],
  createdAt: Date,
  updatedAt: Date
}
```

## Implementation Priority

### Phase 1: Core Backend APIs
1. Products CRUD endpoints
2. Basic cart management
3. Gang sheet creation and management
4. Order processing

### Phase 2: Shopify Integration
1. Shopify API client setup
2. Product synchronization
3. Order creation in Shopify
4. Webhook handling

### Phase 3: Advanced Features
1. File upload for gang sheet designs
2. AI auto-nesting algorithm
3. PDF export for gang sheets
4. Email notifications

## Frontend Integration Changes

### Remove Mock Dependencies
1. Replace mockData imports with API calls
2. Add loading states and error handling
3. Implement proper form validation
4. Add authentication flow

### API Client Setup
```javascript
// services/api.js
const API_BASE = process.env.REACT_APP_BACKEND_URL + '/api';

export const apiClient = {
  products: {
    getAll: () => fetch(`${API_BASE}/products`),
    getById: (id) => fetch(`${API_BASE}/products/${id}`),
    getByCategory: (category) => fetch(`${API_BASE}/products?category=${category}`)
  },
  gangSheets: {
    create: (data) => fetch(`${API_BASE}/gang-sheets`, { method: 'POST', body: JSON.stringify(data) }),
    getById: (id) => fetch(`${API_BASE}/gang-sheets/${id}`),
    addDesign: (id, design) => fetch(`${API_BASE}/gang-sheets/${id}/designs`, { method: 'POST', body: JSON.stringify(design) })
  }
  // ... other endpoints
};
```

## Environment Variables
```
# Backend
SHOPIFY_STORE_URL=presmtechnologies.myshopify.com
SHOPIFY_ACCESS_TOKEN=
SHOPIFY_WEBHOOK_SECRET=

# Frontend  
REACT_APP_SHOPIFY_STOREFRONT_TOKEN=
```

## Testing Strategy
1. Unit tests for API endpoints
2. Integration tests with Shopify sandbox
3. E2E tests for gang sheet builder
4. Load testing for file uploads