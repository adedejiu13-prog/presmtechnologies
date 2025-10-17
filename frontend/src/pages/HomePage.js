import React, { useState, useEffect } from 'react';
import Navigation from '../components/Navigation';
import Footer from '../components/Footer';
import { Button } from '../components/ui/button';
import { Card, CardContent } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Input } from '../components/ui/input';
import { Star, ArrowRight, Check, Zap, Shield, Truck, Clock } from 'lucide-react';
import { Link } from 'react-router-dom';
import { Dialog, DialogContent, DialogTitle, DialogDescription } from '../components/ui/dialog';
import { useCart } from '../context/CartContext';
import { useToast } from '../hooks/use-toast';

const HomePage = () => {
  const [email, setEmail] = useState('');
  const [showPromoModal, setShowPromoModal] = useState(true);
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const { addItem } = useCart();
  const { toast } = useToast();

  // ✅ Fetch Shopify products safely
  useEffect(() => {
    const fetchProducts = async () => {
      try {
        const response = await fetch(
          'https://presmtechnologies.onrender.com/api/shopify/products'
        );
        if (!response.ok) throw new Error('Failed to fetch products');
        const data = await response.json();

        // Ensure it's an array
        const productsArray = Array.isArray(data)
          ? data
          : data.products || [];

        setProducts(productsArray);
      } catch (error) {
        console.error('Error fetching Shopify products:', error);
        setProducts([]);
      } finally {
        setLoading(false);
      }
    };

    fetchProducts();
  }, []);

  const handleNewsletterSignup = (e) => {
    e.preventDefault();
    toast({
      title: 'Success!',
      description: "You've been subscribed to our newsletter.",
    });
    setEmail('');
  };

  const featuredProducts = Array.isArray(products)
    ? products.slice(0, 4)
    : [];

  return (
    <div className="min-h-screen bg-white">
      <Navigation />

      {/* 🟦 Promo Modal */}
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
                Sign up and we'll send you a coupon code for $25 off your first order and other exclusive deals.
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

      {/* 🟨 Hero Section */}
      <section className="bg-gradient-to-r from-blue-50 to-indigo-100 py-20">
        <div className="container mx-auto px-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            <div>
              <Badge className="mb-4 bg-blue-100 text-blue-800 hover:bg-blue-200">
                Trusted by 50,000+ Creators
              </Badge>
              <h1 className="text-5xl font-bold text-gray-900 leading-tight mb-6">
                Professional DTF Transfers &
                <span className="text-blue-600"> Heat Press Equipment</span>
              </h1>
              <p className="text-xl text-gray-600 mb-8 leading-relaxed">
                Create stunning custom apparel with our premium direct-to-film transfers,
                professional heat press equipment, and AI-powered gang sheet builder.
              </p>

              <div className="flex items-center space-x-4 mb-8">
                <div className="flex items-center">
                  {[1, 2, 3, 4, 5].map((star) => (
                    <Star key={star} className="h-5 w-5 fill-yellow-400 text-yellow-400" />
                  ))}
                  <span className="ml-2 font-semibold">4.9</span>
                </div>
                <span className="text-gray-500">Based on 15,000+ Reviews</span>
              </div>

              <div className="flex flex-col sm:flex-row space-y-4 sm:space-y-0 sm:space-x-4 mb-8">
                <Link to="/products">
                  <Button size="lg" className="bg-blue-600 hover:bg-blue-700 text-white px-8 py-3">
                    Shop DTF Transfers
                    <ArrowRight className="ml-2 h-5 w-5" />
                  </Button>
                </Link>
                <Link to="/gang-sheet-builder">
                  <Button
                    size="lg"
                    variant="outline"
                    className="border-blue-600 text-blue-600 hover:bg-blue-50 px-8 py-3"
                  >
                    <Zap className="mr-2 h-5 w-5" />
                    Build Gang Sheet
                  </Button>
                </Link>
              </div>

              <div className="flex items-center space-x-6 text-sm text-gray-600">
                <div className="flex items-center">
                  <Check className="h-4 w-4 text-green-500 mr-1" />
                  100% Satisfaction Guarantee
                </div>
                <div className="flex items-center">
                  <Check className="h-4 w-4 text-green-500 mr-1" />
                  No Minimums
                </div>
                <div className="flex items-center">
                  <Check className="h-4 w-4 text-green-500 mr-1" />
                  Fast Turnaround
                </div>
              </div>
            </div>

            <div className="relative">
              <div className="bg-white rounded-2xl shadow-xl p-8 transform rotate-3 hover:rotate-0 transition-transform duration-300">
                <img
                  src="https://images.unsplash.com/photo-1556742049-0cfed4f6a45d?w=500&h=400&fit=crop"
                  alt="DTF Transfer Sample"
                  className="rounded-lg w-full h-80 object-cover"
                />
                <div className="mt-4">
                  <h3 className="font-semibold text-lg">Premium DTF Quality</h3>
                  <p className="text-gray-600">Vibrant colors, excellent durability</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* 🟩 Featured Products Section */}
      <section className="py-20 bg-gray-50">
        <div className="container mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">Featured Products</h2>
            <p className="text-xl text-gray-600">
              Our most popular DTF transfers and equipment
            </p>
          </div>

          {loading ? (
            <p className="text-center text-gray-500">Loading products...</p>
          ) : products.length === 0 ? (
            <p className="text-center text-gray-500">No products found.</p>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
              {featuredProducts.map((product) => (
                <Card
                  key={product.shopify_id || product.id}
                  className="overflow-hidden hover:shadow-lg transition-shadow"
                >
                  <div className="relative">
                    <img
                      src={product.image || product.images?.[0]?.src}
                      alt={product.title || product.name}
                      className="w-full h-48 object-cover"
                    />
                    <Badge className="absolute top-2 right-2 bg-blue-600">Popular</Badge>
                  </div>
                  <CardContent className="p-6">
                    <h3 className="font-semibold text-lg mb-2">
                      {product.title || product.name}
                    </h3>
                    <p className="text-gray-600 text-sm mb-4">
                      {product.body_html?.replace(/<[^>]+>/g, '').slice(0, 100) ||
                        'High-quality DTF product.'}
                    </p>
                    <div className="flex justify-between items-center">
                      <span className="text-2xl font-bold text-blue-600">
                        ${product.variants?.[0]?.price || product.price || '0.00'}
                      </span>
                      <Button
                        size="sm"
                        onClick={() => {
                          addItem({
                            ...product,
                            quantity: 1,
                            options: { size: product.sizes?.[0] || 'Default' },
                          });
                          toast({
                            title: 'Added to Cart',
                            description: `${product.title || product.name} added successfully.`,
                          });
                        }}
                      >
                        Add to Cart
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}

          <div className="text-center mt-12">
            <Link to="/products">
              <Button
                size="lg"
                variant="outline"
                className="border-blue-600 text-blue-600 hover:bg-blue-50"
              >
                View All Products
                <ArrowRight className="ml-2 h-5 w-5" />
              </Button>
            </Link>
          </div>
        </div>
      </section>

      <Footer />
    </div>
  );
};

export default HomePage;
