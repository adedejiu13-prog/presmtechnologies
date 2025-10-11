export const products = [
  {
    id: 1,
    name: "Standard DTF Transfer",
    category: "dtf-transfers",
    price: 2.50,
    image: "https://images.unsplash.com/photo-1556742049-0cfed4f6a45d?w=400&h=400&fit=crop",
    description: "High-quality direct-to-film transfers with vibrant colors and excellent durability.",
    features: ["Premium PET film", "Vivid colors", "Cold peel", "Machine washable"],
    sizes: ["2x2", "3x3", "4x4", "5x5", "6x6", "8x8", "10x10", "12x12"],
    minQuantity: 1,
    maxQuantity: 1000
  },
  {
    id: 2,
    name: "Gang Sheet 12x16",
    category: "gang-sheets",
    price: 18.99,
    image: "https://images.unsplash.com/photo-1561070791-2526d30994b5?w=400&h=400&fit=crop",
    description: "Maximize efficiency with our 12x16 gang sheets. Perfect for multiple small designs.",
    features: ["12x16 inch sheet", "Multiple designs", "Cost effective", "Fast turnaround"],
    sizes: ["12x16"],
    minQuantity: 1,
    maxQuantity: 100
  },
  {
    id: 3,
    name: "Professional Heat Press 15x15",
    category: "heat-presses",
    price: 299.99,
    image: "https://images.unsplash.com/photo-1586796676553-f4c9c5ba5b12?w=400&h=400&fit=crop",
    description: "Professional-grade heat press machine with digital temperature and time control.",
    features: ["15x15 inch platen", "Digital controls", "Even heat distribution", "1-year warranty"],
    sizes: ["15x15"],
    minQuantity: 1,
    maxQuantity: 10
  },
  {
    id: 4,
    name: "DTF Powder Adhesive",
    category: "supplies",
    price: 24.99,
    image: "https://images.unsplash.com/photo-1564013799919-ab600027ffc6?w=400&h=400&fit=crop",
    description: "Premium hot melt adhesive powder for DTF transfers. 1lb container.",
    features: ["1lb container", "Easy application", "Strong adhesion", "Washable"],
    sizes: ["1lb"],
    minQuantity: 1,
    maxQuantity: 50
  },
  {
    id: 5,
    name: "Teflon Sheets (Pack of 5)",
    category: "accessories",
    price: 15.99,
    image: "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400&h=400&fit=crop",
    description: "High-quality teflon sheets for heat pressing. Reusable and non-stick.",
    features: ["Pack of 5", "Non-stick surface", "Reusable", "Heat resistant"],
    sizes: ["16x20"],
    minQuantity: 1,
    maxQuantity: 20
  },
  {
    id: 6,
    name: "Custom Design Service",
    category: "custom-designs",
    price: 49.99,
    image: "https://images.unsplash.com/photo-1541701494587-cb58502866ab?w=400&h=400&fit=crop",
    description: "Professional custom design service. Our team creates unique designs for your brand.",
    features: ["Professional design", "Unlimited revisions", "Commercial license", "48hr turnaround"],
    sizes: ["Custom"],
    minQuantity: 1,
    maxQuantity: 10
  }
];

export const educationContent = [
  {
    id: 1,
    title: "Heat Press Instructions for DTF Transfers",
    category: "heat-press-guide",
    excerpt: "Step-by-step guide to applying DTF transfers with perfect results every time.",
    content: `
# Heat Press Instructions for DTF Transfers

## Temperature & Timing
- **Temperature:** 310°F (155°C)
- **Pressure:** Medium-High
- **Time:** 12-15 seconds
- **Peel:** Cold peel (wait 10-15 seconds)

## Step-by-Step Process

### 1. Prepare Your Workspace
- Clean your heat press platen
- Use a teflon sheet or parchment paper
- Ensure garment is wrinkle-free

### 2. Position the Transfer
- Place DTF transfer face down on garment
- Ensure proper alignment
- Use heat tape if needed for positioning

### 3. Press Application
1. Close heat press firmly
2. Apply for 12-15 seconds
3. Open press and wait 10-15 seconds
4. Peel transfer film slowly at 45-degree angle

### 4. Final Press
- Cover design with teflon sheet
- Press for 5-10 seconds to ensure adhesion
- Allow to cool completely

## Pro Tips
- Always do a test press on similar fabric
- Adjust time based on fabric thickness
- Store transfers in cool, dry place
- Use light pressure for delicate fabrics
    `,
    videoUrl: "https://www.youtube.com/embed/dQw4w9WgXcQ",
    tags: ["heat press", "dtf", "application", "tutorial"]
  },
  {
    id: 2,
    title: "Design Tips for DTF Success",
    category: "design-tips",
    excerpt: "Essential design considerations for creating stunning DTF transfers.",
    content: `
# Design Tips for DTF Success

## Resolution Requirements
- **Minimum:** 300 DPI at final size
- **Recommended:** 600 DPI for fine details
- **Format:** PNG with transparent background

## Color Considerations
- Use CMYK color mode for printing
- Avoid pure white (use cream/off-white)
- High contrast designs work best
- Consider fabric color in design

## Design Elements
### Text
- Minimum font size: 8pt
- Sans-serif fonts recommended
- Avoid thin lines under 1pt

### Graphics
- Bold, simple designs work best
- Avoid gradients in small areas
- Sharp, clean edges preferred
- Consider white underbase for dark garments

## File Preparation
1. Create design at actual size
2. Use transparent background
3. Flatten all layers
4. Save as high-resolution PNG
5. Include bleed area if needed

## Common Mistakes to Avoid
- Too small text or details
- Designs without white underbase
- Low resolution files
- Complex gradients
- Thin decorative elements
    `,
    tags: ["design", "dtf", "tips", "graphics"]
  }
];

export const testimonials = [
  {
    id: 1,
    name: "Sarah Johnson",
    business: "Custom Apparel Co.",
    rating: 5,
    text: "PRESM Technologies has transformed our business. The gang sheet builder is a game-changer for efficiency!",
    avatar: "https://images.unsplash.com/photo-1494790108755-2616b612b786?w=100&h=100&fit=crop&crop=face"
  },
  {
    id: 2,
    name: "Mike Rodriguez",
    business: "Print Shop Pro",
    rating: 5,
    text: "Quality is outstanding and customer service is top-notch. Highly recommend for any print business.",
    avatar: "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=100&h=100&fit=crop&crop=face"
  },
  {
    id: 3,
    name: "Emily Chen",
    business: "Creative Designs LLC",
    rating: 5,
    text: "The heat press equipment is reliable and the DTF transfers have amazing color quality and durability.",
    avatar: "https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=100&h=100&fit=crop&crop=face"
  }
];

export const gangSheetTemplates = [
  {
    id: 1,
    name: "12x16 Standard Sheet",
    width: 12,
    height: 16,
    price: 18.99,
    maxDesigns: 50,
    image: "https://images.unsplash.com/photo-1561070791-2526d30994b5?w=300&h=200&fit=crop"
  },
  {
    id: 2,
    name: "22x24 Large Sheet",
    width: 22,
    height: 24,
    price: 45.99,
    maxDesigns: 100,
    image: "https://images.unsplash.com/photo-1586796676553-f4c9c5ba5b12?w=300&h=200&fit=crop"
  },
  {
    id: 3,
    name: "8.5x11 Small Sheet",
    width: 8.5,
    height: 11,
    price: 12.99,
    maxDesigns: 25,
    image: "https://images.unsplash.com/photo-1564013799919-ab600027ffc6?w=300&h=200&fit=crop"
  }
];