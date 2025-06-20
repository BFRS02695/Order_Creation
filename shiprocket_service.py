import requests
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime

class ShiprocketAPI:
    """Integration with Shiprocket API for order creation"""
    
    def __init__(self, email: str, password: str):
        """Initialize with Shiprocket credentials"""
        self.base_url = "https://apiv2.shiprocket.in/v1"
        self.email = email
        self.password = password
        self.auth_token = None
        
        # Configure logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def authenticate(self) -> bool:
        """Authenticate with Shiprocket API and get token"""
        self.logger.info("Authenticating with Shiprocket API")
        
        url = f"{self.base_url}/auth/login"
        payload = {
            "email": self.email,
            "password": self.password
        }
        headers = {
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get('token')
                self.logger.info("Authentication successful")
                return True
            else:
                self.logger.error(f"Authentication failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.logger.error(f"Authentication error: {str(e)}")
            return False
    
    def create_order_from_invoice(self, invoice_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create Shiprocket order from invoice data"""
        self.logger.info("Creating Shiprocket order from invoice data")
        
        # Ensure we have an auth token
        if not self.auth_token:
            if not self.authenticate():
                raise Exception("Failed to authenticate with Shiprocket")
        
        # Generate order ID if not provided
        order_id = invoice_data.get('invoice_number')
        if not order_id:
            order_id = f"INV-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
        # Get order date or use current date
        order_date = invoice_data.get('order_date')
        if not order_date:
            order_date = datetime.now().strftime('%Y-%m-%d')
            
        # Prepare order payload
        order_payload = {
            "order_id": order_id,
            "order_date": order_date,
            "channel_id": "",
            
            # Billing Information
            "billing_customer_name": invoice_data.get('billing_customer_name', ''),
            "billing_address": invoice_data.get('billing_address', ''),
            "billing_city": invoice_data.get('billing_city', ''),
            "billing_state": invoice_data.get('billing_state', ''),
            "billing_country": "India",
            "billing_pincode": invoice_data.get('billing_pincode', ''),
            "billing_email": invoice_data.get('billing_email', ''),
            "billing_phone": invoice_data.get('billing_phone', ''),
            "billing_isd_code": "+91",
            
            # Shipping Information (default to billing if not provided)
            "shipping_is_billing": 0,  # Default to separate shipping address
            "shipping_customer_name": invoice_data.get('shipping_customer_name') or invoice_data.get('billing_customer_name', ''),
            "shipping_address": invoice_data.get('shipping_address') or invoice_data.get('billing_address', ''),
            "shipping_city": invoice_data.get('shipping_city') or invoice_data.get('billing_city', ''),
            "shipping_state": invoice_data.get('shipping_state') or invoice_data.get('billing_state', ''),
            "shipping_country": "India",
            "shipping_pincode": invoice_data.get('shipping_pincode') or invoice_data.get('billing_pincode', ''),
            "shipping_email": invoice_data.get('shipping_email') or invoice_data.get('billing_email', ''),
            "shipping_phone": invoice_data.get('shipping_phone') or invoice_data.get('billing_phone', ''),
            
            # Order Items
            "order_items": self.format_order_items(invoice_data.get('order_items', [])),
            
            # Payment and Totals
            "payment_method": invoice_data.get('payment_method', 'prepaid').lower(),
            "sub_total": invoice_data.get('sub_total', 0),
            "total_discount": 0,
            "shipping_charges": 0,
            "giftwrap_charges": 0,
            "transaction_charges": 0,
            
            # Package Details (estimated)
            "weight": self.calculate_total_weight(invoice_data.get('order_items', [])),
            "length": 10,  # Default values
            "breadth": 10,
            "height": 10,
            
            # Additional Fields
            "pickup_location": "Primary",  # Should be configured based on requirements
            "customer_gstin": invoice_data.get('billing_gstin', ''),
            "is_order_revamp": 1,
            "is_document": 0,
            "is_web": 1,
            "is_send_notification": True,
            "is_insurance_opt": 0,
            "currency": "INR"
        }
        
        # Check if shipping is same as billing
        if (order_payload["shipping_address"] == order_payload["billing_address"] and
            order_payload["shipping_pincode"] == order_payload["billing_pincode"] and
            order_payload["shipping_customer_name"] == order_payload["billing_customer_name"]):
            order_payload["shipping_is_billing"] = 1
        
        # Create order via API
        url = f"{self.base_url}/orders/create/adhoc"
        headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
        
        self.logger.info(f"Sending order request: {json.dumps(order_payload, indent=2)}")
        
        try:
            response = requests.post(url, json=order_payload, headers=headers)
            
            if response.status_code in [200, 201]:
                result = response.json()
                self.logger.info(f"Order created successfully: {result.get('order_id')}")
                return result
            else:
                # Check if token expired
                if response.status_code == 401:
                    self.logger.warning("Authentication token expired, re-authenticating")
                    if self.authenticate():
                        # Retry with new token
                        headers["Authorization"] = f"Bearer {self.auth_token}"
                        response = requests.post(url, json=order_payload, headers=headers)
                        
                        if response.status_code in [200, 201]:
                            result = response.json()
                            self.logger.info(f"Order created successfully after re-auth: {result.get('order_id')}")
                            return result
                
                error_msg = f"Order creation failed: {response.status_code} - {response.text}"
                self.logger.error(error_msg)
                return {"error": error_msg, "status": "failed"}
                
        except Exception as e:
            error_msg = f"Error creating order: {str(e)}"
            self.logger.error(error_msg)
            return {"error": error_msg, "status": "failed"}
    
    def format_order_items(self, items: list) -> list:
        """Format order items for Shiprocket API"""
        formatted_items = []
        
        if not items:
            # Add a default item if none provided
            return [{
                "name": "Default Item",
                "selling_price": "100",
                "units": 1,
                "sku": "DEFAULT001",
                "hsn": "",
                "weight": 0.5,
                "category_name": None,
                "tax": None,
                "discount": None,
                "product_description": "Default product when no items found in invoice"
            }]
        
        for item in items:
            if not isinstance(item, dict):
                continue
                
            # Ensure required fields
            name = item.get('name', 'Product')
            if not name:
                name = "Unnamed Product"
                
            try:
                selling_price = float(item.get('selling_price', 0))
            except (ValueError, TypeError):
                selling_price = 0
                
            try:
                units = int(item.get('units', 1))
                if units <= 0:
                    units = 1
            except (ValueError, TypeError):
                units = 1
            
            # Create formatted item
            formatted_item = {
                "name": name,
                "selling_price": str(selling_price),
                "units": units,
                "sku": item.get('sku', name.replace(' ', '_')[:15]),
                "hsn": item.get('hsn', ''),
                "weight": item.get('weight', 0.5),
                "category_name": None,
                "tax": item.get('tax_rate', None),
                "discount": None,
                "product_description": None
            }
            
            formatted_items.append(formatted_item)
        
        return formatted_items
    
    def calculate_total_weight(self, items: list) -> float:
        """Calculate total weight of all items"""
        total_weight = 0
        
        for item in items:
            if not isinstance(item, dict):
                continue
                
            try:
                weight = float(item.get('weight', 0.5))
                units = int(item.get('units', 1))
                total_weight += weight * units
            except (ValueError, TypeError):
                # Default weight for invalid items
                total_weight += 0.5
        
        # Ensure minimum weight
        return max(total_weight, 0.5)
    
    def get_order_status(self, order_id: str) -> Dict[str, Any]:
        """Get status of an order"""
        self.logger.info(f"Getting status for order: {order_id}")
        
        # Ensure we have an auth token
        if not self.auth_token:
            if not self.authenticate():
                raise Exception("Failed to authenticate with Shiprocket")
        
        url = f"{self.base_url}/orders/show/{order_id}"
        headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                result = response.json()
                self.logger.info(f"Order status retrieved successfully")
                return result
            else:
                # Check if token expired
                if response.status_code == 401:
                    self.logger.warning("Authentication token expired, re-authenticating")
                    if self.authenticate():
                        # Retry with new token
                        headers["Authorization"] = f"Bearer {self.auth_token}"
                        response = requests.get(url, headers=headers)
                        
                        if response.status_code == 200:
                            result = response.json()
                            self.logger.info(f"Order status retrieved successfully after re-auth")
                            return result
                
                error_msg = f"Failed to get order status: {response.status_code} - {response.text}"
                self.logger.error(error_msg)
                return {"error": error_msg, "status": "failed"}
                
        except Exception as e:
            error_msg = f"Error getting order status: {str(e)}"
            self.logger.error(error_msg)
            return {"error": error_msg, "status": "failed"} 