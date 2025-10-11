import React, { useState } from 'react';
import Navigation from '../components/Navigation';
import Footer from '../components/Footer';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Input } from '../components/ui/input';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { Search, Play, Clock, BookOpen, Star, Download } from 'lucide-react';
import { educationContent } from '../data/mockData';

const EducationPage = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');

  const categories = [
    { id: 'all', name: 'All Topics', count: educationContent.length },
    { id: 'heat-press-guide', name: 'Heat Press Guide', count: 1 },
    { id: 'design-tips', name: 'Design Tips', count: 1 }
  ];

  const filteredContent = educationContent.filter(content => {
    const matchesSearch = content.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         content.excerpt.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCategory = selectedCategory === 'all' || content.category === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  const featuredContent = educationContent[0];

  return (
    <div className="min-h-screen bg-gray-50">
      <Navigation />
      
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            PRESM Education Center
          </h1>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Master the art of DTF transfers with our comprehensive guides, tutorials, 
            and expert tips. From beginner basics to advanced techniques.
          </p>
        </div>

        {/* Featured Content */}
        <Card className="mb-12 overflow-hidden">
          <div className="grid grid-cols-1 lg:grid-cols-2">
            <div className="relative">
              {featuredContent.videoUrl && (
                <div className="aspect-video bg-gray-900 flex items-center justify-center">
                  <Button size="lg" className="bg-blue-600 hover:bg-blue-700 rounded-full p-4">
                    <Play className="h-8 w-8" />
                  </Button>
                </div>
              )}
            </div>
            <CardContent className="p-8 flex flex-col justify-center">
              <Badge className="w-fit mb-4 bg-blue-100 text-blue-800">Featured Guide</Badge>
              <h2 className="text-2xl font-bold mb-4">{featuredContent.title}</h2>
              <p className="text-gray-600 mb-6">{featuredContent.excerpt}</p>
              <div className="flex items-center space-x-4 mb-6">
                <div className="flex items-center text-sm text-gray-500">
                  <Clock className="h-4 w-4 mr-1" />
                  <span>15 min read</span>
                </div>
                <div className="flex items-center text-sm text-gray-500">
                  <Star className="h-4 w-4 mr-1 fill-yellow-400 text-yellow-400" />
                  <span>4.9 rating</span>
                </div>
              </div>
              <Button className="w-fit bg-blue-600 hover:bg-blue-700">
                <BookOpen className="mr-2 h-4 w-4" />
                Read Full Guide
              </Button>
            </CardContent>
          </div>
        </Card>

        {/* Search and Filter */}
        <div className="mb-8">
          <div className="flex flex-col md:flex-row space-y-4 md:space-y-0 md:space-x-4 mb-6">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              <Input
                type="text"
                placeholder="Search guides and tutorials..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>
          </div>

          <Tabs value={selectedCategory} onValueChange={setSelectedCategory}>
            <TabsList className="grid w-full grid-cols-3 max-w-md">
              {categories.map(category => (
                <TabsTrigger key={category.id} value={category.id} className="text-sm">
                  {category.name} ({category.count})
                </TabsTrigger>
              ))}
            </TabsList>
          </Tabs>
        </div>

        {/* Content Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 mb-12">
          {filteredContent.map((content) => (
            <Card key={content.id} className="hover:shadow-lg transition-shadow">
              <CardHeader>
                <div className="flex justify-between items-start mb-2">
                  <Badge variant="outline" className="capitalize">
                    {content.category.replace('-', ' ')}
                  </Badge>
                  <div className="flex items-center text-sm text-gray-500">
                    <Clock className="h-4 w-4 mr-1" />
                    <span>15 min</span>
                  </div>
                </div>
                <CardTitle className="text-lg">{content.title}</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-600 text-sm mb-4">{content.excerpt}</p>
                
                <div className="flex flex-wrap gap-2 mb-4">
                  {content.tags.map((tag, index) => (
                    <Badge key={index} variant="secondary" className="text-xs">
                      #{tag}
                    </Badge>
                  ))}
                </div>
                
                <div className="flex justify-between items-center">
                  <Button variant="outline" size="sm">
                    <BookOpen className="mr-2 h-4 w-4" />
                    Read Guide
                  </Button>
                  {content.videoUrl && (
                    <Button variant="ghost" size="sm">
                      <Play className="mr-2 h-4 w-4" />
                      Watch
                    </Button>
                  )}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Quick Reference Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
          <Card className="text-center p-6 bg-blue-50 border-blue-200">
            <CardContent className="p-0">
              <div className="text-3xl font-bold text-blue-600 mb-2">310°F</div>
              <div className="text-sm font-medium text-blue-800 mb-1">Temperature</div>
              <div className="text-xs text-blue-600">Standard DTF Heat Press</div>
            </CardContent>
          </Card>

          <Card className="text-center p-6 bg-green-50 border-green-200">
            <CardContent className="p-0">
              <div className="text-3xl font-bold text-green-600 mb-2">12-15s</div>
              <div className="text-sm font-medium text-green-800 mb-1">Press Time</div>
              <div className="text-xs text-green-600">Medium-High Pressure</div>
            </CardContent>
          </Card>

          <Card className="text-center p-6 bg-purple-50 border-purple-200">
            <CardContent className="p-0">
              <div className="text-3xl font-bold text-purple-600 mb-2">300 DPI</div>
              <div className="text-sm font-medium text-purple-800 mb-1">Resolution</div>
              <div className="text-xs text-purple-600">Minimum for Print</div>
            </CardContent>
          </Card>

          <Card className="text-center p-6 bg-orange-50 border-orange-200">
            <CardContent className="p-0">
              <div className="text-3xl font-bold text-orange-600 mb-2">Cold</div>
              <div className="text-sm font-medium text-orange-800 mb-1">Peel Type</div>
              <div className="text-xs text-orange-600">Wait 10-15 seconds</div>
            </CardContent>
          </Card>
        </div>

        {/* Download Resources */}
        <Card className="bg-gradient-to-r from-blue-50 to-indigo-100 border-blue-200">
          <CardContent className="p-8 text-center">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">
              Download Free Resources
            </h2>
            <p className="text-gray-600 mb-6 max-w-2xl mx-auto">
              Get our comprehensive DTF transfer guide, heat press settings chart, 
              and design templates - all in one convenient download.
            </p>
            <Button size="lg" className="bg-blue-600 hover:bg-blue-700">
              <Download className="mr-2 h-5 w-5" />
              Download Resource Pack
            </Button>
          </CardContent>
        </Card>
      </div>

      <Footer />
    </div>
  );
};

export default EducationPage;