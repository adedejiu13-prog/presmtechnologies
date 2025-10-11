import { useState, useEffect, useCallback } from 'react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8081';

export const useShopifyAuth = () => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [shopInfo, setShopInfo] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const checkAuth = useCallback(async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${BACKEND_URL}/api/auth/shopify/verify`, {
        withCredentials: true
      });
      
      if (response.data.authenticated) {
        setIsAuthenticated(true);
        setShopInfo({
          shop: response.data.shop,
          name: response.data.shop_name,
          email: response.data.shop_email
        });
      } else {
        setIsAuthenticated(false);
        setShopInfo(null);
      }
    } catch (err) {
      setIsAuthenticated(false);
      setShopInfo(null);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  const initiateOAuth = useCallback((shop) => {
    const cleanShop = shop.replace('.myshopify.com', '');
    window.location.href = `${BACKEND_URL}/api/auth/shopify/install?shop=${cleanShop}`;
  }, []);

  const logout = useCallback(async () => {
    try {
      await axios.post(`${BACKEND_URL}/api/auth/shopify/logout`, {}, {
        withCredentials: true
      });
      setIsAuthenticated(false);
      setShopInfo(null);
    } catch (err) {
      setError(err.message);
    }
  }, []);

  useEffect(() => {
    checkAuth();
  }, [checkAuth]);

  return {
    isAuthenticated,
    shopInfo,
    loading,
    error,
    initiateOAuth,
    logout,
    checkAuth
  };
};

export default useShopifyAuth;
