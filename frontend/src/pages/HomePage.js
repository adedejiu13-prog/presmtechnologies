// src/pages/HomePage.jsx
import React, { useState, useEffect } from 'react';
import Navigation from '../components/Navigation';
import Footer from '../components/Footer';
import { Button } from '../components/ui/button';
import { Card, CardContent } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Input } from '../components/ui/input';
import { ArrowRight } from 'lucide-react';
import { Link } from 'react-router-dom';
import { Dialog, DialogContent, DialogTitle, DialogDescription } from '../components/ui/dialog';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { useCart } from '../context/CartContext';

const HomePage = () => {
  const BACKEND_URL = "https://silver-dollop-pjrvgv9wqjg5c7wpx-8000.app.github.dev";
  const [email, setEmail] = useState('');
  const [showPromoModal, setShowPromoModal] = useState(true);
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const { addItem } = useCart();

  // Fetch products from FastAPI backend
  useEffect(() => {
    const fetchProducts = async () => {
      try {
        const res = await fetch(`${BACKEND_URL}/api/shopify/products`);
        if (!res.ok) throw new Error(`Failed to fetch products (${res.status})`);
        const data = await res.json();
        setProducts(Array.isArray(data) ? data : data.products || []);
      } catch (err) {
        console.error('❌ Error fetching products:', err);
        setProducts([]);
      } finally {
        setLoading(false);
      }
    };
    fetchProducts();
  }, []);

  const handleNewsletterSignup = (e) => {
    e.preventDefault();
    alert("You've been subscribed to our newsletter.");
    setEmail('');
  };

  const featuredProducts = products.slice(0, 5);

  const ProductCard = ({ product }) => {
    const [selectedVariant, setSelectedVariant] = useState(product.variants[0]?.shopify_id || '');
    const selectedV = product.variants.find(v => v.shopify_id === selectedVariant) || product.variants[0];
    const price = selectedV ? selectedV.price : product.price;

    return (
      <Card key={product.shopify_id} className="hover:shadow-lg transition-shadow">
        <img
          src={product.image || "https://via.placeholder.com/300"}
          alt={product.name}
          className="w-full h-48 object-cover"
        />
        <CardContent className="p-6">
          <h3 className="font-semibold text-lg mb-2">{product.name}</h3>
          <p className="text-gray-600 text-sm mb-4">
            {product.description?.slice(0, 100) || "High-quality product."}
          </p>
          {product.variants.length > 1 && (
            <div className="mb-4">
              <Select value={selectedVariant} onValueChange={setSelectedVariant}>
                <SelectTrigger className="w-full">
                  <SelectValue placeholder="Select variant" />
                </SelectTrigger>
                <SelectContent>
                  {product.variants.map(v => (
                    <SelectItem
                      key={v.shopify_id}
                      value={v.shopify_id}
                      disabled={!v.available}
                    >
                      {v.title} - ${v.price.toFixed(2)} {v.available ? '' : '(Out of Stock)'}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          )}
          <div className="flex justify-between items-center">
            <span className="text-2xl font-bold text-blue-600">
              ${Number(price).toFixed(2)}
            </span>
            <Button
              size="sm"
              className="bg-blue-600 hover:bg-blue-700 text-white"
              disabled={!selectedV?.available}
              onClick={() => {
                if (!selectedVariant) {
                  alert('Please select a variant.');
                  return;
                }
                addItem({
                  variant_id: selectedVariant,
                  quantity: 1,
                  // Optional: Include for display in CartPage
                  name: product.name + (selectedV.title !== "Default Title" ? ` (${selectedV.title})` : ""),
                  price: Number(price),
                  image: product.image,
                });
                alert(`${product.name} added to cart.`);
              }}
            >
              Add to Cart
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  };

  return (
    <div className="min-h-screen bg-white">
      <Navigation />

      {/* Promo Modal */}
      {showPromoModal && (
        <Dialog open={showPromoModal} onOpenChange={setShowPromoModal}>
          <DialogContent className="max-w-md">
            <div className="text-center p-6">
              <div className="bg-blue-600 text-white p-3 rounded-full w-16 h-16 mx-auto mb-4 flex items-center justify-center">
                <span className="text-2xl">🎯</span>
              </div>
              <DialogTitle className="text-2xl font-bold mb-2">
                Unlock $25 Off Your First Order
              </DialogTitle>
              <DialogDescription className="text-gray-600 mb-4">
                Sign up to get $25 off your first order and exclusive deals.
              </DialogDescription>
              <form onSubmit={handleNewsletterSignup}>
                <Input
                  type="email"
                  placeholder="Enter your email"
                  className="mb-4"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                />
                <Button type="submit" className="w-full mb-2 bg-blue-600 hover:bg-blue-700">
                  Get $25 Off
                </Button>
                <Button variant="ghost" onClick={() => setShowPromoModal(false)}>
                  No Thanks
                </Button>
              </form>
            </div>
          </DialogContent>
        </Dialog>
      )}

      {/* Hero Section */}
      <section className="bg-gradient-to-r from-blue-50 to-indigo-100 py-20">
        <div className="container mx-auto px-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            <div>
              <Badge className="mb-4 bg-blue-100 text-blue-800">Trusted by 50,000+ Creators</Badge>
              <h1 className="text-5xl font-bold text-gray-900 mb-6">
                Professional DTF Transfers & <span className="text-blue-600">Equipment</span>
              </h1>
              <p className="text-xl text-gray-600 mb-8">
                Create stunning custom apparel with premium DTF transfers and gear.
              </p>
              <Link to="/products">
                <Button size="lg" className="bg-blue-600 hover:bg-blue-700 text-white">
                  Shop Now <ArrowRight className="ml-2 h-5 w-5" />
                </Button>
              </Link>
            </div>
            <div>
              <img
                src="https://images.unsplash.com/photo-1556742049-0cfed4f6a45d?w=500&h=400&fit=crop"
                alt="Sample"
                className="rounded-lg shadow-xl"
              />
            </div>
          </div>
        </div>
      </section>

      {/* Featured Products */}
      <section className="py-20 bg-gray-50">
        <div className="container mx-auto px-4">
          <div className="text-center mb-12">
            <h2 className="text-4xl font-bold text-gray-900 mb-2">Featured Products</h2>
            <p className="text-lg text-gray-600">Our best sellers and customer favorites</p>
          </div>

          {loading ? (
            <p className="text-center text-gray-500">Loading products...</p>
          ) : products.length === 0 ? (
            <p className="text-center text-gray-500">No products available.</p>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
              {featuredProducts.map((product) => (
                <ProductCard key={product.shopify_id} product={product} />
              ))}
            </div>
          )}
        </div>
      </section>

      <Footer />
    </div>
  );
};

export default HomePage;