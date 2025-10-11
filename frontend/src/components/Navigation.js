import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { ShoppingCart, Menu, X, Search, User, Phone } from 'lucide-react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { useCart } from '../context/CartContext';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "./ui/dropdown-menu";

const Navigation = () => {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const location = useLocation();
  const { getTotalItems } = useCart();
  
  const isActive = (path) => location.pathname === path;
  
  return (
    <nav className="bg-white shadow-sm border-b sticky top-0 z-50">
      {/* Top Bar */}
      <div className="bg-blue-600 text-white text-sm">
        <div className="container mx-auto px-4 py-2 flex justify-between items-center">
          <div className="flex items-center space-x-4">
            <span>Free Shipping on Orders Over $75</span>
          </div>
          <div className="flex items-center space-x-4">
            <div className="flex items-center">
              <Phone className="h-4 w-4 mr-1" />
              <span>888-PRESM-01</span>
            </div>
            <span>Support</span>
          </div>
        </div>
      </div>
      
      {/* Main Navigation */}
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center space-x-2">
            <div className="bg-blue-600 text-white p-2 rounded-lg font-bold text-xl">
              PRESM
            </div>
            <div className="text-gray-700">
              <span className="font-semibold text-lg">PRESM</span>
              <span className="text-blue-600 ml-1">Technologies</span>
            </div>
          </Link>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center space-x-8">
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button 
                  variant="ghost" 
                  className={`hover:text-blue-600 ${isActive('/products') ? 'text-blue-600' : ''}`}
                >
                  DTF Transfers
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent>
                <DropdownMenuItem asChild>
                  <Link to="/products/dtf-transfers">Standard DTF Transfers</Link>
                </DropdownMenuItem>
                <DropdownMenuItem asChild>
                  <Link to="/products/gang-sheets">Gang Sheets</Link>
                </DropdownMenuItem>
                <DropdownMenuItem asChild>
                  <Link to="/products/custom-designs">Custom Designs</Link>
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>

            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" className="hover:text-blue-600">
                  Heat Press Equipment
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent>
                <DropdownMenuItem asChild>
                  <Link to="/products/heat-presses">Heat Press Machines</Link>
                </DropdownMenuItem>
                <DropdownMenuItem asChild>
                  <Link to="/products/accessories">Accessories</Link>
                </DropdownMenuItem>
                <DropdownMenuItem asChild>
                  <Link to="/products/supplies">Supplies</Link>
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>

            <Link 
              to="/gang-sheet-builder" 
              className={`hover:text-blue-600 transition-colors ${isActive('/gang-sheet-builder') ? 'text-blue-600' : ''}`}
            >
              Gang Sheet Builder
            </Link>
            <Link 
              to="/education" 
              className={`hover:text-blue-600 transition-colors ${isActive('/education') ? 'text-blue-600' : ''}`}
            >
              Education
            </Link>
            <Link 
              to="/about" 
              className={`hover:text-blue-600 transition-colors ${isActive('/about') ? 'text-blue-600' : ''}`}
            >
              About
            </Link>
          </div>

          {/* Search Bar */}
          <div className="hidden md:flex items-center space-x-4">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              <Input
                type="text"
                placeholder="Search products..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10 w-64"
              />
            </div>
          </div>

          {/* Right Side Actions */}
          <div className="flex items-center space-x-4">
            <Button variant="ghost" size="sm">
              <User className="h-5 w-5" />
              <span className="ml-1 hidden md:inline">Account</span>
            </Button>
            
            <Link to="/cart">
              <Button variant="ghost" size="sm" className="relative">
                <ShoppingCart className="h-5 w-5" />
                {getTotalItems() > 0 && (
                  <span className="absolute -top-2 -right-2 bg-blue-600 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center">
                    {getTotalItems()}
                  </span>
                )}
                <span className="ml-1 hidden md:inline">Cart</span>
              </Button>
            </Link>

            {/* Mobile Menu Button */}
            <Button
              variant="ghost"
              size="sm"
              className="md:hidden"
              onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
            >
              {isMobileMenuOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
            </Button>
          </div>
        </div>

        {/* Mobile Menu */}
        {isMobileMenuOpen && (
          <div className="md:hidden pb-4">
            <div className="space-y-2">
              <Link 
                to="/products" 
                className="block py-2 hover:text-blue-600"
                onClick={() => setIsMobileMenuOpen(false)}
              >
                DTF Transfers
              </Link>
              <Link 
                to="/products/heat-press" 
                className="block py-2 hover:text-blue-600"
                onClick={() => setIsMobileMenuOpen(false)}
              >
                Heat Press Equipment
              </Link>
              <Link 
                to="/gang-sheet-builder" 
                className="block py-2 hover:text-blue-600"
                onClick={() => setIsMobileMenuOpen(false)}
              >
                Gang Sheet Builder
              </Link>
              <Link 
                to="/education" 
                className="block py-2 hover:text-blue-600"
                onClick={() => setIsMobileMenuOpen(false)}
              >
                Education
              </Link>
              <Link 
                to="/about" 
                className="block py-2 hover:text-blue-600"
                onClick={() => setIsMobileMenuOpen(false)}
              >
                About
              </Link>
            </div>
          </div>
        )}
      </div>
    </nav>
  );
};

export default Navigation;