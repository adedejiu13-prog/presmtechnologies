import React from 'react';
import { Link } from 'react-router-dom';
import { Facebook, Instagram, Twitter, Youtube, Mail, Phone, MapPin } from 'lucide-react';

const Footer = () => {
  return (
    <footer className="bg-gray-900 text-white">
      <div className="container mx-auto px-4 py-12">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
          {/* Company Info */}
          <div>
            <div className="flex items-center space-x-2 mb-4">
              <div className="bg-blue-600 text-white p-2 rounded-lg font-bold text-xl">
                PRESM
              </div>
              <div>
                <span className="font-semibold text-lg">PRESM</span>
                <span className="text-blue-400 ml-1">Technologies</span>
              </div>
            </div>
            <p className="text-gray-300 mb-4">
              Leading provider of direct-to-film transfers and heat press equipment. 
              Empowering creators with professional-grade tools and exceptional service.
            </p>
            <div className="flex space-x-4">
              <Facebook className="h-5 w-5 hover:text-blue-400 cursor-pointer transition-colors" />
              <Instagram className="h-5 w-5 hover:text-pink-400 cursor-pointer transition-colors" />
              <Twitter className="h-5 w-5 hover:text-blue-400 cursor-pointer transition-colors" />
              <Youtube className="h-5 w-5 hover:text-red-400 cursor-pointer transition-colors" />
            </div>
          </div>

          {/* Products */}
          <div>
            <h3 className="font-semibold text-lg mb-4">Products</h3>
            <ul className="space-y-2">
              <li><Link to="/products/dtf-transfers" className="text-gray-300 hover:text-white transition-colors">DTF Transfers</Link></li>
              <li><Link to="/products/gang-sheets" className="text-gray-300 hover:text-white transition-colors">Gang Sheets</Link></li>
              <li><Link to="/products/heat-presses" className="text-gray-300 hover:text-white transition-colors">Heat Press Machines</Link></li>
              <li><Link to="/products/accessories" className="text-gray-300 hover:text-white transition-colors">Accessories</Link></li>
              <li><Link to="/products/supplies" className="text-gray-300 hover:text-white transition-colors">Supplies</Link></li>
              <li><Link to="/gang-sheet-builder" className="text-gray-300 hover:text-white transition-colors">Gang Sheet Builder</Link></li>
            </ul>
          </div>

          {/* Support */}
          <div>
            <h3 className="font-semibold text-lg mb-4">Support</h3>
            <ul className="space-y-2">
              <li><Link to="/education" className="text-gray-300 hover:text-white transition-colors">Education Center</Link></li>
              <li><Link to="/education/heat-press-guide" className="text-gray-300 hover:text-white transition-colors">Heat Press Instructions</Link></li>
              <li><Link to="/education/design-tips" className="text-gray-300 hover:text-white transition-colors">Design Tips</Link></li>
              <li><Link to="/contact" className="text-gray-300 hover:text-white transition-colors">Contact Support</Link></li>
              <li><Link to="/shipping" className="text-gray-300 hover:text-white transition-colors">Shipping Info</Link></li>
              <li><Link to="/returns" className="text-gray-300 hover:text-white transition-colors">Returns</Link></li>
            </ul>
          </div>

          {/* Contact */}
          <div>
            <h3 className="font-semibold text-lg mb-4">Contact Us</h3>
            <div className="space-y-3">
              <div className="flex items-center">
                <Phone className="h-5 w-5 mr-3 text-blue-400" />
                <span className="text-gray-300">888-PRESM-01</span>
              </div>
              <div className="flex items-center">
                <Mail className="h-5 w-5 mr-3 text-blue-400" />
                <span className="text-gray-300">support@presmtech.com</span>
              </div>
              <div className="flex items-start">
                <MapPin className="h-5 w-5 mr-3 mt-1 text-blue-400" />
                <span className="text-gray-300">
                  123 Innovation Drive<br />
                  Tech Valley, CA 94043
                </span>
              </div>
            </div>
            
            {/* Newsletter Signup */}
            <div className="mt-6">
              <h4 className="font-medium mb-2">Newsletter</h4>
              <div className="flex">
                <input 
                  type="email" 
                  placeholder="Your email" 
                  className="bg-gray-800 text-white px-3 py-2 rounded-l-md flex-1 focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                <button className="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded-r-md transition-colors">
                  Subscribe
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Bottom Bar */}
        <div className="border-t border-gray-800 mt-8 pt-8 flex flex-col md:flex-row justify-between items-center">
          <p className="text-gray-400 text-sm">
            © 2024 PRESM Technologies. All rights reserved.
          </p>
          <div className="flex space-x-6 mt-4 md:mt-0">
            <Link to="/privacy" className="text-gray-400 hover:text-white text-sm transition-colors">Privacy Policy</Link>
            <Link to="/terms" className="text-gray-400 hover:text-white text-sm transition-colors">Terms of Service</Link>
            <Link to="/cookies" className="text-gray-400 hover:text-white text-sm transition-colors">Cookie Policy</Link>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;