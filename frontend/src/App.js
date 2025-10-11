import React from "react";
import "./App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { Toaster } from "./components/ui/toaster";
import HomePage from "./pages/HomePage";
import ProductsPage from "./pages/ProductsPage";
import GangSheetBuilder from "./pages/GangSheetBuilder";
import EducationPage from "./pages/EducationPage";
import AboutPage from "./pages/AboutPage";
import ContactPage from "./pages/ContactPage";
import CartPage from "./pages/CartPage";
import { CartProvider } from "./context/CartContext";

function App() {
  return (
    <CartProvider>
      <div className="App">
        <BrowserRouter>
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/products" element={<ProductsPage />} />
            <Route path="/products/:category" element={<ProductsPage />} />
            <Route path="/gang-sheet-builder" element={<GangSheetBuilder />} />
            <Route path="/education" element={<EducationPage />} />
            <Route path="/about" element={<AboutPage />} />
            <Route path="/contact" element={<ContactPage />} />
            <Route path="/cart" element={<CartPage />} />
          </Routes>
          <Toaster />
        </BrowserRouter>
      </div>
    </CartProvider>
  );
}

export default App;