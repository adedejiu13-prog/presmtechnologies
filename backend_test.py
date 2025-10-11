#!/usr/bin/env python3
"""
Comprehensive Backend API Tests for PRESM Technologies
Tests all API endpoints including Products, Gang Sheets, Cart, and Health checks
"""

import requests
import json
import uuid
from typing import Dict, Any, List
import sys

# Backend URL from frontend .env
BASE_URL = "https://presm-transfers-1.preview.emergentagent.com/api"

class PRESMAPITester:
    def __init__(self):
        self.base_url = BASE_URL
        self.session = requests.Session()
        self.session_id = str(uuid.uuid4())
        self.session.headers.update({
            'Content-Type': 'application/json',
            'x-session-id': self.session_id
        })
        self.test_results = []
        self.created_resources = []  # Track created resources for cleanup
        
    def log_test(self, test_name: str, success: bool, details: str = "", response_data: Any = None):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"   Details: {details}")
        if response_data and not success:
            print(f"   Response: {response_data}")
        print()
        
        self.test_results.append({
            'test': test_name,
            'success': success,
            'details': details,
            'response': response_data
        })
    
    def test_health_endpoints(self):
        """Test basic health and root endpoints"""
        print("=== TESTING HEALTH & BASIC ENDPOINTS ===")
        
        # Test root endpoint
        try:
            response = self.session.get(f"{self.base_url}/")
            if response.status_code == 200:
                data = response.json()
                if "PRESM Technologies API" in data.get("message", ""):
                    self.log_test("GET /api/ - Root endpoint", True, f"Status: {response.status_code}")
                else:
                    self.log_test("GET /api/ - Root endpoint", False, f"Unexpected response: {data}")
            else:
                self.log_test("GET /api/ - Root endpoint", False, f"Status: {response.status_code}", response.text)
        except Exception as e:
            self.log_test("GET /api/ - Root endpoint", False, f"Exception: {str(e)}")
        
        # Test health endpoint
        try:
            response = self.session.get(f"{self.base_url}/health")
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "healthy":
                    self.log_test("GET /api/health - Health check", True, f"Status: {response.status_code}")
                else:
                    self.log_test("GET /api/health - Health check", False, f"Unexpected response: {data}")
            else:
                self.log_test("GET /api/health - Health check", False, f"Status: {response.status_code}", response.text)
        except Exception as e:
            self.log_test("GET /api/health - Health check", False, f"Exception: {str(e)}")
    
    def test_products_endpoints(self):
        """Test all products API endpoints"""
        print("=== TESTING PRODUCTS API ENDPOINTS ===")
        
        # Test get all products
        try:
            response = self.session.get(f"{self.base_url}/products/")
            if response.status_code == 200:
                products = response.json()
                if isinstance(products, list) and len(products) == 6:
                    self.log_test("GET /api/products/ - Get all products", True, f"Found {len(products)} products")
                    # Store first product ID for individual product test
                    if products:
                        self.first_product_id = products[0].get('_id')
                        print(f"   First product ID: {self.first_product_id}")
                else:
                    self.log_test("GET /api/products/ - Get all products", False, f"Expected 6 products, got {len(products) if isinstance(products, list) else 'non-list'}")
            else:
                self.log_test("GET /api/products/ - Get all products", False, f"Status: {response.status_code}", response.text)
        except Exception as e:
            self.log_test("GET /api/products/ - Get all products", False, f"Exception: {str(e)}")
        
        # Test get categories
        try:
            response = self.session.get(f"{self.base_url}/products/categories")
            if response.status_code == 200:
                categories = response.json()
                expected_categories = ["dtf-transfers", "gang-sheets", "heat-presses", "supplies", "accessories", "custom-designs"]
                if isinstance(categories, list) and len(categories) == 6:
                    found_categories = [cat.get('category') for cat in categories if isinstance(cat, dict)]
                    if all(cat in found_categories for cat in expected_categories):
                        self.log_test("GET /api/products/categories - Get categories", True, f"Found {len(categories)} categories with counts")
                    else:
                        self.log_test("GET /api/products/categories - Get categories", False, f"Missing expected categories. Found: {found_categories}")
                else:
                    self.log_test("GET /api/products/categories - Get categories", False, f"Expected list of 6 categories, got {len(categories) if isinstance(categories, list) else 'non-list'}")
            else:
                self.log_test("GET /api/products/categories - Get categories", False, f"Status: {response.status_code}", response.text)
        except Exception as e:
            self.log_test("GET /api/products/categories - Get categories", False, f"Exception: {str(e)}")
        
        # Test individual product by ID
        if hasattr(self, 'first_product_id') and self.first_product_id:
            try:
                response = self.session.get(f"{self.base_url}/products/{self.first_product_id}")
                if response.status_code == 200:
                    product = response.json()
                    if product.get('_id') == self.first_product_id:
                        self.log_test("GET /api/products/{id} - Get individual product", True, f"Retrieved product: {product.get('name')}")
                    else:
                        self.log_test("GET /api/products/{id} - Get individual product", False, f"ID mismatch")
                else:
                    self.log_test("GET /api/products/{id} - Get individual product", False, f"Status: {response.status_code}", response.text)
            except Exception as e:
                self.log_test("GET /api/products/{id} - Get individual product", False, f"Exception: {str(e)}")
        
        # Test invalid product ID
        try:
            response = self.session.get(f"{self.base_url}/products/invalid-id-12345")
            if response.status_code == 404:
                self.log_test("GET /api/products/{invalid_id} - Invalid product ID", True, "Correctly returned 404")
            else:
                self.log_test("GET /api/products/{invalid_id} - Invalid product ID", False, f"Expected 404, got {response.status_code}")
        except Exception as e:
            self.log_test("GET /api/products/{invalid_id} - Invalid product ID", False, f"Exception: {str(e)}")
        
        # Test category filtering
        categories_to_test = ["dtf-transfers", "gang-sheets", "heat-presses"]
        for category in categories_to_test:
            try:
                response = self.session.get(f"{self.base_url}/products/?category={category}")
                if response.status_code == 200:
                    products = response.json()
                    if isinstance(products, list):
                        # Check if all products belong to the requested category
                        if all(p.get('category') == category for p in products):
                            self.log_test(f"GET /api/products/?category={category} - Filter by category", True, f"Found {len(products)} products")
                        else:
                            self.log_test(f"GET /api/products/?category={category} - Filter by category", False, "Some products don't match category")
                    else:
                        self.log_test(f"GET /api/products/?category={category} - Filter by category", False, "Response is not a list")
                else:
                    self.log_test(f"GET /api/products/?category={category} - Filter by category", False, f"Status: {response.status_code}")
            except Exception as e:
                self.log_test(f"GET /api/products/?category={category} - Filter by category", False, f"Exception: {str(e)}")
        
        # Test search functionality
        search_terms = ["DTF", "Heat", "Custom"]
        for term in search_terms:
            try:
                response = self.session.get(f"{self.base_url}/products/?search={term}")
                if response.status_code == 200:
                    products = response.json()
                    if isinstance(products, list):
                        # Check if search term appears in name or description
                        relevant_products = [p for p in products if term.lower() in p.get('name', '').lower() or term.lower() in p.get('description', '').lower()]
                        if len(relevant_products) > 0:
                            self.log_test(f"GET /api/products/?search={term} - Search functionality", True, f"Found {len(relevant_products)} relevant products")
                        else:
                            self.log_test(f"GET /api/products/?search={term} - Search functionality", False, f"No relevant products found for '{term}'")
                    else:
                        self.log_test(f"GET /api/products/?search={term} - Search functionality", False, "Response is not a list")
                else:
                    self.log_test(f"GET /api/products/?search={term} - Search functionality", False, f"Status: {response.status_code}")
            except Exception as e:
                self.log_test(f"GET /api/products/?search={term} - Search functionality", False, f"Exception: {str(e)}")
    
    def test_gang_sheets_endpoints(self):
        """Test gang sheets API endpoints"""
        print("=== TESTING GANG SHEETS API ENDPOINTS ===")
        
        # Test get gang sheet templates
        try:
            response = self.session.get(f"{self.base_url}/gang-sheets/templates")
            if response.status_code == 200:
                templates = response.json()
                expected_templates = ["12x16", "22x24", "8.5x11"]
                if isinstance(templates, list) and len(templates) == 3:
                    template_names = [t.get('name') for t in templates if isinstance(t, dict)]
                    if all(name in str(templates) for name in expected_templates):
                        self.log_test("GET /api/gang-sheets/templates - Get templates", True, f"Found {len(templates)} templates")
                    else:
                        self.log_test("GET /api/gang-sheets/templates - Get templates", False, f"Missing expected templates. Found: {templates}")
                else:
                    self.log_test("GET /api/gang-sheets/templates - Get templates", False, f"Expected 3 templates, got {len(templates) if isinstance(templates, list) else 'non-list'}")
            else:
                self.log_test("GET /api/gang-sheets/templates - Get templates", False, f"Status: {response.status_code}", response.text)
        except Exception as e:
            self.log_test("GET /api/gang-sheets/templates - Get templates", False, f"Exception: {str(e)}")
        
        # Test create gang sheet
        try:
            gang_sheet_data = {
                "template_id": "12x16",
                "template_name": "12x16",
                "width": 12.0,
                "height": 16.0,
                "base_price": 18.99,
                "user_id": "test-user-123"
            }
            response = self.session.post(f"{self.base_url}/gang-sheets/", json=gang_sheet_data)
            if response.status_code == 200:
                gang_sheet = response.json()
                if gang_sheet.get('template_name') == "12x16":
                    self.created_gang_sheet_id = gang_sheet.get('_id')
                    self.created_resources.append(('gang_sheet', self.created_gang_sheet_id))
                    self.log_test("POST /api/gang-sheets/ - Create gang sheet", True, f"Created gang sheet: {self.created_gang_sheet_id}")
                else:
                    self.log_test("POST /api/gang-sheets/ - Create gang sheet", False, f"Unexpected response: {gang_sheet}")
            else:
                self.log_test("POST /api/gang-sheets/ - Create gang sheet", False, f"Status: {response.status_code}", response.text)
        except Exception as e:
            self.log_test("POST /api/gang-sheets/ - Create gang sheet", False, f"Exception: {str(e)}")
        
        # Test add design to gang sheet (if gang sheet was created)
        if hasattr(self, 'created_gang_sheet_id') and self.created_gang_sheet_id:
            try:
                design_data = {
                    "name": "Test Design",
                    "file_data": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==",
                    "x": 10.0,
                    "y": 10.0,
                    "quantity": 2
                }
                response = self.session.post(f"{self.base_url}/gang-sheets/{self.created_gang_sheet_id}/designs", json=design_data)
                if response.status_code == 200:
                    updated_sheet = response.json()
                    if len(updated_sheet.get('designs', [])) > 0:
                        self.log_test("POST /api/gang-sheets/{id}/designs - Add design", True, "Design added successfully")
                    else:
                        self.log_test("POST /api/gang-sheets/{id}/designs - Add design", False, "No designs found in response")
                else:
                    self.log_test("POST /api/gang-sheets/{id}/designs - Add design", False, f"Status: {response.status_code}", response.text)
            except Exception as e:
                self.log_test("POST /api/gang-sheets/{id}/designs - Add design", False, f"Exception: {str(e)}")
            
            # Test auto-nest functionality
            try:
                response = self.session.post(f"{self.base_url}/gang-sheets/{self.created_gang_sheet_id}/auto-nest")
                if response.status_code == 200:
                    updated_sheet = response.json()
                    self.log_test("POST /api/gang-sheets/{id}/auto-nest - Auto-nest designs", True, "Auto-nest completed")
                else:
                    self.log_test("POST /api/gang-sheets/{id}/auto-nest - Auto-nest designs", False, f"Status: {response.status_code}", response.text)
            except Exception as e:
                self.log_test("POST /api/gang-sheets/{id}/auto-nest - Auto-nest designs", False, f"Exception: {str(e)}")
        else:
            self.log_test("POST /api/gang-sheets/{id}/designs - Add design", False, "No gang sheet ID available")
            self.log_test("POST /api/gang-sheets/{id}/auto-nest - Auto-nest designs", False, "No gang sheet ID available")
    
    def test_cart_endpoints(self):
        """Test cart API endpoints"""
        print("=== TESTING CART API ENDPOINTS ===")
        
        # Test get cart (should be empty initially)
        try:
            response = self.session.get(f"{self.base_url}/cart/")
            if response.status_code == 200:
                cart = response.json()
                if isinstance(cart, dict) and cart.get('session_id') == self.session_id:
                    self.log_test("GET /api/cart/ - Get cart", True, f"Cart retrieved for session: {self.session_id}")
                else:
                    self.log_test("GET /api/cart/ - Get cart", False, f"Unexpected cart response: {cart}")
            else:
                self.log_test("GET /api/cart/ - Get cart", False, f"Status: {response.status_code}", response.text)
        except Exception as e:
            self.log_test("GET /api/cart/ - Get cart", False, f"Exception: {str(e)}")
        
        # Test add item to cart (need a product ID first)
        if hasattr(self, 'first_product_id') and self.first_product_id:
            try:
                cart_item = {
                    "product_id": self.first_product_id,
                    "quantity": 2,
                    "options": {"size": "4x4"}
                }
                response = self.session.post(f"{self.base_url}/cart/items", json=cart_item)
                if response.status_code == 200:
                    cart = response.json()
                    if len(cart.get('items', [])) > 0:
                        self.log_test("POST /api/cart/items - Add item to cart", True, f"Item added, cart has {len(cart['items'])} items")
                    else:
                        self.log_test("POST /api/cart/items - Add item to cart", False, "No items found in cart after adding")
                else:
                    self.log_test("POST /api/cart/items - Add item to cart", False, f"Status: {response.status_code}", response.text)
            except Exception as e:
                self.log_test("POST /api/cart/items - Add item to cart", False, f"Exception: {str(e)}")
        else:
            self.log_test("POST /api/cart/items - Add item to cart", False, "No product ID available for testing")
        
        # Test cart session management with different session ID
        try:
            different_session = str(uuid.uuid4())
            headers = {'x-session-id': different_session}
            response = self.session.get(f"{self.base_url}/cart/", headers=headers)
            if response.status_code == 200:
                cart = response.json()
                if cart.get('session_id') == different_session:
                    self.log_test("GET /api/cart/ - Session management", True, f"Different session cart retrieved: {different_session}")
                else:
                    self.log_test("GET /api/cart/ - Session management", False, f"Session ID mismatch")
            else:
                self.log_test("GET /api/cart/ - Session management", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("GET /api/cart/ - Session management", False, f"Exception: {str(e)}")
        
        # Test cart summary
        try:
            response = self.session.get(f"{self.base_url}/cart/summary")
            if response.status_code == 200:
                summary = response.json()
                required_fields = ['total_items', 'subtotal', 'shipping', 'tax', 'total']
                if all(field in summary for field in required_fields):
                    self.log_test("GET /api/cart/summary - Cart summary", True, f"Summary: {summary['total_items']} items, ${summary['total']}")
                else:
                    self.log_test("GET /api/cart/summary - Cart summary", False, f"Missing required fields in summary")
            else:
                self.log_test("GET /api/cart/summary - Cart summary", False, f"Status: {response.status_code}", response.text)
        except Exception as e:
            self.log_test("GET /api/cart/summary - Cart summary", False, f"Exception: {str(e)}")
    
    def test_error_scenarios(self):
        """Test various error scenarios"""
        print("=== TESTING ERROR SCENARIOS ===")
        
        # Test malformed JSON
        try:
            response = self.session.post(f"{self.base_url}/cart/items", data="invalid json")
            if response.status_code in [400, 422]:
                self.log_test("POST with malformed JSON - Error handling", True, f"Correctly returned {response.status_code}")
            else:
                self.log_test("POST with malformed JSON - Error handling", False, f"Expected 400/422, got {response.status_code}")
        except Exception as e:
            self.log_test("POST with malformed JSON - Error handling", False, f"Exception: {str(e)}")
        
        # Test non-existent endpoints
        try:
            response = self.session.get(f"{self.base_url}/nonexistent")
            if response.status_code == 404:
                self.log_test("GET /api/nonexistent - 404 handling", True, "Correctly returned 404")
            else:
                self.log_test("GET /api/nonexistent - 404 handling", False, f"Expected 404, got {response.status_code}")
        except Exception as e:
            self.log_test("GET /api/nonexistent - 404 handling", False, f"Exception: {str(e)}")
    
    def run_all_tests(self):
        """Run all test suites"""
        print(f"🚀 Starting PRESM Technologies Backend API Tests")
        print(f"📍 Base URL: {self.base_url}")
        print(f"🔑 Session ID: {self.session_id}")
        print("=" * 60)
        
        self.test_health_endpoints()
        self.test_products_endpoints()
        self.test_gang_sheets_endpoints()
        self.test_cart_endpoints()
        self.test_error_scenarios()
        
        # Summary
        print("=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for result in self.test_results if result['success'])
        failed = len(self.test_results) - passed
        
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"📈 Success Rate: {(passed/len(self.test_results)*100):.1f}%")
        
        if failed > 0:
            print("\n🔍 FAILED TESTS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"   ❌ {result['test']}: {result['details']}")
        
        print("\n" + "=" * 60)
        return passed, failed

if __name__ == "__main__":
    tester = PRESMAPITester()
    passed, failed = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if failed == 0 else 1)