import React, { useState, useRef, useCallback } from 'react';
import Navigation from '../components/Navigation';
import Footer from '../components/Footer';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Input } from '../components/ui/input';
import { Badge } from '../components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { 
  Upload, 
  Trash2, 
  RotateCw, 
  Move, 
  ZoomIn, 
  ZoomOut,
  Download,
  ShoppingCart,
  Sparkles,
  Grid,
  Calculator,
  AlertCircle,
  Plus,
  Minus
} from 'lucide-react';
import { useCart } from '../context/CartContext';
import { useToast } from '../hooks/use-toast';
import { gangSheetTemplates } from '../data/mockData';

const GangSheetBuilder = () => {
  const BACKEND_URL = "https://silver-dollop-pjrvgv9wqjg5c7wpx-8000.app.github.dev";
  const [selectedTemplate, setSelectedTemplate] = useState(gangSheetTemplates[0]);
  const [designs, setDesigns] = useState([]);
  const [selectedDesign, setSelectedDesign] = useState(null);
  const [zoom, setZoom] = useState(100);
  const [isDragging, setIsDragging] = useState(false);
  const [dragOffset, setDragOffset] = useState({ x: 0, y: 0 });
  const [showGrid, setShowGrid] = useState(true);
  const [autoNest, setAutoNest] = useState(false);
  const fileInputRef = useRef(null);
  const canvasRef = useRef(null);
  const { addItem } = useCart();
  const { toast } = useToast();

  // Design management functions
  const handleFileUpload = (event) => {
    const files = Array.from(event.target.files);
    
    files.forEach((file, index) => {
      if (file.type.startsWith('image/')) {
        const reader = new FileReader();
        reader.onload = (e) => {
          const img = new Image();
          img.onload = () => {
            const newDesign = {
              id: Date.now() + index,
              name: file.name,
              src: e.target.result,
              width: Math.min(img.width / 10, 100), // Scale down for initial placement
              height: Math.min(img.height / 10, 100),
              originalWidth: img.width,
              originalHeight: img.height,
              x: 50 + (index * 20), // Offset multiple uploads
              y: 50 + (index * 20),
              rotation: 0
            };
            setDesigns(prev => [...prev, newDesign]);
          };
          img.src = e.target.result;
        };
        reader.readAsDataURL(file);
      }
    });
    
    // Reset file input
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const deleteDesign = (designId) => {
    setDesigns(prev => prev.filter(d => d.id !== designId));
    if (selectedDesign?.id === designId) {
      setSelectedDesign(null);
    }
  };

  const duplicateDesign = (design) => {
    const newDesign = {
      ...design,
      id: Date.now(),
      x: design.x + 20,
      y: design.y + 20
    };
    setDesigns(prev => [...prev, newDesign]);
  };

  const rotateDesign = (designId, rotation) => {
    setDesigns(prev => prev.map(d => 
      d.id === designId ? { ...d, rotation: (d.rotation + rotation) % 360 } : d
    ));
  };

  const updateDesignSize = (designId, width, height) => {
    setDesigns(prev => prev.map(d => 
      d.id === designId ? { ...d, width: Math.max(10, width), height: Math.max(10, height) } : d
    ));
  };

  // Canvas interaction functions
  const handleCanvasClick = (event) => {
    const rect = canvasRef.current.getBoundingClientRect();
    const x = (event.clientX - rect.left) / (rect.width / 100);
    const y = (event.clientY - rect.top) / (rect.height / 100);
    
    // Find clicked design (reverse order to prioritize top designs)
    const clickedDesign = [...designs].reverse().find(design => 
      x >= design.x && x <= design.x + design.width &&
      y >= design.y && y <= design.y + design.height
    );
    
    setSelectedDesign(clickedDesign || null);
  };

  const handleMouseDown = (event, design) => {
    if (selectedDesign?.id === design.id) {
      setIsDragging(true);
      const rect = canvasRef.current.getBoundingClientRect();
      setDragOffset({
        x: (event.clientX - rect.left) / (rect.width / 100) - design.x,
        y: (event.clientY - rect.top) / (rect.height / 100) - design.y
      });
    }
  };

  const handleMouseMove = useCallback((event) => {
    if (isDragging && selectedDesign) {
      const rect = canvasRef.current.getBoundingClientRect();
      const x = (event.clientX - rect.left) / (rect.width / 100) - dragOffset.x;
      const y = (event.clientY - rect.top) / (rect.height / 100) - dragOffset.y;
      
      setDesigns(prev => prev.map(d => 
        d.id === selectedDesign.id 
          ? { 
              ...d, 
              x: Math.max(0, Math.min(100 - d.width, x)),
              y: Math.max(0, Math.min(100 - d.height, y))
            } 
          : d
      ));
    }
  }, [isDragging, selectedDesign, dragOffset]);

  const handleMouseUp = useCallback(() => {
    setIsDragging(false);
  }, []);

  // Auto-nest function (simplified AI simulation)
  const handleAutoNest = () => {
    if (designs.length === 0) return;
    
    // Simple bin packing algorithm simulation
    let currentX = 0;
    let currentY = 0;
    let rowHeight = 0;
    const padding = 5 / 72; // in inches, but since units are normalized to 100, adjust
    const maxWidth = 100;
    
    const optimizedDesigns = [...designs].sort((a,b) => b.height - a.height).map(design => {
      if (currentX + design.width > maxWidth) {
        currentX = 0;
        currentY += rowHeight + padding;
        rowHeight = 0;
      }
      
      const optimizedDesign = {
        ...design,
        x: currentX,
        y: currentY
      };
      
      currentX += design.width + padding;
      rowHeight = Math.max(rowHeight, design.height);
      
      return optimizedDesign;
    });
    
    setDesigns(optimizedDesigns);
    toast({
      title: "Auto-Nest Complete",
      description: "Designs have been optimally arranged on the sheet.",
    });
  };

  // Price calculation
  const calculatePrice = () => {
    const totalDesigns = designs.length;
    const basePrice = selectedTemplate.price;
    const designCost = totalDesigns * 0.50; // $0.50 per unique design
    return basePrice + designCost;
  };

  const addToCart = async () => {
    if (designs.length === 0) {
      toast({
        title: "No Designs",
        description: "Please add at least one design to your gang sheet.",
        variant: "destructive"
      });
      return;
    }

    try {
      // Create high-res canvas for print-ready image
      const dpi = 300;
      const scale = dpi / 72;
      const canvasWidth = selectedTemplate.width * dpi;
      const canvasHeight = selectedTemplate.height * dpi;

      const canvas = document.createElement('canvas');
      canvas.width = canvasWidth;
      canvas.height = canvasHeight;
      const ctx = canvas.getContext('2d');

      // White background
      ctx.fillStyle = 'white';
      ctx.fillRect(0, 0, canvasWidth, canvasHeight);

      // Draw each design at high resolution
      for (const design of designs) {
        const img = await new Promise((resolve, reject) => {
          const i = new Image();
          i.onload = () => resolve(i);
          i.onerror = reject;
          i.src = design.src;
        });

        const scaledX = design.x * scale;
        const scaledY = design.y * scale;
        const scaledWidth = design.width * scale;
        const scaledHeight = design.height * scale;
        const centerX = scaledX + (scaledWidth / 2);
        const centerY = scaledY + (scaledHeight / 2);

        ctx.save();
        ctx.translate(centerX, centerY);
        ctx.rotate(design.rotation * Math.PI / 180);
        ctx.drawImage(img, -scaledWidth / 2, -scaledHeight / 2, scaledWidth, scaledHeight);
        ctx.restore();
      }

      const dataURL = canvas.toDataURL('image/png');
      const base64 = dataURL.split(',')[1];

      // Send to backend to create custom product in Shopify
      const response = await fetch(`${BACKEND_URL}/api/shopify/create_custom_gang_sheet`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          base64_image: base64,
          filename: `gang_sheet_${Date.now()}.png`,
          name: `Custom Gang Sheet (${selectedTemplate.name})`,
          price: calculatePrice(),
          description: `Custom gang sheet with ${designs.length} unique designs. Sheet size: ${selectedTemplate.width}" x ${selectedTemplate.height}".`
        })
      });

      if (!response.ok) {
        throw new Error(`Failed to create custom product: ${response.status}`);
      }

      const data = await response.json();
      const variant_id = data.variant_id;
      const image_url = data.image_url || selectedTemplate.image;

      // Add to local cart with the new variant_id
      const gangSheetItem = {
        variant_id,
        name: `Custom Gang Sheet (${selectedTemplate.name})`,
        price: calculatePrice(),
        image: image_url,
        description: `Custom gang sheet with ${designs.length} unique designs`,
        quantity: 1,
        options: {
          template: selectedTemplate.name,
          designs: designs.length
        }
      };

      addItem(gangSheetItem);
      toast({
        title: "Added to Cart",
        description: "Your custom gang sheet has been added to cart.",
      });
    } catch (err) {
      console.error("Error creating custom gang sheet:", err);
      toast({
        title: "Error",
        description: "Failed to create custom gang sheet. Please try again.",
        variant: "destructive"
      });
    }
  };

  // Event listeners
  React.useEffect(() => {
    document.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('mouseup', handleMouseUp);
    
    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };
  }, [handleMouseMove, handleMouseUp]);

  return (
    <div className="min-h-screen bg-gray-50">
      <Navigation />
      
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            <Sparkles className="inline-block mr-2 h-8 w-8 text-blue-600" />
            AI-Powered Gang Sheet Builder
          </h1>
          <p className="text-xl text-gray-600">
            Create optimized gang sheets with drag-and-drop simplicity and AI auto-nesting
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Left Sidebar - Tools & Templates */}
          <div className="lg:col-span-1 space-y-6">
            {/* Template Selection */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Sheet Templates</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {gangSheetTemplates.map(template => (
                  <div 
                    key={template.id}
                    className={`p-3 border rounded-lg cursor-pointer transition-all ${
                      selectedTemplate.id === template.id 
                        ? 'border-blue-500 bg-blue-50' 
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                    onClick={() => setSelectedTemplate(template)}
                  >
                    <div className="flex justify-between items-start mb-2">
                      <h4 className="font-semibold text-sm">{template.name}</h4>
                      <Badge variant="outline">${template.price}</Badge>
                    </div>
                    <p className="text-xs text-gray-600">
                      {template.width}" × {template.height}" • Max {template.maxDesigns} designs
                    </p>
                  </div>
                ))}
              </CardContent>
            </Card>

            {/* Upload Designs */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Upload Designs</CardTitle>
              </CardHeader>
              <CardContent>
                <Button 
                  onClick={() => fileInputRef.current?.click()}
                  className="w-full mb-4"
                  variant="outline"
                >
                  <Upload className="mr-2 h-4 w-4" />
                  Upload Images
                </Button>
                <input
                  ref={fileInputRef}
                  type="file"
                  multiple
                  accept="image/*"
                  onChange={handleFileUpload}
                  className="hidden"
                />
                
                <div className="space-y-2 text-xs text-gray-600">
                  <p>• Supported: JPG, PNG, SVG</p>
                  <p>• Minimum: 300 DPI</p>
                  <p>• Transparent backgrounds recommended</p>
                </div>
              </CardContent>
            </Card>

            {/* Tools */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Tools</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <Button 
                  onClick={handleAutoNest}
                  className="w-full bg-blue-600 hover:bg-blue-700"
                  disabled={designs.length === 0}
                >
                  <Sparkles className="mr-2 h-4 w-4" />
                  AI Auto-Nest
                </Button>
                
                <div className="flex space-x-2">
                  <Button 
                    variant="outline" 
                    size="sm"
                    onClick={() => setShowGrid(!showGrid)}
                    className={showGrid ? 'bg-blue-50 border-blue-300' : ''}
                  >
                    <Grid className="h-4 w-4" />
                  </Button>
                  <Button 
                    variant="outline" 
                    size="sm"
                    onClick={() => setZoom(Math.max(25, zoom - 25))}
                  >
                    <ZoomOut className="h-4 w-4" />
                  </Button>
                  <Button 
                    variant="outline" 
                    size="sm"
                    onClick={() => setZoom(Math.min(200, zoom + 25))}
                  >
                    <ZoomIn className="h-4 w-4" />
                  </Button>
                </div>
                
                <div className="text-center text-sm text-gray-600">
                  Zoom: {zoom}%
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Main Canvas Area */}
          <div className="lg:col-span-2">
            <Card className="mb-4">
              <CardContent className="p-0">
                <div 
                  ref={canvasRef}
                  className="relative bg-white border-2 border-dashed border-gray-300 overflow-hidden cursor-crosshair"
                  style={{
                    width: `${selectedTemplate.width * 72 * (zoom / 100)}px`,
                    height: `${selectedTemplate.height * 72 * (zoom / 100)}px`,
                    maxWidth: '100%',
                    maxHeight: '600px',
                    margin: '0 auto'
                  }}
                  onClick={handleCanvasClick}
                >
                  {/* Grid */}
                  {showGrid && (
                    <div 
                      className="absolute inset-0 opacity-20"
                      style={{
                        backgroundImage: `
                          linear-gradient(to right, #000 1px, transparent 1px),
                          linear-gradient(to bottom, #000 1px, transparent 1px)
                        `,
                        backgroundSize: `${(selectedTemplate.width * 72 * (zoom / 100)) / 12}px ${(selectedTemplate.height * 72 * (zoom / 100)) / 12}px`
                      }}
                    />
                  )}
                  
                  {/* Designs */}
                  {designs.map(design => (
                    <div
                      key={design.id}
                      className={`absolute cursor-move ${
                        selectedDesign?.id === design.id 
                          ? 'ring-2 ring-blue-500 ring-offset-2' 
                          : 'hover:ring-1 hover:ring-gray-400'
                      }`}
                      style={{
                        left: `${design.x * (selectedTemplate.width * 72 / 100) * (zoom / 100)}px`,
                        top: `${design.y * (selectedTemplate.height * 72 / 100) * (zoom / 100)}px`,
                        width: `${design.width * (zoom / 100)}px`,
                        height: `${design.height * (zoom / 100)}px`,
                        transform: `rotate(${design.rotation}deg)`,
                        transformOrigin: 'center'
                      }}
                      onMouseDown={(e) => handleMouseDown(e, design)}
                    >
                      <img 
                        src={design.src} 
                        alt={design.name}
                        className="w-full h-full object-contain"
                        draggable={false}
                      />
                    </div>
                  ))}
                  
                  {/* Empty state */}
                  {designs.length === 0 && (
                    <div className="absolute inset-0 flex items-center justify-center">
                      <div className="text-center text-gray-400">
                        <Upload className="h-12 w-12 mx-auto mb-4" />
                        <p>Upload designs to get started</p>
                      </div>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>

            <div className="text-center text-sm text-gray-600">
              Sheet Size: {selectedTemplate.width}" × {selectedTemplate.height}" • 
              Total Designs: {designs.length} • 
              Estimated Price: <span className="font-semibold text-green-600">${calculatePrice().toFixed(2)}</span>
            </div>
          </div>

          {/* Right Sidebar - Design Properties & Summary */}
          <div className="lg:col-span-1 space-y-6">
            {/* Selected Design Properties */}
            {selectedDesign && (
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg flex justify-between items-center">
                    Design Properties
                    <Button 
                      variant="ghost" 
                      size="sm"
                      onClick={() => deleteDesign(selectedDesign.id)}
                      className="text-red-500 hover:text-red-700"
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <label className="text-sm font-medium">Name</label>
                    <p className="text-sm text-gray-600 truncate">{selectedDesign.name}</p>
                  </div>
                  
                  <div className="grid grid-cols-2 gap-2">
                    <div>
                      <label className="text-sm font-medium">Width</label>
                      <Input 
                        type="number" 
                        value={Math.round(selectedDesign.width)}
                        onChange={(e) => updateDesignSize(
                          selectedDesign.id, 
                          parseInt(e.target.value) || selectedDesign.width,
                          selectedDesign.height
                        )}
                        className="text-xs"
                      />
                    </div>
                    <div>
                      <label className="text-sm font-medium">Height</label>
                      <Input 
                        type="number" 
                        value={Math.round(selectedDesign.height)}
                        onChange={(e) => updateDesignSize(
                          selectedDesign.id, 
                          selectedDesign.width,
                          parseInt(e.target.value) || selectedDesign.height
                        )}
                        className="text-xs"
                      />
                    </div>
                  </div>

                  <div className="flex space-x-2">
                    <Button 
                      variant="outline" 
                      size="sm"
                      onClick={() => rotateDesign(selectedDesign.id, -90)}
                      className="flex-1"
                    >
                      <RotateCw className="h-3 w-3 transform -scale-x-100" />
                    </Button>
                    <Button 
                      variant="outline" 
                      size="sm"
                      onClick={() => rotateDesign(selectedDesign.id, 90)}
                      className="flex-1"
                    >
                      <RotateCw className="h-3 w-3" />
                    </Button>
                  </div>

                  <Button 
                    variant="outline" 
                    size="sm" 
                    onClick={() => duplicateDesign(selectedDesign)}
                    className="w-full"
                  >
                    Duplicate Design
                  </Button>
                </CardContent>
              </Card>
            )}

            {/* Design List */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">
                  Designs ({designs.length})
                </CardTitle>
              </CardHeader>
              <CardContent className="max-h-60 overflow-y-auto">
                {designs.length === 0 ? (
                  <p className="text-sm text-gray-500">No designs added yet</p>
                ) : (
                  <div className="space-y-2">
                    {designs.map(design => (
                      <div 
                        key={design.id}
                        className={`flex items-center p-2 rounded border cursor-pointer ${
                          selectedDesign?.id === design.id 
                            ? 'border-blue-500 bg-blue-50' 
                            : 'border-gray-200 hover:border-gray-300'
                        }`}
                        onClick={() => setSelectedDesign(design)}
                      >
                        <img 
                          src={design.src} 
                          alt={design.name}
                          className="w-8 h-8 object-cover rounded mr-2"
                        />
                        <div className="flex-1 min-w-0">
                          <p className="text-xs font-medium truncate">{design.name}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Order Summary */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg flex items-center">
                  <Calculator className="mr-2 h-5 w-5" />
                  Order Summary
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex justify-between text-sm">
                  <span>Base Sheet ({selectedTemplate.name})</span>
                  <span>${selectedTemplate.price}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span>Designs ({designs.length} × $0.50)</span>
                  <span>${(designs.length * 0.50).toFixed(2)}</span>
                </div>
                <div className="border-t pt-2">
                  <div className="flex justify-between font-semibold">
                    <span>Total</span>
                    <span className="text-green-600">${calculatePrice().toFixed(2)}</span>
                  </div>
                </div>
                
                <Button 
                  onClick={addToCart}
                  className="w-full bg-blue-600 hover:bg-blue-700"
                  disabled={designs.length === 0}
                >
                  <ShoppingCart className="mr-2 h-4 w-4" />
                  Add to Cart
                </Button>
                
                <Button variant="outline" className="w-full" disabled={designs.length === 0}>
                  <Download className="mr-2 h-4 w-4" />
                  Export Preview
                </Button>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>

      <Footer />
    </div>
  );
};

export default GangSheetBuilder;