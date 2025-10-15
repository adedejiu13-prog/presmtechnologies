import React, { createContext, useContext, useReducer } from 'react';

const CartContext = createContext();

const cartReducer = (state, action) => {
  switch (action.type) {
    case 'ADD_ITEM':
      const existingItem = state.items.find(item => 
        item.id === action.payload.id && 
        JSON.stringify(item.options) === JSON.stringify(action.payload.options)
      );
      
      if (existingItem) {
        return {
          ...state,
          items: state.items.map(item => 
            item === existingItem 
              ? { ...item, quantity: item.quantity + action.payload.quantity }
              : item
          )
        };
      }
      
      return {
        ...state,
        items: [...state.items, action.payload]
      };
    
    case 'REMOVE_ITEM':
      return {
        ...state,
        items: state.items.filter(item => item.cartId !== action.payload)
      };
    
    case 'UPDATE_QUANTITY':
      return {
        ...state,
        items: state.items.map(item => 
          item.cartId === action.payload.cartId 
            ? { ...item, quantity: action.payload.quantity }
            : item
        )
      };
    
    case 'CLEAR_CART':
      return {
        ...state,
        items: []
      };
    
    default:
      return state;
  }
};

export const CartProvider = ({ children }) => {
  const [state, dispatch] = useReducer(cartReducer, { items: [] });
  
  const addItem = (item) => {
    // Ensure each item has a variant_id
    const variantId =
      item.variant_id || item.variants?.[0]?.id || "gid://shopify/ProductVariant/1234567890";
    
    dispatch({
      type: 'ADD_ITEM',
      payload: { ...item, variant_id: variantId, cartId: Date.now() + Math.random() }
    });
  };
  
  const removeItem = (cartId) => {
    dispatch({ type: 'REMOVE_ITEM', payload: cartId });
  };
  
  const updateQuantity = (cartId, quantity) => {
    if (quantity <= 0) {
      removeItem(cartId);
    } else {
      dispatch({ type: 'UPDATE_QUANTITY', payload: { cartId, quantity } });
    }
  };
  
  const clearCart = () => {
    dispatch({ type: 'CLEAR_CART' });
  };
  
  const getTotalItems = () => {
    return state.items.reduce((total, item) => total + item.quantity, 0);
  };
  
  const getTotalPrice = () => {
    return state.items.reduce((total, item) => total + (item.price * item.quantity), 0);
  };

  // ✅ Sync cart with backend
  const syncCartWithBackend = async (sessionId, backendUrl) => {
    try {
      for (const item of state.items) {
        await fetch(`${backendUrl}/api/cart/items`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'x-session-id': sessionId,
          },
          body: JSON.stringify({
            product_id: item.id,
            variant_id: item.variant_id,
            name: item.name,
            quantity: item.quantity,
            price: item.price,
            options: item.options || {},
          }),
        });
      }
    } catch (error) {
      console.error('Error syncing cart with backend:', error);
    }
  };
  
  return (
    <CartContext.Provider value={{
      items: state.items,
      addItem,
      removeItem,
      updateQuantity,
      clearCart,
      getTotalItems,
      getTotalPrice,
      syncCartWithBackend
    }}>
      {children}
    </CartContext.Provider>
  );
};

export const useCart = () => {
  const context = useContext(CartContext);
  if (!context) {
    throw new Error('useCart must be used within a CartProvider');
  }
  return context;
};
