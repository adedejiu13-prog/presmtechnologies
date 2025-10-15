import React, { useEffect } from 'react';
import Navigation from '../components/Navigation';
import Footer from '../components/Footer';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Input } from '../components/ui/input';
import { Badge } from '../components/ui/badge';
import { Trash2, Plus, Minus, ArrowRight, ShoppingBag } from 'lucide-react';
import { useCart } from '../context/CartContext';
import { Link } from 'react-router-dom';

const CartPage = () => {
  const { items, removeItem, updateQuantity, getTotalPrice, clearCart } = useCart();

  // ✅ Generate or load a persistent session ID
  useEffect(() => {
    if (!localStorage.getItem("session_id")) {
      localStorage.setItem("session_id", crypto.randomUUID());
    }
  }, []);

  const sessionId = localStorage.getItem("session_id");

  // ✅ Ensure backend cart syncs before checkout
  const syncCartWithBackend = async () => {
    const backendUrl = process.env.REACT_APP_BACKEND_URL || window.location.origin;
    try {
      for (const item of items) {
        await fetch(`${backendUrl}/api/cart/items`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "x-session-id": sessionId,
          },
          body: JSON.stringify({
            product_id: item.id || item.product_id || "123",
            variant_id: item.variant_id || "gid://shopify/ProductVariant/1234567890",
            name: item.name || "Test Product",
            quantity: item.quantity || 1,
            price: item.price || 20.0,
          }),
        });
      }
    } catch (error) {
      console.error("Error syncing cart:", error);
    }
  };

  const handleCheckout = async () => {
    const backendUrl = process.env.REACT_APP_BACKEND_URL || window.location.origin;
    try {
      // ✅ Ensure backend has the latest items
      await syncCartWithBackend();

      const response = await fetch(`${backendUrl}/api/shopify/checkout/create`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "x-session-id": sessionId,
        },
      });

      const data = await response.json();

      if (response.ok && data.checkout_url) {
        window.location.href = data.checkout_url;
      } else {
        alert("Checkout failed: " + (data.detail || "Unknown error"));
        console.error("Checkout error:", data);
      }
    } catch (error) {
      console.error("Error creating checkout:", error);
      alert("Something went wrong creating the checkout.");
    }
  };

  // 🛒 Empty Cart UI
  if (items.length === 0) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Navigation />
        <div className="container mx-auto px-4 py-16 text-center">
          <ShoppingBag className="h-24 w-24 mx-auto text-gray-300 mb-6" />
          <h2 className="text-3xl font-bold text-gray-900 mb-4">Your cart is empty</h2>
          <p className="text-gray-600 mb-8">Add some products to get started with your order.</p>
          <Link to="/products">
            <Button size="lg" className="bg-blue-600 hover:bg-blue-700">
              Start Shopping
              <ArrowRight className="ml-2 h-5 w-5" />
            </Button>
          </Link>
        </div>
        <Footer />
      </div>
    );
  }

  // 🛍️ Cart UI
  return (
    <div className="min-h-screen bg-gray-50">
      <Navigation />
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-4xl font-bold text-gray-900 mb-8">Shopping Cart</h1>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Cart Items */}
          <div className="lg:col-span-2 space-y-4">
            {items.map((item) => (
              <Card key={item.cartId || item.id} className="overflow-hidden">
                <CardContent className="p-0">
                  <div className="flex">
                    <img
                      src={item.image}
                      alt={item.name}
                      className="w-24 h-24 object-cover"
                    />
                    <div className="flex-1 p-6">
                      <div className="flex justify-between items-start mb-2">
                        <h3 className="font-semibold text-lg">{item.name}</h3>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => removeItem(item.cartId || item.id)}
                          className="text-red-500 hover:text-red-700"
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>

                      <p className="text-gray-600 text-sm mb-3">{item.description}</p>

                      {item.options && (
                        <div className="flex flex-wrap gap-2 mb-3">
                          {Object.entries(item.options).map(([key, value]) => (
                            <Badge key={key} variant="outline" className="text-xs">
                              {key}: {value}
                            </Badge>
                          ))}
                        </div>
                      )}

                      <div className="flex justify-between items-center">
                        <div className="flex items-center space-x-2">
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => updateQuantity(item.cartId || item.id, item.quantity - 1)}
                            disabled={item.quantity <= 1}
                          >
                            <Minus className="h-3 w-3" />
                          </Button>
                          <span className="text-sm min-w-[2rem] text-center">{item.quantity}</span>
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => updateQuantity(item.cartId || item.id, item.quantity + 1)}
                          >
                            <Plus className="h-3 w-3" />
                          </Button>
                        </div>

                        <div className="text-right">
                          <div className="text-lg font-bold text-blue-600">
                            ${(item.price * item.quantity).toFixed(2)}
                          </div>
                          <div className="text-sm text-gray-500">${item.price} each</div>
                        </div>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}

            <div className="flex justify-between items-center pt-4">
              <Button
                variant="outline"
                onClick={clearCart}
                className="text-red-600 border-red-300 hover:bg-red-50"
              >
                Clear Cart
              </Button>
              <Link to="/products">
                <Button variant="ghost">Continue Shopping</Button>
              </Link>
            </div>
          </div>

          {/* Order Summary */}
          <div className="lg:col-span-1">
            <Card className="sticky top-24">
              <CardHeader>
                <CardTitle>Order Summary</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex justify-between text-sm">
                  <span>Subtotal ({items.length} items)</span>
                  <span>${getTotalPrice().toFixed(2)}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span>Shipping</span>
                  <span className="text-green-600">
                    {getTotalPrice() >= 75 ? 'Free' : '$9.99'}
                  </span>
                </div>
                <div className="flex justify-between text-sm">
                  <span>Tax (estimated)</span>
                  <span>${(getTotalPrice() * 0.08).toFixed(2)}</span>
                </div>
                <div className="border-t pt-4">
                  <div className="flex justify-between font-semibold text-lg">
                    <span>Total</span>
                    <span className="text-green-600">
                      ${(getTotalPrice() + (getTotalPrice() >= 75 ? 0 : 9.99) + (getTotalPrice() * 0.08)).toFixed(2)}
                    </span>
                  </div>
                </div>

                {getTotalPrice() < 75 && (
                  <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
                    <p className="text-sm text-blue-800">
                      Add ${(75 - getTotalPrice()).toFixed(2)} more for free shipping!
                    </p>
                  </div>
                )}

                {/* ✅ Checkout Button */}
                <Button
                  className="w-full bg-blue-600 hover:bg-blue-700"
                  size="lg"
                  onClick={handleCheckout}
                >
                  Proceed to Checkout
                  <ArrowRight className="ml-2 h-5 w-5" />
                </Button>

                <div className="text-center">
                  <p className="text-xs text-gray-500">
                    Secure checkout powered by Shopify
                  </p>
                </div>

                {/* Promo Code */}
                <div className="border-t pt-4">
                  <label className="text-sm font-medium mb-2 block">Promo Code</label>
                  <div className="flex space-x-2">
                    <Input placeholder="Enter code" className="flex-1" />
                    <Button variant="outline">Apply</Button>
                  </div>
                </div>

                {/* Trust Badges */}
                <div className="border-t pt-4 space-y-2">
                  <div className="flex items-center text-sm text-gray-600">
                    <span className="w-4 h-4 bg-green-500 rounded-full mr-2"></span>
                    100% Satisfaction Guarantee
                  </div>
                  <div className="flex items-center text-sm text-gray-600">
                    <span className="w-4 h-4 bg-green-500 rounded-full mr-2"></span>
                    Secure SSL Encrypted Payment
                  </div>
                  <div className="flex items-center text-sm text-gray-600">
                    <span className="w-4 h-4 bg-green-500 rounded-full mr-2"></span>
                    Fast & Reliable Shipping
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
      <Footer />
    </div>
  );
};

export default CartPage;
