// GangSheetBuilder.jsx
import React, { useState, useRef, useCallback, useEffect } from "react";
import Navigation from "../components/Navigation";
import Footer from "../components/Footer";
import { Button } from "../components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Input } from "../components/ui/input";
import { Badge } from "../components/ui/badge";
import { useCart } from "../context/CartContext";
import { useToast } from "../hooks/use-toast";
import { gangSheetTemplates } from "../data/mockData";
import {
  Upload,
  Trash2,
  RotateCw,
  ZoomIn,
  ZoomOut,
  Sparkles,
  Grid,
  ShoppingCart,
  Calculator,
  Download,
  Copy,
  Lock,
  Unlock,
  ArrowUpCircle,
  ArrowDownCircle,
  CornerUpLeft,
  CornerUpRight,
  Eye,
  EyeOff
} from "lucide-react";

/**
 * Full-featured Gang Sheet Builder
 * - Keeps UI similar to original
 * - All editing features requested
 * - Uses backend: POST /api/shopify/create-gang-sheet (form-data: name, description, price, image)
 */

const GangSheetBuilder = () => {
  // Change this to your backend base URL
  const BACKEND_URL = "https://unimaginepresmbackned.onrender.com";

  const [selectedTemplate, setSelectedTemplate] = useState(gangSheetTemplates[0]);
  const [designs, setDesigns] = useState([]); // each design: {id,name,src,x,y,width,height,rotation,opacity,flipH,flipV,locked,visible}
  const [selectedDesign, setSelectedDesign] = useState(null);
  const [zoom, setZoom] = useState(100);
  const [showGrid, setShowGrid] = useState(true);
  const fileInputRef = useRef(null);
  const canvasRef = useRef(null);
  const { addItem } = useCart();
  const { toast } = useToast();
  const [loading, setLoading] = useState(false);

  // displayed canvas dimensions (pixels)
  const displayCanvasDims = () => {
    const width = selectedTemplate.width * 72 * (zoom / 100);
    const height = selectedTemplate.height * 72 * (zoom / 100);
    return { width, height };
  };

  // ---------------- File upload (local dataURL for immediate placement) ----------------
  const handleFileUpload = (e) => {
    const files = Array.from(e.target.files || []);
    if (!files.length) return;
    const { width: displayW } = displayCanvasDims();

    files.forEach((file, idx) => {
      if (!file.type.startsWith("image/")) return;
      const reader = new FileReader();
      reader.onload = (ev) => {
        const dataUrl = ev.target.result;
        const img = new Image();
        img.onload = () => {
          const defaultWidthPx = Math.min(displayW * 0.25, img.width);
          const scale = defaultWidthPx / img.width;
          const defaultHeightPx = img.height * scale;

          const newDesign = {
            id: Date.now() + idx,
            name: file.name,
            src: dataUrl,
            x: 10 + idx * 10,
            y: 10 + idx * 10,
            width: defaultWidthPx,
            height: defaultHeightPx,
            rotation: 0,
            opacity: 1,
            flipH: false,
            flipV: false,
            locked: false,
            visible: true
          };

          setDesigns((p) => [...p, newDesign]);
        };
        img.onerror = () => toast({ title: "Invalid image", description: file.name, variant: "destructive" });
        img.src = dataUrl;
      };
      reader.readAsDataURL(file);
    });

    // reset input
    if (fileInputRef.current) fileInputRef.current.value = "";
  };

  // ---------------- Selection + dragging ----------------
  const [isDragging, setIsDragging] = useState(false);
  const [dragOffset, setDragOffset] = useState({ x: 0, y: 0 });

  const handleCanvasClick = (ev) => {
    if (!canvasRef.current) return;
    const rect = canvasRef.current.getBoundingClientRect();
    const clickX = ev.clientX - rect.left;
    const clickY = ev.clientY - rect.top;

    const clicked = [...designs].reverse().find((d) =>
      d.visible &&
      clickX >= d.x && clickX <= d.x + d.width &&
      clickY >= d.y && clickY <= d.y + d.height
    );

    setSelectedDesign(clicked || null);
  };

  const handleMouseDown = (ev, design) => {
    if (design.locked) return;
    if (!canvasRef.current) return;

    // select if not selected
    if (!selectedDesign || selectedDesign.id !== design.id) setSelectedDesign(design);

    const rect = canvasRef.current.getBoundingClientRect();
    const mx = ev.clientX - rect.left;
    const my = ev.clientY - rect.top;

    setDragOffset({ x: mx - design.x, y: my - design.y });
    setIsDragging(true);
  };

  const handleMouseMove = useCallback((ev) => {
    if (!isDragging || !selectedDesign || selectedDesign.locked) return;
    const rect = canvasRef.current.getBoundingClientRect();
    const mx = ev.clientX - rect.left;
    const my = ev.clientY - rect.top;
    const newX = Math.max(0, Math.min(rect.width - selectedDesign.width, mx - dragOffset.x));
    const newY = Math.max(0, Math.min(rect.height - selectedDesign.height, my - dragOffset.y));

    setDesigns((prev) => prev.map((d) => (d.id === selectedDesign.id ? { ...d, x: newX, y: newY } : d)));
  }, [isDragging, selectedDesign, dragOffset]);

  const handleMouseUp = useCallback(() => setIsDragging(false), []);

  useEffect(() => {
    document.addEventListener("mousemove", handleMouseMove);
    document.addEventListener("mouseup", handleMouseUp);
    return () => {
      document.removeEventListener("mousemove", handleMouseMove);
      document.removeEventListener("mouseup", handleMouseUp);
    };
  }, [handleMouseMove, handleMouseUp]);

  // ---------------- Editing helpers ----------------
  const updateDesign = (id, updates) => {
    setDesigns((prev) => prev.map((d) => (d.id === id ? { ...d, ...updates } : d)));
    if (selectedDesign?.id === id) setSelectedDesign((s) => ({ ...s, ...updates }));
  };

  const rotateDesign = (id, deg) => {
    updateDesign(id, { rotation: ((designs.find(d => d.id === id)?.rotation || 0) + deg) % 360 });
  };

  const updateDesignSize = (id, width, height) => updateDesign(id, { width: Math.max(5, width), height: Math.max(5, height) });

  const toggleFlip = (id, axis) => {
    const d = designs.find(x => x.id === id);
    if (!d) return;
    if (axis === "h") updateDesign(id, { flipH: !d.flipH });
    else updateDesign(id, { flipV: !d.flipV });
  };

  const toggleVisibility = (id) => {
    const d = designs.find(x => x.id === id);
    if (!d) return;
    updateDesign(id, { visible: !d.visible });
  };

  const duplicateDesign = (id) => {
    const d = designs.find(x => x.id === id);
    if (!d) return;
    const copy = { ...d, id: Date.now(), x: d.x + 10, y: d.y + 10, locked: false };
    setDesigns((prev) => [...prev, copy]);
  };

  const bringToFront = (id) => {
    const item = designs.find((d) => d.id === id);
    if (!item) return;
    setDesigns((prev) => [...prev.filter((d) => d.id !== id), item]);
  };

  const sendToBack = (id) => {
    const item = designs.find((d) => d.id === id);
    if (!item) return;
    setDesigns((prev) => [item, ...prev.filter((d) => d.id !== id)]);
  };

  const toggleLock = (id) => {
    const d = designs.find(x => x.id === id);
    if (!d) return;
    updateDesign(id, { locked: !d.locked });
  };

  const resetTransform = (id) => updateDesign(id, { rotation: 0, flipH: false, flipV: false, opacity: 1 });

  const nudge = (id, dx, dy) => {
    const d = designs.find(x => x.id === id);
    if (!d || d.locked) return;
    updateDesign(id, { x: d.x + dx, y: d.y + dy });
  };

  const deleteDesign = (id) => {
    setDesigns((prev) => prev.filter((d) => d.id !== id));
    if (selectedDesign?.id === id) setSelectedDesign(null);
  };

  // ---------------- Auto-nest (simple packing) ----------------
  const handleAutoNest = () => {
    if (!designs.length || !canvasRef.current) {
      toast({ title: "Nothing to nest", description: "Upload designs first", variant: "destructive" });
      return;
    }
    const rect = canvasRef.current.getBoundingClientRect();
    const maxW = rect.width;
    let cursorX = 5;
    let cursorY = 5;
    let rowH = 0;
    const newDesigns = [...designs].map(d => ({ ...d }));
    newDesigns.sort((a, b) => b.height - a.height);
    for (const d of newDesigns) {
      if (cursorX + d.width > maxW - 5) {
        cursorX = 5;
        cursorY += rowH + 5;
        rowH = 0;
      }
      d.x = cursorX;
      d.y = cursorY;
      cursorX += d.width + 5;
      rowH = Math.max(rowH, d.height);
    }
    setDesigns(newDesigns);
    toast({ title: "Auto-Nest complete", description: "Designs arranged" });
  };

  // ---------------- Pricing ----------------
  const calculatePrice = () => {
    const base = selectedTemplate.price || 0;
    const designCost = designs.length * 0.5;
    return +(base + designCost).toFixed(2);
  };

  // ---------------- BUY / Upload to backend ----------------
  // ---------------- BUY / Upload to backend + redirect ----------------


const buyNow = async () => {
  if (!designs.length) {
    toast({
      title: "No designs",
      description: "Please add at least one design",
      variant: "destructive"
    });
    return;
  }
  if (!canvasRef.current) {
    toast({ title: "Canvas missing", variant: "destructive" });
    return;
  }

  setLoading(true);
  toast({ title: "Uploading", description: "Creating product on Shopify..." });

  try {
    const displayRect = canvasRef.current.getBoundingClientRect();
    const displayW = displayRect.width;
    const displayH = displayRect.height;

    const DPI = 300;
    const highW = Math.round(selectedTemplate.width * DPI);
    const highH = Math.round(selectedTemplate.height * DPI);

    const exportCanvas = document.createElement("canvas");
    exportCanvas.width = highW;
    exportCanvas.height = highH;
    const ctx = exportCanvas.getContext("2d");
    ctx.fillStyle = "white";
    ctx.fillRect(0, 0, highW, highH);

    const sx = highW / displayW;
    const sy = highH / displayH;

    // draw each design
    for (const d of designs) {
      if (!d.visible) continue;
      const img = await new Promise((resolve, reject) => {
        const i = new Image();
        i.crossOrigin = "anonymous";
        i.onload = () => resolve(i);
        i.onerror = () => reject(new Error("Image load error"));
        i.src = d.src;
      });

      const dx = d.x * sx;
      const dy = d.y * sy;
      const dw = d.width * sx;
      const dh = d.height * sy;
      const cx = dx + dw / 2;
      const cy = dy + dh / 2;

      ctx.save();
      ctx.translate(cx, cy);
      ctx.rotate((d.rotation || 0) * Math.PI / 180);
      ctx.scale(d.flipH ? -1 : 1, d.flipV ? -1 : 1);
      ctx.globalAlpha = typeof d.opacity === "number" ? d.opacity : 1;
      ctx.drawImage(img, -dw / 2, -dh / 2, dw, dh);
      ctx.restore();
    }

    const blob = await new Promise((res) => exportCanvas.toBlob(res, "image/png", 0.95));
    if (!blob) throw new Error("Failed to create blob");

    const formData = new FormData();
    formData.append("name", `Custom Gang Sheet (${selectedTemplate.name})`);
    formData.append(
      "description",
      `Custom gang sheet with ${designs.length} designs (${selectedTemplate.width}" x ${selectedTemplate.height}")`
    );
    formData.append("price", String(calculatePrice()));
    formData.append("image", blob, `gang_sheet_${Date.now()}.png`);

    const res = await fetch(`${BACKEND_URL}/api/shopify/create-gang-sheet`, {
      method: "POST",
      body: formData
    });

    if (!res.ok) {
      const text = await res.text().catch(() => null);
      console.error("Upload failed:", res.status, text);
      throw new Error("Shopify create failed");
    }

    const data = await res.json();

    // Expect backend returns checkout_url (add this in backend)
    const checkoutUrl = data.cart?.checkout_url || data.checkout_url;

    if (checkoutUrl) {
      toast({ title: "Redirecting", description: "Taking you to checkout..." });
      window.location.href = checkoutUrl;
    } else {
      toast({
        title: "Missing checkout URL",
        description: "Product created but no checkout link returned.",
        variant: "destructive"
      });
    }
  } catch (err) {
    console.error("BuyNow error:", err);
    toast({
      title: "Error",
      description: err.message || "Failed to create product",
      variant: "destructive"
    });
  } finally {
    setLoading(false);
  }
};


  // display dims
  const { width: displayWidth, height: displayHeight } = displayCanvasDims();

  // ---------------- Render ----------------
  return (
    <div className="min-h-screen bg-gray-50">
      <Navigation />
      <div className="container mx-auto px-4 py-8">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold mb-2 text-gray-900">AI Gang Sheet Builder</h1>
          <p className="text-gray-600">Upload, arrange, and send your designs directly to Shopify.</p>
        </div>

        <div className="grid lg:grid-cols-4 gap-6">
          {/* Left */}
          <div className="space-y-6">
            <Card>
              <CardHeader><CardTitle>Templates</CardTitle></CardHeader>
              <CardContent>
                {gangSheetTemplates.map((t) => (
                  <div key={t.id} onClick={() => setSelectedTemplate(t)}
                    className={`p-3 rounded border cursor-pointer ${selectedTemplate.id === t.id ? "border-blue-500 bg-blue-50" : "border-gray-200 hover:border-gray-300"}`}>
                    <div className="flex justify-between">
                      <span>{t.name}</span>
                      <Badge>${t.price}</Badge>
                    </div>
                    <p className="text-xs text-gray-600">{t.width}" x {t.height}"</p>
                  </div>
                ))}
              </CardContent>
            </Card>

            <Card>
              <CardHeader><CardTitle>Upload Designs</CardTitle></CardHeader>
              <CardContent>
                <Button onClick={() => fileInputRef.current?.click()} variant="outline" className="w-full mb-3">
                  <Upload className="mr-2 h-4 w-4" /> Upload Images
                </Button>
                <input ref={fileInputRef} type="file" multiple accept="image/*" onChange={handleFileUpload} className="hidden" />
                <div className="text-xs text-gray-600 space-y-1">
                  <div>• Supported: JPG, PNG, SVG (SVG may rasterize)</div>
                  <div>• Recommended: 300 DPI for print</div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader><CardTitle>Tools</CardTitle></CardHeader>
              <CardContent>
                <Button className="w-full mb-2" onClick={handleAutoNest} disabled={!designs.length}>
                  <Sparkles className="mr-2 h-4 w-4" /> AI Auto-Nest
                </Button>
                <div className="flex space-x-2 mb-2">
                  <Button variant="outline" size="sm" onClick={() => setZoom(z => Math.max(25, z - 25))}><ZoomOut className="h-4 w-4" /></Button>
                  <div className="flex-1 text-center self-center text-sm">{zoom}%</div>
                  <Button variant="outline" size="sm" onClick={() => setZoom(z => Math.min(200, z + 25))}><ZoomIn className="h-4 w-4" /></Button>
                </div>
                <Button variant="outline" className="w-full" onClick={() => setShowGrid(s => !s)}>
                  <Grid className="mr-2 h-4 w-4" /> Toggle Grid
                </Button>
              </CardContent>
            </Card>
          </div>

          {/* Canvas */}
          <div className="lg:col-span-2">
            <Card>
              <CardContent className="p-0">
                <div
                  ref={canvasRef}
                  onClick={handleCanvasClick}
                  className="relative bg-white border-2 border-dashed border-gray-300 overflow-hidden cursor-crosshair mx-auto"
                  style={{ width: `${displayWidth}px`, height: `${displayHeight}px`, maxWidth: "100%", maxHeight: "600px" }}
                >
                  {showGrid && (
                    <div className="absolute inset-0 opacity-20"
                      style={{
                        backgroundImage: `
                          linear-gradient(to right, #000 1px, transparent 1px),
                          linear-gradient(to bottom, #000 1px, transparent 1px)
                        `,
                        backgroundSize: `${displayWidth / 12}px ${displayHeight / 12}px`
                      }} />
                  )}

                  {designs.map((d) => (
                    d.visible && (
                      <div
                        key={d.id}
                        onMouseDown={(e) => handleMouseDown(e, d)}
                        className={`absolute cursor-move ${selectedDesign?.id === d.id ? "ring-2 ring-blue-500 ring-offset-2" : "hover:ring-1 hover:ring-gray-400"}`}
                        style={{
                          left: `${d.x}px`,
                          top: `${d.y}px`,
                          width: `${d.width}px`,
                          height: `${d.height}px`,
                          transform: `rotate(${d.rotation}deg) scaleX(${d.flipH ? -1 : 1}) scaleY(${d.flipV ? -1 : 1})`,
                          transformOrigin: "center",
                          opacity: d.opacity
                        }}
                      >
                        <img src={d.src} alt={d.name} className="w-full h-full object-contain" draggable={false} />
                        {d.locked && <div className="absolute inset-0 flex items-center justify-center bg-white/20"><Lock className="w-4 h-4 text-gray-600" /></div>}
                      </div>
                    )
                  ))}

                  {!designs.length && (
                    <div className="absolute inset-0 flex items-center justify-center text-gray-400">
                      <Upload className="h-12 w-12 mr-2" />
                      <div>Upload designs to get started</div>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>

            <div className="text-center text-sm mt-2">
              {selectedTemplate.width}" × {selectedTemplate.height}" • Total Designs: {designs.length} • Estimated Price: <span className="font-semibold text-green-600">${calculatePrice().toFixed(2)}</span>
            </div>
          </div>

          {/* Right */}
          <div className="space-y-6">
            {selectedDesign && (
              <Card>
                <CardHeader><CardTitle>Design Properties</CardTitle></CardHeader>
                <CardContent className="space-y-3">
                  <div className="text-sm font-medium">{selectedDesign.name}</div>

                  <div className="grid grid-cols-2 gap-2">
                    <div>
                      <label className="text-xs">Width (px)</label>
                      <Input type="number" value={Math.round(selectedDesign.width)} onChange={(e) => updateDesignSize(selectedDesign.id, parseInt(e.target.value) || selectedDesign.width, selectedDesign.height)} className="text-xs" />
                    </div>
                    <div>
                      <label className="text-xs">Height (px)</label>
                      <Input type="number" value={Math.round(selectedDesign.height)} onChange={(e) => updateDesignSize(selectedDesign.id, selectedDesign.width, parseInt(e.target.value) || selectedDesign.height)} className="text-xs" />
                    </div>
                  </div>

                  <div>
                    <label className="text-xs">Opacity</label>
                    <input type="range" min="0" max="1" step="0.01" value={selectedDesign.opacity} onChange={(e) => updateDesign(selectedDesign.id, { opacity: parseFloat(e.target.value) })} className="w-full" />
                  </div>

                  <div className="grid grid-cols-3 gap-2">
                    <Button size="sm" onClick={() => rotateDesign(selectedDesign.id, -15)}><RotateCw /></Button>
                    <Button size="sm" onClick={() => rotateDesign(selectedDesign.id, 15)}><RotateCw style={{ transform: "scaleX(-1)" }} /></Button>
                    <Button size="sm" onClick={() => toggleFlip(selectedDesign.id, "h")}><CornerUpLeft /></Button>
                    <Button size="sm" onClick={() => toggleFlip(selectedDesign.id, "v")}><CornerUpRight /></Button>
                    <Button size="sm" onClick={() => duplicateDesign(selectedDesign.id)}><Copy /></Button>
                    <Button size="sm" onClick={() => toggleLock(selectedDesign.id)}>{selectedDesign.locked ? <Unlock /> : <Lock />}</Button>
                  </div>

                  <div className="flex space-x-2">
                    <Button variant="outline" size="sm" onClick={() => bringToFront(selectedDesign.id)}><ArrowUpCircle /> Front</Button>
                    <Button variant="outline" size="sm" onClick={() => sendToBack(selectedDesign.id)}><ArrowDownCircle /> Back</Button>
                    <Button variant="outline" size="sm" onClick={() => toggleVisibility(selectedDesign.id)}>{selectedDesign.visible ? <Eye /> : <EyeOff />} {selectedDesign.visible ? "Visible" : "Hidden"}</Button>
                  </div>

                  <div className="flex space-x-2">
                    <Button variant="outline" size="sm" onClick={() => resetTransform(selectedDesign.id)}>Reset</Button>
                    <Button variant="destructive" size="sm" onClick={() => deleteDesign(selectedDesign.id)}><Trash2 /> Delete</Button>
                  </div>

                  <div className="grid grid-cols-3 gap-2 text-center">
                    <Button size="sm" onClick={() => nudge(selectedDesign.id, 0, -1)}>↑</Button>
                    <Button size="sm" onClick={() => nudge(selectedDesign.id, -1, 0)}>←</Button>
                    <Button size="sm" onClick={() => nudge(selectedDesign.id, 1, 0)}>→</Button>
                    <Button size="sm" onClick={() => nudge(selectedDesign.id, 0, 1)}>↓</Button>
                    <Button size="sm" onClick={() => nudge(selectedDesign.id, 0, -5)}>↑5</Button>
                    <Button size="sm" onClick={() => nudge(selectedDesign.id, 0, 5)}>↓5</Button>
                  </div>
                </CardContent>
              </Card>
            )}

            <Card>
              <CardHeader><CardTitle>Order Summary</CardTitle></CardHeader>
              <CardContent className="space-y-3">
                <div className="flex justify-between text-sm"><span>Base ({selectedTemplate.name})</span><span>${selectedTemplate.price}</span></div>
                <div className="flex justify-between text-sm"><span>Designs ({designs.length} × $0.50)</span><span>${(designs.length * 0.5).toFixed(2)}</span></div>
                <div className="border-t pt-2 flex justify-between font-semibold"><span>Total</span><span>${calculatePrice().toFixed(2)}</span></div>
<Button
  onClick={buyNow}
  className="w-full bg-blue-600 hover:bg-blue-700 mt-2 flex items-center justify-center"
  disabled={!designs.length || loading}
>
  {loading ? (
    <>
      <svg
        className="animate-spin h-4 w-4 mr-2 text-white"
        xmlns="http://www.w3.org/2000/svg"
        fill="none"
        viewBox="0 0 24 24"
      >
        <circle
          className="opacity-25"
          cx="12"
          cy="12"
          r="10"
          stroke="currentColor"
          strokeWidth="4"
        ></circle>
        <path
          className="opacity-75"
          fill="currentColor"
          d="M4 12a8 8 0 018-8v4l3.5-3.5L12 1v4a8 8 0 000 16v4l3.5-3.5L12 19v4a8 8 0 01-8-8z"
        ></path>
      </svg>
      Processing...
    </>
  ) : (
    <>
      <ShoppingCart className="mr-2 h-4 w-4" /> Buy Now
    </>
  )}
</Button>


                <Button variant="outline" className="w-full mt-2" disabled={!designs.length} onClick={async () => {
                  try {
                    const rect = canvasRef.current.getBoundingClientRect();
                    const exportCanvas = document.createElement("canvas");
                    exportCanvas.width = rect.width;
                    exportCanvas.height = rect.height;
                    const ctx = exportCanvas.getContext("2d");
                    ctx.fillStyle = "white";
                    ctx.fillRect(0, 0, exportCanvas.width, exportCanvas.height);
                    for (const d of designs) {
                      if (!d.visible) continue;
                      const img = new Image();
                      await new Promise((res, rej) => {
                        img.onload = () => { ctx.drawImage(img, d.x, d.y, d.width, d.height); res(); };
                        img.onerror = rej;
                        img.src = d.src;
                      });
                    }
                    const url = exportCanvas.toDataURL("image/png");
                    const a = document.createElement("a");
                    a.href = url;
                    a.download = `gangsheet_preview_${Date.now()}.png`;
                    a.click();
                  } catch (err) {
                    toast({ title: "Export failed", description: err.message || "Could not export preview", variant: "destructive" });
                  }
                }}>
                  <Download className="mr-2 h-4 w-4" /> Export Preview
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
