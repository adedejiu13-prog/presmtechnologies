import React, { createContext, useContext } from 'react';
import { useShopifyAuth } from '../hooks/useShopifyAuth';

const ShopifyAuthContext = createContext(null);

export const ShopifyAuthProvider = ({ children }) => {
  const auth = useShopifyAuth();

  return (
    <ShopifyAuthContext.Provider value={auth}>
      {children}
    </ShopifyAuthContext.Provider>
  );
};

export const useShopifyAuthContext = () => {
  const context = useContext(ShopifyAuthContext);
  if (!context) {
    throw new Error('useShopifyAuthContext must be used within ShopifyAuthProvider');
  }
  return context;
};

export default ShopifyAuthContext;
