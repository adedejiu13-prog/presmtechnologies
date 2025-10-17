import React, { useEffect, useState } from "react";
import Navigation from "../components/Navigation";
import Footer from "../components/Footer";
import { Button } from "../components/ui/button";
import { Card, CardContent } from "../components/ui/card";
import { Loader2, ShoppingCart } from "lucide-react";

const ProductsPage = () => {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);

  // Fetch products from your backend (which connects to Shopify)
  useEffect(() => {
    const fetchProducts = async () => {
      try {
        const res = await fetch("https://fictional-meme-979vqvw5xp7v37r45-8000.app.github.dev/api/shopify/products");
        const data = await res.json();
        setProducts(data.products || []);
      } catch (err) {
        console.error("Error fetching Shopify products:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchProducts();
  }, []);

  // Handle checkout creation
  const handleBuy = async (variantId) => {
    try {
      const res = await fetch("https://presmtechnologies.onrender.com/api/shopify/cart/create", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          variant_id: variantId,
          quantity: 1,
        }),
      });

      const data = await res.json();
      if (data.checkout_url) {
        window.location.href = data.checkout_url; // Redirect to Shopify checkout
      } else {
        alert("Failed to create checkout. Please try again.");
      }
    } catch (error) {
      console.error("Error during checkout:", error);
    }
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
                  <p className="text-gray-600 mb-4">${product.price}</p>

                  {product.variants?.length > 0 && (
                    <Button
                      className="w-full bg-blue-600 hover:bg-blue-700"
                      onClick={() => handleBuy(product.variants[0].shopify_id)}
                    >
                      <ShoppingCart className="mr-2 h-4 w-4" />
                      Buy Now
                    </Button>
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
