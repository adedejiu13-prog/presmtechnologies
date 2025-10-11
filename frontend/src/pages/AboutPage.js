import React from 'react';
import Navigation from '../components/Navigation';
import Footer from '../components/Footer';
import { Button } from '../components/ui/button';
import { Card, CardContent } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Star, Users, Award, Clock, Shield, Zap, Heart, Target } from 'lucide-react';
import { Link } from 'react-router-dom';

const AboutPage = () => {
  const stats = [
    { icon: Users, value: '50,000+', label: 'Happy Customers' },
    { icon: Award, value: '500K+', label: 'Transfers Printed' },
    { icon: Star, value: '4.9', label: 'Average Rating' },
    { icon: Clock, value: '24hrs', label: 'Average Turnaround' }
  ];

  const values = [
    {
      icon: Shield,
      title: 'Quality First',
      description: 'We use only premium materials and cutting-edge technology to ensure every transfer meets our high standards.'
    },
    {
      icon: Zap,
      title: 'Innovation',
      description: 'Our AI-powered gang sheet builder and advanced printing techniques keep us at the forefront of DTF technology.'
    },
    {
      icon: Heart,
      title: 'Customer Success',
      description: 'Your success is our mission. We provide comprehensive support to help your business thrive.'
    },
    {
      icon: Target,
      title: 'Precision',
      description: 'Every transfer is crafted with meticulous attention to detail, ensuring consistent, professional results.'
    }
  ];

  const team = [
    {
      name: 'Sarah Johnson',
      role: 'CEO & Founder',
      image: 'https://images.unsplash.com/photo-1494790108755-2616b612b786?w=300&h=300&fit=crop&crop=face',
      bio: '15+ years in printing industry, passionate about democratizing custom apparel.'
    },
    {
      name: 'Mike Chen',
      role: 'CTO',
      image: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=300&h=300&fit=crop&crop=face',
      bio: 'Tech visionary behind our AI gang sheet builder and automation systems.'
    },
    {
      name: 'Emily Rodriguez',
      role: 'Head of Operations',
      image: 'https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=300&h=300&fit=crop&crop=face',
      bio: 'Ensures every order meets our quality standards and ships on time.'
    }
  ];

  return (
    <div className="min-h-screen bg-white">
      <Navigation />
      
      {/* Hero Section */}
      <section className="py-20 bg-gradient-to-r from-blue-50 to-indigo-100">
        <div className="container mx-auto px-4 text-center">
          <h1 className="text-5xl font-bold text-gray-900 mb-6">
            Transforming Ideas Into 
            <span className="text-blue-600"> Stunning Apparel</span>
          </h1>
          <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
            PRESM Technologies is the leading provider of direct-to-film transfers and heat press equipment, 
            trusted by creators, entrepreneurs, and businesses worldwide to bring their visions to life.
          </p>
          <div className="flex flex-col sm:flex-row justify-center space-y-4 sm:space-y-0 sm:space-x-4">
            <Link to="/products">
              <Button size="lg" className="bg-blue-600 hover:bg-blue-700">
                Explore Products
              </Button>
            </Link>
            <Link to="/contact">
              <Button size="lg" variant="outline" className="border-blue-600 text-blue-600 hover:bg-blue-50">
                Contact Us
              </Button>
            </Link>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-16 bg-white">
        <div className="container mx-auto px-4">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            {stats.map((stat, index) => (
              <div key={index} className="text-center">
                <div className="flex justify-center mb-4">
                  <stat.icon className="h-12 w-12 text-blue-600" />
                </div>
                <div className="text-4xl font-bold text-gray-900 mb-2">{stat.value}</div>
                <div className="text-gray-600">{stat.label}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Story Section */}
      <section className="py-20 bg-gray-50">
        <div className="container mx-auto px-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            <div>
              <h2 className="text-4xl font-bold text-gray-900 mb-6">Our Story</h2>
              <p className="text-gray-600 text-lg mb-6">
                Founded in 2019, PRESM Technologies began with a simple mission: make professional-quality 
                custom apparel accessible to everyone. We saw creators struggling with expensive minimums, 
                complex processes, and inconsistent quality.
              </p>
              <p className="text-gray-600 text-lg mb-6">
                Today, we've revolutionized the DTF transfer industry with our AI-powered gang sheet builder, 
                premium materials, and commitment to customer success. From solo entrepreneurs to large 
                enterprises, we empower creators to bring their ideas to life with confidence.
              </p>
              <div className="space-y-3">
                <div className="flex items-center">
                  <div className="w-2 h-2 bg-blue-600 rounded-full mr-3"></div>
                  <span className="text-gray-700">First to market with AI gang sheet optimization</span>
                </div>
                <div className="flex items-center">
                  <div className="w-2 h-2 bg-blue-600 rounded-full mr-3"></div>
                  <span className="text-gray-700">Over 500,000 transfers printed and shipped</span>
                </div>
                <div className="flex items-center">
                  <div className="w-2 h-2 bg-blue-600 rounded-full mr-3"></div>
                  <span className="text-gray-700">Trusted by businesses in 50+ countries</span>
                </div>
              </div>
            </div>
            <div className="relative">
              <img 
                src="https://images.unsplash.com/photo-1556742049-0cfed4f6a45d?w=600&h=500&fit=crop"
                alt="PRESM Technologies facility"
                className="rounded-2xl shadow-xl"
              />
              <div className="absolute -bottom-6 -left-6 bg-white p-6 rounded-xl shadow-lg">
                <div className="flex items-center space-x-2 mb-2">
                  {[1,2,3,4,5].map((star) => (
                    <Star key={star} className="h-5 w-5 fill-yellow-400 text-yellow-400" />
                  ))}
                </div>
                <p className="text-sm font-semibold">4.9/5 Customer Rating</p>
                <p className="text-xs text-gray-600">Based on 15,000+ reviews</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Values Section */}
      <section className="py-20 bg-white">
        <div className="container mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">Our Values</h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              The principles that guide everything we do at PRESM Technologies
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            {values.map((value, index) => (
              <Card key={index} className="text-center p-6 hover:shadow-lg transition-shadow">
                <CardContent className="p-0">
                  <div className="bg-blue-100 rounded-full p-4 w-16 h-16 mx-auto mb-4 flex items-center justify-center">
                    <value.icon className="h-8 w-8 text-blue-600" />
                  </div>
                  <h3 className="font-semibold text-lg mb-3">{value.title}</h3>
                  <p className="text-gray-600 text-sm">{value.description}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Team Section */}
      <section className="py-20 bg-gray-50">
        <div className="container mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">Meet Our Team</h2>
            <p className="text-xl text-gray-600">
              The passionate people behind PRESM Technologies
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {team.map((member, index) => (
              <Card key={index} className="text-center p-6 hover:shadow-lg transition-shadow">
                <CardContent className="p-0">
                  <img 
                    src={member.image} 
                    alt={member.name}
                    className="w-24 h-24 rounded-full mx-auto mb-4 object-cover"
                  />
                  <h3 className="font-semibold text-lg mb-1">{member.name}</h3>
                  <Badge variant="outline" className="mb-3">{member.role}</Badge>
                  <p className="text-gray-600 text-sm">{member.bio}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Mission Section */}
      <section className="py-20 bg-blue-600 text-white">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-4xl font-bold mb-6">Our Mission</h2>
          <p className="text-xl mb-8 max-w-4xl mx-auto">
            To democratize custom apparel creation by providing professional-grade DTF transfers, 
            innovative tools, and exceptional support that empowers creators to turn their ideas 
            into successful businesses.
          </p>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="bg-blue-700 rounded-lg p-6">
              <h3 className="font-semibold text-lg mb-3">Accessibility</h3>
              <p className="text-blue-100">No minimums, fair pricing, and user-friendly tools for creators of all sizes.</p>
            </div>
            <div className="bg-blue-700 rounded-lg p-6">
              <h3 className="font-semibold text-lg mb-3">Innovation</h3>
              <p className="text-blue-100">Cutting-edge technology that simplifies complex processes and maximizes efficiency.</p>
            </div>
            <div className="bg-blue-700 rounded-lg p-6">
              <h3 className="font-semibold text-lg mb-3">Partnership</h3>
              <p className="text-blue-100">We're not just a supplier - we're your partner in creative and business success.</p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-gradient-to-r from-blue-50 to-indigo-100">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-4xl font-bold text-gray-900 mb-4">
            Ready to Create Something Amazing?
          </h2>
          <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
            Join thousands of creators who trust PRESM Technologies for their DTF transfer needs.
          </p>
          <div className="flex flex-col sm:flex-row justify-center space-y-4 sm:space-y-0 sm:space-x-4">
            <Link to="/gang-sheet-builder">
              <Button size="lg" className="bg-blue-600 hover:bg-blue-700">
                Try Gang Sheet Builder
              </Button>
            </Link>
            <Link to="/products">
              <Button size="lg" variant="outline" className="border-blue-600 text-blue-600 hover:bg-blue-50">
                Browse Products
              </Button>
            </Link>
          </div>
        </div>
      </section>

      <Footer />
    </div>
  );
};

export default AboutPage;