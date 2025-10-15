import React, { useState } from 'react';
import Navigation from '../components/Navigation';
import Footer from '../components/Footer';
import { Button } from '../components/ui/button';
import { Card, CardContent } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Input } from '../components/ui/input';
import { Star, ArrowRight, Check, Zap, Shield, Truck, Clock, Users, Award, Play } from 'lucide-react';
import { Link } from 'react-router-dom';
import { Dialog, DialogContent, DialogTrigger, DialogTitle, DialogDescription } from '../components/ui/dialog';
import { products, testimonials } from '../data/mockData';
import { useCart } from '../context/CartContext';
import { useToast } from '../hooks/use-toast';

const HomePage = () => {
  const [email, setEmail] = useState('');
  const [showPromoModal, setShowPromoModal] = useState(true);
  const { addItem } = useCart();
  const { toast } = useToast();

  const handleNewsletterSignup = (e) => {
    e.preventDefault();
    toast({
      title: "Success!",
      description: "You've been subscribed to our newsletter.",
    });
    setEmail('');
  };

  const featuredProducts = products.slice(0, 4);

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
              <DialogTitle className="text-2xl font-bold mb-2">Unlock $25 Off Your First Order</DialogTitle>
              <DialogDescription className="text-gray-600 mb-4">
                Sign up and we'll send you a coupon code for $25 off your first order and other exclusive deals.
              </DialogDescription>
              <Input
                type="email"
                placeholder="Enter your email"
                className="mb-4"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
              <Button className="w-full mb-2 bg-blue-600 hover:bg-blue-700">
                Get $25 Off
              </Button>
              <Button variant="ghost" onClick={() => setShowPromoModal(false)}>
                No Thanks
              </Button>
            </div>
          </DialogContent>
        </Dialog>
      )}

      {/* Hero Section */}
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
                  {[1,2,3,4,5].map((star) => (
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
                  <Button size="lg" variant="outline" className="border-blue-600 text-blue-600 hover:bg-blue-50 px-8 py-3">
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

      {/* Features Section */}
      <section className="py-20 bg-white">
        <div className="container mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">
              Why Choose PRESM Technologies?
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              We combine cutting-edge technology with exceptional service to deliver 
              the best DTF transfer experience in the industry.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            <Card className="text-center p-6 hover:shadow-lg transition-shadow">
              <CardContent className="p-0">
                <div className="bg-blue-100 rounded-full p-4 w-16 h-16 mx-auto mb-4 flex items-center justify-center">
                  <Zap className="h-8 w-8 text-blue-600" />
                </div>
                <h3 className="font-semibold text-lg mb-2">AI-Powered Builder</h3>
                <p className="text-gray-600">
                  Smart gang sheet optimization with automatic nesting and cost calculation.
                </p>
              </CardContent>
            </Card>

            <Card className="text-center p-6 hover:shadow-lg transition-shadow">
              <CardContent className="p-0">
                <div className="bg-green-100 rounded-full p-4 w-16 h-16 mx-auto mb-4 flex items-center justify-center">
                  <Shield className="h-8 w-8 text-green-600" />
                </div>
                <h3 className="font-semibold text-lg mb-2">Premium Quality</h3>
                <p className="text-gray-600">
                  Professional-grade materials with industry-leading color vibrancy and durability.
                </p>
              </CardContent>
            </Card>

            <Card className="text-center p-6 hover:shadow-lg transition-shadow">
              <CardContent className="p-0">
                <div className="bg-purple-100 rounded-full p-4 w-16 h-16 mx-auto mb-4 flex items-center justify-center">
                  <Clock className="h-8 w-8 text-purple-600" />
                </div>
                <h3 className="font-semibold text-lg mb-2">Fast Turnaround</h3>
                <p className="text-gray-600">
                  Most orders ship within 1-2 business days with rush options available.
                </p>
              </CardContent>
            </Card>

            <Card className="text-center p-6 hover:shadow-lg transition-shadow">
              <CardContent className="p-0">
                <div className="bg-orange-100 rounded-full p-4 w-16 h-16 mx-auto mb-4 flex items-center justify-center">
                  <Truck className="h-8 w-8 text-orange-600" />
                </div>
                <h3 className="font-semibold text-lg mb-2">Free Shipping</h3>
                <p className="text-gray-600">
                  Free shipping on orders over $75 with tracking included on all orders.
                </p>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* Featured Products */}
      <section className="py-20 bg-gray-50">
        <div className="container mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">
              Featured Products
            </h2>
            <p className="text-xl text-gray-600">
              Our most popular DTF transfers and equipment
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            {featuredProducts.map((product) => (
              <Card key={product.id} className="overflow-hidden hover:shadow-lg transition-shadow">
                <div className="relative">
                  <img 
                    src={product.image} 
                    alt={product.name}
                    className="w-full h-48 object-cover"
                  />
                  <Badge className="absolute top-2 right-2 bg-blue-600">
                    Popular
                  </Badge>
                </div>
                <CardContent className="p-6">
                  <h3 className="font-semibold text-lg mb-2">{product.name}</h3>
                  <p className="text-gray-600 text-sm mb-4">{product.description}</p>
                  <div className="flex justify-between items-center">
                    <span className="text-2xl font-bold text-blue-600">
                      ${product.price}
                    </span>
                    <Button 
                      size="sm"
                      onClick={() => {
                        addItem({
                          ...product,
                          quantity: 1,
                          options: { size: product.sizes[0] }
                        });
                        toast({
                          title: "Added to Cart",
                          description: `${product.name} added successfully.`,
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

          <div className="text-center mt-12">
            <Link to="/products">
              <Button size="lg" variant="outline" className="border-blue-600 text-blue-600 hover:bg-blue-50">
                View All Products
                <ArrowRight className="ml-2 h-5 w-5" />
              </Button>
            </Link>
          </div>
        </div>
      </section>

      {/* Testimonials */}
      <section className="py-20 bg-white">
        <div className="container mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">
              Trusted by Creators Worldwide
            </h2>
            <p className="text-xl text-gray-600">
              See what our customers are saying about PRESM Technologies
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {testimonials.map((testimonial) => (
              <Card key={testimonial.id} className="p-6">
                <CardContent className="p-0">
                  <div className="flex items-center mb-4">
                    {[1,2,3,4,5].map((star) => (
                      <Star key={star} className="h-4 w-4 fill-yellow-400 text-yellow-400" />
                    ))}
                  </div>
                  <p className="text-gray-700 mb-4 italic">"{testimonial.text}"</p>
                  <div className="flex items-center">
                    <img 
                      src={testimonial.avatar} 
                      alt={testimonial.name}
                      className="w-10 h-10 rounded-full mr-3"
                    />
                    <div>
                      <h4 className="font-semibold">{testimonial.name}</h4>
                      <p className="text-sm text-gray-600">{testimonial.business}</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-20 bg-blue-600 text-white">
        <div className="container mx-auto px-4">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8 text-center">
            <div>
              <div className="flex items-center justify-center mb-4">
                <Users className="h-8 w-8 mr-2" />
                <span className="text-4xl font-bold">50K+</span>
              </div>
              <p className="text-blue-100">Happy Customers</p>
            </div>
            <div>
              <div className="flex items-center justify-center mb-4">
                <Award className="h-8 w-8 mr-2" />
                <span className="text-4xl font-bold">500K+</span>
              </div>
              <p className="text-blue-100">Transfers Printed</p>
            </div>
            <div>
              <div className="flex items-center justify-center mb-4">
                <Star className="h-8 w-8 mr-2" />
                <span className="text-4xl font-bold">4.9</span>
              </div>
              <p className="text-blue-100">Average Rating</p>
            </div>
            <div>
              <div className="flex items-center justify-center mb-4">
                <Clock className="h-8 w-8 mr-2" />
                <span className="text-4xl font-bold">24hrs</span>
              </div>
              <p className="text-blue-100">Average Turnaround</p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-gradient-to-r from-blue-50 to-indigo-100">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-4xl font-bold text-gray-900 mb-4">
            Ready to Start Creating?
          </h2>
          <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
            Join thousands of creators who trust PRESM Technologies for their 
            DTF transfer and heat press equipment needs.
          </p>
          
          <div className="flex flex-col sm:flex-row justify-center space-y-4 sm:space-y-0 sm:space-x-4 mb-12">
            <Link to="/gang-sheet-builder">
              <Button size="lg" className="bg-blue-600 hover:bg-blue-700 text-white px-8 py-3">
                <Zap className="mr-2 h-5 w-5" />
                Try Gang Sheet Builder
              </Button>
            </Link>
            <Link to="/products">
              <Button size="lg" variant="outline" className="border-blue-600 text-blue-600 hover:bg-blue-50 px-8 py-3">
                Browse Products
                <ArrowRight className="ml-2 h-5 w-5" />
              </Button>
            </Link>
          </div>

          <form onSubmit={handleNewsletterSignup} className="max-w-md mx-auto flex space-x-2">
            <Input
              type="email"
              placeholder="Enter your email for updates"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className="flex-1"
            />
            <Button type="submit" className="bg-blue-600 hover:bg-blue-700">
              Subscribe
            </Button>
          </form>
        </div>
      </section>

      <Footer />
    </div>
  );
};

export default HomePage;