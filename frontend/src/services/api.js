import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API_BASE = `${BACKEND_URL}/api`;

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor for session management
api.interceptors.request.use((config) => {
  const sessionId = getSessionId();
  config.headers['x-session-id'] = sessionId;
  return config;
});

// Session management
const getSessionId = () => {
  let sessionId = localStorage.getItem('sessionId');
  if (!sessionId) {
    sessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    localStorage.setItem('sessionId', sessionId);
  }
  return sessionId;
};

// Products API
export const productsAPI = {
  getAll: (params = {}) => api.get('/products/', { params }),
  getById: (id) => api.get(`/products/${id}`),
  getByCategory: (category) => api.get('/products/', { params: { category } }),
  search: (query, category = null) => api.get('/products/', { params: { search: query, category } }),
  getCategories: () => api.get('/products/categories'),
};

// Gang Sheets API
export const gangSheetsAPI = {
  getTemplates: () => api.get('/gang-sheets/templates'),
  create: (data) => api.post('/gang-sheets/', data),
  getById: (id) => api.get(`/gang-sheets/${id}`),
  addDesign: (id, design) => api.post(`/gang-sheets/${id}/designs`, design),
  updateDesign: (id, designId, updates) => api.put(`/gang-sheets/${id}/designs/${designId}`, updates),
  removeDesign: (id, designId) => api.delete(`/gang-sheets/${id}/designs/${designId}`),
  autoNest: (id) => api.post(`/gang-sheets/${id}/auto-nest`),
  uploadFile: (id, file) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post(`/gang-sheets/${id}/designs/upload`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
  }
};

// Cart API
export const cartAPI = {
  get: () => api.get('/cart/'),
  addItem: (item) => api.post('/cart/items', item),
  updateItem: (index, data) => api.put(`/cart/items/${index}`, data),
  removeItem: (index) => api.delete(`/cart/items/${index}`),
  clear: () => api.delete('/cart/clear'),
  getSummary: () => api.get('/cart/summary'),
};

// Shopify API
export const shopifyAPI = {
  createCheckout: () => api.post('/shopify/checkout/create'),
  getStoreInfo: () => api.get('/shopify/store/info'),
};

// Error handling helper
export const handleAPIError = (error) => {
  if (error.response) {
    // Server responded with error status
    console.error('API Error:', error.response.data);
    return error.response.data.detail || 'An error occurred';
  } else if (error.request) {
    // Request made but no response received
    console.error('Network Error:', error.request);
    return 'Network error - please check your connection';
  } else {
    // Something else happened
    console.error('Error:', error.message);
    return error.message || 'An unexpected error occurred';
  }
};

export default api;