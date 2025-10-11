import React, { useState, useMemo, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import Navigation from '../components/Navigation';
import Footer from '../components/Footer';
import { Button } from '../components/ui/button';
import { Card, CardContent } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Input } from '../components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { Checkbox } from '../components/ui/checkbox';
import { Star, Filter, Grid, List, ShoppingCart, Loader2 } from 'lucide-react';
import { useCart } from '../context/CartContext';
import { useToast } from '../hooks/use-toast';
import { productsAPI, handleAPIError } from '../services/api';

const ProductsPage = () => {
  const { category } = useParams();
  const [searchTerm, setSearchTerm] = useState('');
  const [sortBy, setSortBy] = useState('name');
  const [priceRange, setPriceRange] = useState({ min: '', max: '' });
  const [selectedCategories, setSelectedCategories] = useState([]);
  const [viewMode, setViewMode] = useState('grid');
  const [products, setProducts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const { addItem } = useCart();
  const { toast } = useToast();

  // Fetch products and categories on component mount
  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const [productsResponse, categoriesResponse] = await Promise.all([
          category ? productsAPI.getByCategory(category) : productsAPI.getAll(),
          productsAPI.getCategories()
        ]);
        
        setProducts(productsResponse.data);
        setCategories(categoriesResponse.data);
        setError(null);
      } catch (err) {
        setError(handleAPIError(err));
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [category]);

  // Refetch products when search term changes
  useEffect(() => {
    const fetchSearchResults = async () => {
      if (searchTerm.trim()) {
        try {
          setLoading(true);
          const response = await productsAPI.search(searchTerm, category);
          setProducts(response.data);
        } catch (err) {
          setError(handleAPIError(err));
        } finally {
          setLoading(false);
        }
      } else {
        // Reset to all products if search is cleared
        try {
          setLoading(true);
          const response = category ? await productsAPI.getByCategory(category) : await productsAPI.getAll();
          setProducts(response.data);
        } catch (err) {
          setError(handleAPIError(err));
        } finally {
          setLoading(false);
        }
      }
    };

    const timeoutId = setTimeout(fetchSearchResults, 500); // Debounce search
    return () => clearTimeout(timeoutId);
  }, [searchTerm, category]);

  // Filter and sort products
  const filteredProducts = useMemo(() => {
    let filtered = products;

    // Filter by URL category
    if (category) {
      filtered = filtered.filter(product => product.category === category);
    }

    // Filter by search term
    if (searchTerm) {
      filtered = filtered.filter(product =>
        product.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        product.description.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    // Filter by selected categories
    if (selectedCategories.length > 0) {
      filtered = filtered.filter(product =>
        selectedCategories.includes(product.category)
      );
    }

    // Filter by price range
    if (priceRange.min) {
      filtered = filtered.filter(product => product.price >= parseFloat(priceRange.min));
    }
    if (priceRange.max) {
      filtered = filtered.filter(product => product.price <= parseFloat(priceRange.max));
    }

    // Sort products
    filtered.sort((a, b) => {
      switch (sortBy) {
        case 'price-low':
          return a.price - b.price;
        case 'price-high':
          return b.price - a.price;
        case 'name':
        default:
          return a.name.localeCompare(b.name);
      }
    });

    return filtered;
  }, [products, category, searchTerm, selectedCategories, priceRange, sortBy]);

  // Transform categories data for display
  const categoryOptions = [
    { id: 'dtf-transfers', name: 'DTF Transfers' },
    { id: 'gang-sheets', name: 'Gang Sheets' },
    { id: 'heat-presses', name: 'Heat Presses' },
    { id: 'accessories', name: 'Accessories' },
    { id: 'supplies', name: 'Supplies' },
    { id: 'custom-designs', name: 'Custom Designs' }
  ].map(cat => {
    const categoryData = categories.find(c => c.category === cat.id);
    return {
      ...cat,
      count: categoryData ? categoryData.count : 0
    };
  });

  const handleCategoryChange = async (categoryId, checked) => {
    const newCategories = checked
      ? [...selectedCategories, categoryId]
      : selectedCategories.filter(id => id !== categoryId);
    
    setSelectedCategories(newCategories);
    
    // Refetch products with selected categories
    try {
      setLoading(true);
      let response;
      if (newCategories.length === 1) {
        response = await productsAPI.getByCategory(newCategories[0]);
      } else if (newCategories.length === 0) {
        response = await productsAPI.getAll();
      } else {
        // For multiple categories, we'll filter on frontend for now
        response = await productsAPI.getAll();
      }
      setProducts(response.data);
    } catch (err) {
      setError(handleAPIError(err));
    } finally {
      setLoading(false);
    }
  };

  const handleAddToCart = (product) => {
    addItem({
      ...product,
      id: product._id, // Use MongoDB _id
      quantity: 1,
      options: { size: product.sizes[0] }
    });
    toast({
      title: "Added to Cart",
      description: `${product.name} added successfully.`,
    });
  };

  const getCategoryTitle = () => {
    const categoryMap = {
      'dtf-transfers': 'DTF Transfers',
      'gang-sheets': 'Gang Sheets',
      'heat-presses': 'Heat Press Equipment',
      'accessories': 'Accessories',
      'supplies': 'Supplies',
      'custom-designs': 'Custom Design Services'
    };
    return category ? categoryMap[category] || 'Products' : 'All Products';
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Navigation />
      
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            {getCategoryTitle()}
          </h1>
          <p className="text-gray-600">
            {loading ? 'Loading...' : `${filteredProducts.length} products found`}
          </p>
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4 mt-4">
              <p className="text-red-600">{error}</p>
            </div>
          )}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          {/* Filters Sidebar */}
          <div className="lg:col-span-1">
            <Card className="sticky top-24">
              <CardContent className="p-6">
                <h3 className="font-semibold text-lg mb-4 flex items-center">
                  <Filter className="mr-2 h-5 w-5" />
                  Filters
                </h3>

                {/* Search */}
                <div className="mb-6">
                  <label className="text-sm font-medium mb-2 block">Search</label>
                  <Input
                    placeholder="Search products..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                  />
                </div>

                {/* Categories */}
                {!category && (
                  <div className="mb-6">
                    <label className="text-sm font-medium mb-2 block">Categories</label>
                    <div className="space-y-2">
                      {categoryOptions.map(cat => (
                        <div key={cat.id} className="flex items-center space-x-2">
                          <Checkbox
                            id={cat.id}
                            checked={selectedCategories.includes(cat.id)}
                            onCheckedChange={(checked) => handleCategoryChange(cat.id, checked)}
                          />
                          <label htmlFor={cat.id} className="text-sm flex-1 cursor-pointer">
                            {cat.name} ({cat.count})
                          </label>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Price Range */}
                <div className="mb-6">
                  <label className="text-sm font-medium mb-2 block">Price Range</label>
                  <div className="grid grid-cols-2 gap-2">
                    <Input
                      type="number"
                      placeholder="Min"
                      value={priceRange.min}
                      onChange={(e) => setPriceRange(prev => ({ ...prev, min: e.target.value }))}
                    />
                    <Input
                      type="number"
                      placeholder="Max"
                      value={priceRange.max}
                      onChange={(e) => setPriceRange(prev => ({ ...prev, max: e.target.value }))}
                    />
                  </div>
                </div>

                {/* Clear Filters */}
                <Button 
                  variant="outline" 
                  className="w-full"
                  onClick={() => {
                    setSearchTerm('');
                    setSelectedCategories([]);
                    setPriceRange({ min: '', max: '' });
                  }}
                >
                  Clear Filters
                </Button>
              </CardContent>
            </Card>
          </div>

          {/* Products Grid */}
          <div className="lg:col-span-3">
            {/* Toolbar */}
            <div className="flex justify-between items-center mb-6 p-4 bg-white rounded-lg border">
              <div className="flex items-center space-x-4">
                <Select value={sortBy} onValueChange={setSortBy}>
                  <SelectTrigger className="w-48">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="name">Sort by Name</SelectItem>
                    <SelectItem value="price-low">Price: Low to High</SelectItem>
                    <SelectItem value="price-high">Price: High to Low</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              
              <div className="flex items-center space-x-2">
                <Button
                  variant={viewMode === 'grid' ? 'default' : 'ghost'}
                  size="sm"
                  onClick={() => setViewMode('grid')}
                >
                  <Grid className="h-4 w-4" />
                </Button>
                <Button
                  variant={viewMode === 'list' ? 'default' : 'ghost'}
                  size="sm"
                  onClick={() => setViewMode('list')}
                >
                  <List className="h-4 w-4" />
                </Button>
              </div>
            </div>

            {/* Products */}
            {loading ? (
              <div className="flex justify-center items-center py-12">
                <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
                <span className="ml-2 text-gray-600">Loading products...</span>
              </div>
            ) : filteredProducts.length === 0 ? (
              <div className="text-center py-12">
                <p className="text-gray-500 text-lg">No products found matching your criteria.</p>
                <Button 
                  variant="outline" 
                  className="mt-4"
                  onClick={() => {
                    setSearchTerm('');
                    setSelectedCategories([]);
                    setPriceRange({ min: '', max: '' });
                  }}
                >
                  Clear Filters
                </Button>
              </div>
            ) : (
              <div className={
                viewMode === 'grid' 
                  ? 'grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6'
                  : 'space-y-4'
              }>
                {filteredProducts.map((product) => (
                  <Card key={product._id} className={`hover:shadow-lg transition-shadow ${
                    viewMode === 'list' ? 'flex flex-row overflow-hidden' : 'overflow-hidden'
                  }`}>
                    <div className={viewMode === 'list' ? 'w-48 flex-shrink-0' : ''}>
                      <img 
                        src={product.image} 
                        alt={product.name}
                        className={`object-cover ${
                          viewMode === 'list' ? 'w-full h-full' : 'w-full h-48'
                        }`}
                      />
                    </div>
                    
                    <CardContent className={`p-6 ${viewMode === 'list' ? 'flex-1 flex flex-col justify-between' : ''}`}>
                      <div className="mb-4">
                        <div className="flex justify-between items-start mb-2">
                          <h3 className="font-semibold text-lg">{product.name}</h3>
                          <Badge variant="secondary" className="ml-2 capitalize">
                            {product.category.replace('-', ' ')}
                          </Badge>
                        </div>
                        <p className="text-gray-600 text-sm mb-3">{product.description}</p>
                        
                        {/* Features */}
                        <div className="flex flex-wrap gap-1 mb-3">
                          {product.features.slice(0, 3).map((feature, index) => (
                            <Badge key={index} variant="outline" className="text-xs">
                              {feature}
                            </Badge>
                          ))}
                        </div>
                        
                        {/* Sizes */}
                        <div className="mb-3">
                          <span className="text-sm font-medium">Available sizes: </span>
                          <span className="text-sm text-gray-600">
                            {product.sizes.slice(0, 3).join(', ')}
                            {product.sizes.length > 3 && ` +${product.sizes.length - 3} more`}
                          </span>
                        </div>
                      </div>
                      
                      <div className="flex justify-between items-center">
                        <div>
                          <span className="text-2xl font-bold text-blue-600">
                            ${product.price}
                          </span>
                          {product.minQuantity > 1 && (
                            <span className="text-sm text-gray-500 block">
                              Min qty: {product.minQuantity}
                            </span>
                          )}
                        </div>
                        <Button 
                          onClick={() => handleAddToCart(product)}
                          className="bg-blue-600 hover:bg-blue-700"
                        >
                          <ShoppingCart className="mr-2 h-4 w-4" />
                          Add to Cart
                        </Button>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>

      <Footer />
    </div>
  );
};

export default ProductsPage;