import React, { useState } from 'react';
import Navigation from '../components/Navigation';
import Footer from '../components/Footer';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Input } from '../components/ui/input';
import { Textarea } from '../components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { Phone, Mail, MapPin, Clock, MessageCircle, HelpCircle, Truck } from 'lucide-react';
import { useToast } from '../hooks/use-toast';

const ContactPage = () => {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    subject: '',
    category: '',
    message: ''
  });
  const { toast } = useToast();

  const handleSubmit = (e) => {
    e.preventDefault();
    // Mock form submission
    toast({
      title: "Message Sent!",
      description: "We'll get back to you within 24 hours.",
    });
    setFormData({
      name: '',
      email: '',
      subject: '',
      category: '',
      message: ''
    });
  };

  const handleInputChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const contactMethods = [
    {
      icon: Phone,
      title: 'Phone Support',
      details: '888-PRESM-01',
      description: 'Mon-Fri, 8AM-6PM PST',
      action: 'Call Now'
    },
    {
      icon: Mail,
      title: 'Email Support',
      details: 'support@presmtech.com',
      description: 'We respond within 4 hours',
      action: 'Send Email'
    },
    {
      icon: MessageCircle,
      title: 'Live Chat',
      details: 'Chat with our team',
      description: 'Available 24/7',
      action: 'Start Chat'
    }
  ];

  const faqCategories = [
    {
      icon: HelpCircle,
      title: 'General Questions',
      items: [
        'What is DTF printing?',
        'How do I place an order?',
        'What file formats do you accept?',
        'Do you offer rush orders?'
      ]
    },
    {
      icon: Truck,
      title: 'Shipping & Orders',
      items: [
        'What are your shipping times?',
        'Do you ship internationally?',
        'How do I track my order?',
        'What is your return policy?'
      ]
    }
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      <Navigation />
      
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            Contact PRESM Technologies
          </h1>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Have questions about our DTF transfers or need support? 
            We're here to help you succeed.
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-12">
          {/* Contact Methods */}
          <div className="lg:col-span-1 space-y-6">
            {contactMethods.map((method, index) => (
              <Card key={index} className="hover:shadow-lg transition-shadow">
                <CardContent className="p-6 text-center">
                  <div className="bg-blue-100 rounded-full p-4 w-16 h-16 mx-auto mb-4 flex items-center justify-center">
                    <method.icon className="h-8 w-8 text-blue-600" />
                  </div>
                  <h3 className="font-semibold text-lg mb-2">{method.title}</h3>
                  <div className="text-blue-600 font-medium mb-1">{method.details}</div>
                  <p className="text-gray-600 text-sm mb-4">{method.description}</p>
                  <Button variant="outline" className="w-full border-blue-600 text-blue-600 hover:bg-blue-50">
                    {method.action}
                  </Button>
                </CardContent>
              </Card>
            ))}

            {/* Business Hours */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Clock className="mr-2 h-5 w-5" />
                  Business Hours
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-gray-600">Monday - Friday</span>
                  <span className="font-medium">8:00 AM - 6:00 PM PST</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Saturday</span>
                  <span className="font-medium">9:00 AM - 4:00 PM PST</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Sunday</span>
                  <span className="font-medium">Closed</span>
                </div>
              </CardContent>
            </Card>

            {/* Location */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <MapPin className="mr-2 h-5 w-5" />
                  Our Location
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-600 mb-4">
                  123 Innovation Drive<br />
                  Tech Valley, CA 94043<br />
                  United States
                </p>
                <Button variant="outline" className="w-full">
                  Get Directions
                </Button>
              </CardContent>
            </Card>
          </div>

          {/* Contact Form */}
          <div className="lg:col-span-2">
            <Card>
              <CardHeader>
                <CardTitle>Send us a Message</CardTitle>
                <p className="text-gray-600">
                  Fill out the form below and we'll get back to you as soon as possible.
                </p>
              </CardHeader>
              <CardContent>
                <form onSubmit={handleSubmit} className="space-y-6">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="text-sm font-medium mb-2 block">Name *</label>
                      <Input
                        required
                        value={formData.name}
                        onChange={(e) => handleInputChange('name', e.target.value)}
                        placeholder="Your full name"
                      />
                    </div>
                    <div>
                      <label className="text-sm font-medium mb-2 block">Email *</label>
                      <Input
                        type="email"
                        required
                        value={formData.email}
                        onChange={(e) => handleInputChange('email', e.target.value)}
                        placeholder="your@email.com"
                      />
                    </div>
                  </div>

                  <div>
                    <label className="text-sm font-medium mb-2 block">Category</label>
                    <Select value={formData.category} onValueChange={(value) => handleInputChange('category', value)}>
                      <SelectTrigger>
                        <SelectValue placeholder="Select a category" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="general">General Inquiry</SelectItem>
                        <SelectItem value="technical">Technical Support</SelectItem>
                        <SelectItem value="orders">Order Support</SelectItem>
                        <SelectItem value="billing">Billing Question</SelectItem>
                        <SelectItem value="partnership">Partnership</SelectItem>
                        <SelectItem value="feedback">Feedback</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div>
                    <label className="text-sm font-medium mb-2 block">Subject *</label>
                    <Input
                      required
                      value={formData.subject}
                      onChange={(e) => handleInputChange('subject', e.target.value)}
                      placeholder="Brief description of your inquiry"
                    />
                  </div>

                  <div>
                    <label className="text-sm font-medium mb-2 block">Message *</label>
                    <Textarea
                      required
                      value={formData.message}
                      onChange={(e) => handleInputChange('message', e.target.value)}
                      placeholder="Tell us more about how we can help you..."
                      className="min-h-[120px]"
                    />
                  </div>

                  <Button type="submit" size="lg" className="w-full bg-blue-600 hover:bg-blue-700">
                    Send Message
                  </Button>

                  <p className="text-sm text-gray-500 text-center">
                    We typically respond within 4 hours during business hours.
                  </p>
                </form>
              </CardContent>
            </Card>
          </div>
        </div>

        {/* FAQ Section */}
        <Card>
          <CardHeader>
            <CardTitle>Frequently Asked Questions</CardTitle>
            <p className="text-gray-600">
              Quick answers to common questions about our products and services.
            </p>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              {faqCategories.map((category, index) => (
                <div key={index}>
                  <div className="flex items-center mb-4">
                    <category.icon className="h-5 w-5 text-blue-600 mr-2" />
                    <h3 className="font-semibold text-lg">{category.title}</h3>
                  </div>
                  <div className="space-y-2">
                    {category.items.map((item, itemIndex) => (
                      <div key={itemIndex} className="text-gray-600 hover:text-blue-600 cursor-pointer transition-colors">
                        • {item}
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>

            <div className="text-center mt-8">
              <Button variant="outline" className="border-blue-600 text-blue-600 hover:bg-blue-50">
                View All FAQs
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>

      <Footer />
    </div>
  );
};

export default ContactPage;