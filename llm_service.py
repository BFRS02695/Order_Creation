import requests
import json
import logging
from typing import Dict, Any, Optional
import re
from pydantic import BaseModel

class InvoiceFields(BaseModel):
    """Data model for invoice fields"""
    # Billing Information
    billing_customer_name: Optional[str] = None
    billing_address: Optional[str] = None
    billing_city: Optional[str] = None
    billing_state: Optional[str] = None
    billing_pincode: Optional[str] = None
    billing_phone: Optional[str] = None
    billing_email: Optional[str] = None
    billing_gstin: Optional[str] = None
    
    # Shipping Information
    shipping_customer_name: Optional[str] = None
    shipping_address: Optional[str] = None
    shipping_city: Optional[str] = None
    shipping_state: Optional[str] = None
    shipping_pincode: Optional[str] = None
    shipping_phone: Optional[str] = None
    shipping_email: Optional[str] = None
    
    # Order Information
    order_date: Optional[str] = None
    invoice_number: Optional[str] = None
    order_items: list = []
    sub_total: Optional[float] = None
    tax_amount: Optional[float] = None
    total_amount: Optional[float] = None
    payment_method: Optional[str] = None

class LLMInvoiceProcessor:
    """Process invoice text using local LLM via Ollama"""
    
    def __init__(self, model="llama3:8b", ollama_url="http://localhost:11434"):
        self.model = model
        self.ollama_url = ollama_url
        
        # Configure logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Test connection to Ollama
        self.test_connection()
    
    def test_connection(self):
        """Test connection to Ollama server"""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags")
            if response.status_code == 200:
                models = response.json().get('models', [])
                model_names = [model.get('name') for model in models]
                self.logger.info(f"Connected to Ollama. Available models: {model_names}")
                
                # Check if our model is available
                if self.model.split(':')[0] not in [m.split(':')[0] for m in model_names]:
                    self.logger.warning(f"Model {self.model} not found in available models. You may need to pull it.")
            else:
                self.logger.warning(f"Ollama returned status code {response.status_code}")
        except Exception as e:
            self.logger.error(f"Failed to connect to Ollama at {self.ollama_url}: {str(e)}")
            self.logger.info("Make sure Ollama is running and accessible.")
    
    def query_ollama(self, prompt, system_prompt=None):
        """Send a query to Ollama LLM API"""
        try:
            url = f"{self.ollama_url}/api/generate"
            
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False
            }
            
            if system_prompt:
                payload["system"] = system_prompt
                
            response = requests.post(url, json=payload)
            
            if response.status_code == 200:
                return response.json().get('response', '')
            else:
                self.logger.error(f"Ollama API error: {response.status_code} - {response.text}")
                return ""
                
        except Exception as e:
            self.logger.error(f"Error querying Ollama: {str(e)}")
            return ""
    
    def extract_invoice_fields(self, ocr_text: str) -> Dict[str, Any]:
        """Extract invoice fields from OCR text using local LLM"""
        self.logger.info("Extracting invoice fields using local LLM")
        
        system_prompt = """
        You are an expert invoice data extraction AI. Your task is to extract structured information from the text of an invoice.
        
        Follow these guidelines strictly:
        1. Extract all possible fields: billing details, shipping details, items, amounts
        2. Format numbers as numeric values without currency symbols
        3. Format dates in YYYY-MM-DD format
        4. For GSTIN (India GST Number), ensure it's exactly 15 characters
        5. Return ONLY a valid JSON object with the extracted data
        6. Do not include any explanations, just the JSON
        7. Use null for missing fields, don't make up data
        8. For fields not found in the text, leave them as null
        9. Format Indian PIN codes as 6 digits
        """
        
        prompt = f"""
        Extract the following information from this invoice text into a JSON object:

        Invoice Text:
        {ocr_text}
        
        Return only a valid JSON object with this exact structure:
        {{
            "billing_customer_name": null,
            "billing_address": null,
            "billing_city": null, 
            "billing_state": null,
            "billing_pincode": null,
            "billing_phone": null,
            "billing_email": null,
            "billing_gstin": null,
            "shipping_customer_name": null,
            "shipping_address": null,
            "shipping_city": null,
            "shipping_state": null,
            "shipping_pincode": null,
            "shipping_phone": null,
            "shipping_email": null,
            "order_date": null,
            "invoice_number": null,
            "order_items": [
                {{
                    "name": null,
                    "units": null,
                    "selling_price": null,
                    "hsn": null,
                    "tax_rate": null,
                    "weight": 1
                }}
            ],
            "sub_total": null,
            "tax_amount": null,
            "total_amount": null,
            "payment_method": null
        }}
        
        Only return the JSON object, nothing else.
        """
        
        # Query LLM
        self.logger.info("Sending invoice text to LLM for extraction")
        response = self.query_ollama(prompt, system_prompt)
        
        # Extract JSON from response
        try:
            # Try to find JSON in the response
            json_match = re.search(r'({[\s\S]*})', response)
            
            if json_match:
                json_str = json_match.group(1)
                # Parse the JSON
                result = json.loads(json_str)
                return result
            else:
                self.logger.error("No valid JSON found in LLM response")
                # If no JSON found, try alternate approach
                return self.extract_fields_fallback(ocr_text)
                
        except json.JSONDecodeError as e:
            self.logger.error(f"JSON parsing error: {str(e)}")
            # Fallback to simpler extraction
            return self.extract_fields_fallback(ocr_text)
        except Exception as e:
            self.logger.error(f"Error extracting fields: {str(e)}")
            return self.create_empty_result()
    
    def extract_fields_fallback(self, ocr_text: str) -> Dict[str, Any]:
        """Fallback method using regex and heuristics to extract invoice fields"""
        self.logger.info("Using fallback extraction method")
        
        result = self.create_empty_result()
        
        # Extract invoice number (common formats)
        inv_match = re.search(r'(?:invoice|inv|bill)(?:\s+no[.:])?\s*[#:]?\s*([A-Z0-9-/]+)', 
                            ocr_text, re.IGNORECASE)
        if inv_match:
            result['invoice_number'] = inv_match.group(1).strip()
        
        # Extract date (various formats)
        date_match = re.search(r'(?:date|dt)[.:]\s*(\d{1,2}[-/]\d{1,2}[-/]\d{2,4}|\d{2,4}[-/]\d{1,2}[-/]\d{1,2})', 
                             ocr_text, re.IGNORECASE)
        if date_match:
            date_str = date_match.group(1)
            # Convert to YYYY-MM-DD (simplified)
            # A more robust date parser would be needed for production
            result['order_date'] = date_str
        
        # Extract GSTIN
        gstin_match = re.search(r'(?:GSTIN|GST IN|GST Number)[.:]\s*([0-9A-Z]{15})', 
                              ocr_text, re.IGNORECASE)
        if gstin_match:
            result['billing_gstin'] = gstin_match.group(1).upper()
        
        # Extract total amount
        total_match = re.search(r'(?:total|amount|grand total)[.:]\s*(?:Rs\.?|₹|INR)?\s*(\d+(?:,\d+)*(?:\.\d+)?)', 
                              ocr_text, re.IGNORECASE)
        if total_match:
            # Remove commas and convert to float
            amount_str = total_match.group(1).replace(',', '')
            try:
                result['total_amount'] = float(amount_str)
            except:
                pass
        
        # Extract phone number
        phone_match = re.search(r'(?:phone|mobile|contact|tel)[.:]\s*(\+?\d{1,3}[-.\s]?)?\(?(\d{3})\)?[-.\s]?(\d{3})[-.\s]?(\d{4})', 
                              ocr_text, re.IGNORECASE)
        if phone_match:
            result['billing_phone'] = ''.join(g for g in phone_match.groups() if g)
        
        # Basic extraction of customer name
        name_match = re.search(r'(?:bill to|customer|client|buyer)[.:]\s*([A-Za-z\s]+)', 
                             ocr_text, re.IGNORECASE)
        if name_match:
            result['billing_customer_name'] = name_match.group(1).strip()
        
        return result
    
    def create_empty_result(self) -> Dict[str, Any]:
        """Create an empty result dictionary with the expected structure"""
        return {
            "billing_customer_name": None,
            "billing_address": None,
            "billing_city": None, 
            "billing_state": None,
            "billing_pincode": None,
            "billing_phone": None,
            "billing_email": None,
            "billing_gstin": None,
            "shipping_customer_name": None,
            "shipping_address": None,
            "shipping_city": None,
            "shipping_state": None,
            "shipping_pincode": None,
            "shipping_phone": None,
            "shipping_email": None,
            "order_date": None,
            "invoice_number": None,
            "order_items": [],
            "sub_total": None,
            "tax_amount": None,
            "total_amount": None,
            "payment_method": None
        }
    
    def refine_extraction(self, extracted_data: Dict[str, Any], ocr_text: str) -> Dict[str, Any]:
        """Refine extracted data with additional processing"""
        self.logger.info("Refining extracted data")
        
        # Copy the original data
        refined = extracted_data.copy()
        
        # Ensure proper types for numeric fields
        for field in ['sub_total', 'tax_amount', 'total_amount']:
            if refined.get(field) and not isinstance(refined[field], (int, float)):
                try:
                    # Remove currency symbols and commas
                    value = str(refined[field])
                    value = re.sub(r'[₹$,]', '', value)
                    refined[field] = float(value)
                except:
                    refined[field] = None
        
        # Ensure order_items is a list
        if not isinstance(refined.get('order_items'), list):
            refined['order_items'] = []
        
        # If shipping address is missing but billing is present, use billing
        if not refined.get('shipping_address') and refined.get('billing_address'):
            refined['shipping_address'] = refined['billing_address']
            
        if not refined.get('shipping_customer_name') and refined.get('billing_customer_name'):
            refined['shipping_customer_name'] = refined['billing_customer_name']
            
        if not refined.get('shipping_city') and refined.get('billing_city'):
            refined['shipping_city'] = refined['billing_city']
            
        if not refined.get('shipping_state') and refined.get('billing_state'):
            refined['shipping_state'] = refined['billing_state']
            
        if not refined.get('shipping_pincode') and refined.get('billing_pincode'):
            refined['shipping_pincode'] = refined['billing_pincode']
            
        if not refined.get('shipping_phone') and refined.get('billing_phone'):
            refined['shipping_phone'] = refined['billing_phone']
            
        if not refined.get('shipping_email') and refined.get('billing_email'):
            refined['shipping_email'] = refined['billing_email']
        
        # Try to infer payment method
        if not refined.get('payment_method'):
            if re.search(r'paid|prepaid|credit card|debit card|upi|online', ocr_text, re.IGNORECASE):
                refined['payment_method'] = 'prepaid'
            elif re.search(r'cod|cash on delivery|collect', ocr_text, re.IGNORECASE):
                refined['payment_method'] = 'cod'
        
        return refined 