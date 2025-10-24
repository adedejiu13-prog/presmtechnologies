import React, { useEffect, useState } from "react";
import Navigation from "../components/Navigation";
import Footer from "../components/Footer";
import { Button } from "../components/ui/button";
import { Card, CardContent } from "../components/ui/card";
import { Loader2, ShoppingCart, Plus } from "lucide-react";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "../components/ui/select";
import { useCart } from "../context/CartContext";

const ProductsPage = () => {
  const BACKEND_URL = "https://unimaginepresmbackned.onrender.com";
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const { addItem } = useCart();

  // Fetch products from Shopify backend
  useEffect(() => {
    const fetchProducts = async () => {
      try {
        const res = await fetch(`${BACKEND_URL}/api/shopify/products`);
        if (!res.ok) throw new Error(`Failed to fetch products (${res.status})`);
        const data = await res.json();
        setProducts(data.products || []);
      } catch (err) {
        console.error("Error fetching Shopify products:", err);
        setProducts([]);
      } finally {
        setLoading(false);
      }
    };
    fetchProducts();
  }, []);

  // Handle Buy Now (direct checkout)
  const handleBuy = async (variantId) => {
    try {
      const res = await fetch(`${BACKEND_URL}/api/shopify/cart/create`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          items: [{ variant_id: variantId, quantity: 1 }],
        }),
      });

      if (!res.ok) {
        const errorText = await res.text();
        throw new Error(`Failed to create checkout: ${res.status} ${errorText}`);
      }

      const data = await res.json();
      if (data.checkout_url) {
        window.location.href = data.checkout_url;
      } else {
        console.error("Checkout failed: No checkout URL returned.");
      }
    } catch (error) {
      console.error("Error during checkout:", error);
    }
  };

  // Handle Add to Cart
  const handleAddToCart = (product, variantId) => {
    const selectedVariant = product.variants.find(v => v.shopify_id === variantId);
    if (!selectedVariant || !selectedVariant.available) {
      console.error("Cannot add to cart: Variant unavailable.");
      return;
    }
    addItem({
      variant_id: variantId,
      quantity: 1,
      name: product.name + (selectedVariant.title !== "Default Title" ? ` (${selectedVariant.title})` : ""),
      price: Number(selectedVariant.price),
      image: product.image,
    });
    console.log(`${product.name} added to cart.`);
  };

  if (loading)
    return (
      <div className="flex flex-col items-center justify-center py-20">
        <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
        <p className="mt-3 text-gray-600">Loading products...</p>
      </div>
    );

  return (
    <div className="min-h-screen bg-gray-50">
      <Navigation />
      <div className="max-w-6xl mx-auto px-6 py-12">
        <h1 className="text-4xl font-bold mb-8 text-gray-900 text-center">
          Our Shopify Products
        </h1>

        {products.length === 0 ? (
          <p className="text-center text-gray-500">No products found.</p>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8">
            {products.map((product) => (
              <Card
                key={product.shopify_id}
                className="overflow-hidden shadow-sm hover:shadow-md transition-shadow bg-white"
              >
                {product.image ? (
                  <img
                    src={product.image}
                    alt={product.name}
                    className="w-full h-56 object-cover"
                  />
                ) : (
                  <div className="w-full h-56 bg-gray-200 flex items-center justify-center text-gray-500">
                    No image
                  </div>
                )}
                <CardContent className="p-6">
                  <h2 className="text-xl font-semibold mb-2 text-gray-800">
                    {product.name}
                  </h2>
                  <p className="text-gray-600 mb-4">
                    ${product.variants[0]?.price.toFixed(2) || product.price.toFixed(2)}
                  </p>
                  {product.variants?.length > 0 && (
                    <>
                      {product.variants.length > 1 ? (
                        <Select
                          onValueChange={(value) => handleAddToCart(product, value)}
                          defaultValue={product.variants[0].shopify_id}
                        >
                          <SelectTrigger className="w-full mb-4">
                            <SelectValue placeholder="Select variant" />
                          </SelectTrigger>
                          <SelectContent>
                            {product.variants.map((variant) => (
                              <SelectItem
                                key={variant.shopify_id}
                                value={variant.shopify_id}
                                disabled={!variant.available}
                              >
                                {variant.title} - ${variant.price.toFixed(2)}
                                {!variant.available && " (Out of Stock)"}
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                      ) : (
                        <Button
                          className="w-full bg-blue-600 hover:bg-blue-700 mb-2"
                          onClick={() => handleAddToCart(product, product.variants[0].shopify_id)}
                          disabled={!product.variants[0].available}
                        >
                          <Plus className="mr-2 h-4 w-4" />
                          Add to Cart
                        </Button>
                      )}
                      <Button
                        className="w-full bg-blue-600 hover:bg-blue-700"
                        onClick={() => handleBuy(product.variants[0].shopify_id)}
                        disabled={!product.variants[0].available}
                      >
                        <ShoppingCart className="mr-2 h-4 w-4" />
                        Buy Now
                      </Button>
                    </>
                  )}
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
      <Footer />
    </div>
  );
};

export default ProductsPage;
