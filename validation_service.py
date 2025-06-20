import re
import logging
from typing import Dict, Any, Tuple, List
from datetime import datetime

class InvoiceValidator:
    """Validate invoice data extracted from OCR and LLM processing"""
    
    def __init__(self):
        # Configure logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Load Indian states
        self.indian_states = [
            'Andhra Pradesh', 'Arunachal Pradesh', 'Assam', 'Bihar', 'Chhattisgarh',
            'Goa', 'Gujarat', 'Haryana', 'Himachal Pradesh', 'Jharkhand', 'Karnataka',
            'Kerala', 'Madhya Pradesh', 'Maharashtra', 'Manipur', 'Meghalaya', 
            'Mizoram', 'Nagaland', 'Odisha', 'Punjab', 'Rajasthan', 'Sikkim',
            'Tamil Nadu', 'Telangana', 'Tripura', 'Uttar Pradesh', 'Uttarakhand', 
            'West Bengal', 'Delhi', 'Jammu and Kashmir', 'Ladakh', 'Puducherry',
            'Chandigarh', 'Daman and Diu', 'Dadra and Nagar Haveli', 'Lakshadweep',
            'Andaman and Nicobar Islands'
        ]
        # Add state codes
        self.state_codes = {
            'AP': 'Andhra Pradesh', 'AR': 'Arunachal Pradesh', 'AS': 'Assam',
            'BR': 'Bihar', 'CT': 'Chhattisgarh', 'GA': 'Goa', 'GJ': 'Gujarat',
            'HR': 'Haryana', 'HP': 'Himachal Pradesh', 'JH': 'Jharkhand',
            'KA': 'Karnataka', 'KL': 'Kerala', 'MP': 'Madhya Pradesh',
            'MH': 'Maharashtra', 'MN': 'Manipur', 'ML': 'Meghalaya',
            'MZ': 'Mizoram', 'NL': 'Nagaland', 'OR': 'Odisha', 'PB': 'Punjab',
            'RJ': 'Rajasthan', 'SK': 'Sikkim', 'TN': 'Tamil Nadu', 'TG': 'Telangana',
            'TR': 'Tripura', 'UP': 'Uttar Pradesh', 'UK': 'Uttarakhand',
            'WB': 'West Bengal', 'DL': 'Delhi', 'JK': 'Jammu and Kashmir',
            'LA': 'Ladakh', 'PY': 'Puducherry', 'CH': 'Chandigarh',
            'DD': 'Daman and Diu', 'DN': 'Dadra and Nagar Haveli',
            'LD': 'Lakshadweep', 'AN': 'Andaman and Nicobar Islands'
        }
    
    def validate_gstin(self, gstin: str) -> bool:
        """Validate GSTIN format and checksum"""
        if not gstin:
            return False
            
        # GSTIN format: 22AAAAA0000A1Z5
        pattern = r'^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}[Z]{1}[0-9A-Z]{1}$'
        
        # Basic pattern check
        if not re.match(pattern, gstin):
            return False
            
        # State code check (first two digits)
        state_code = int(gstin[:2])
        if state_code < 1 or state_code > 38:  # Current state codes in India
            return False
            
        # Check the checksum character (last character)
        # For a complete implementation, a proper checksum calculation would be needed
        # This is a simplified version
        
        return True
    
    def validate_pincode(self, pincode: str) -> bool:
        """Validate Indian PIN code"""
        if not pincode:
            return False
            
        # Handle string and numeric pincodes
        pincode_str = str(pincode).strip()
        
        # Indian PIN codes are 6 digits
        if not re.match(r'^[1-9][0-9]{5}$', pincode_str):
            return False
            
        return True
    
    def validate_phone(self, phone: str) -> bool:
        """Validate Indian phone number"""
        if not phone:
            return False
            
        # Remove spaces, dashes, and parentheses
        phone_clean = re.sub(r'[\s\-()]', '', str(phone))
        
        # Handle country code if present
        if phone_clean.startswith('+91'):
            phone_clean = phone_clean[3:]
        elif phone_clean.startswith('91') and len(phone_clean) > 10:
            phone_clean = phone_clean[2:]
            
        # Indian phone numbers are 10 digits
        if not re.match(r'^[6-9][0-9]{9}$', phone_clean):
            return False
            
        return True
    
    def validate_email(self, email: str) -> bool:
        """Validate email format"""
        if not email:
            return False
            
        # Basic email validation
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    def validate_date(self, date_str: str) -> Tuple[bool, str]:
        """Validate and standardize date format to YYYY-MM-DD"""
        if not date_str:
            return False, ""
            
        # Common date formats
        formats = [
            r'(\d{1,2})[/.-](\d{1,2})[/.-](\d{2,4})',  # DD/MM/YYYY or MM/DD/YYYY
            r'(\d{2,4})[/.-](\d{1,2})[/.-](\d{1,2})',  # YYYY/MM/DD
        ]
        
        for fmt in formats:
            match = re.match(fmt, date_str)
            if match:
                parts = [match.group(1), match.group(2), match.group(3)]
                
                # Handle 2-digit year
                if len(parts[2]) == 2:
                    parts[2] = '20' + parts[2] if int(parts[2]) < 50 else '19' + parts[2]
                    
                # Determine date format (assume DD/MM/YYYY if first number <= 31)
                if len(parts[0]) == 4:  # YYYY/MM/DD
                    year, month, day = parts
                elif int(parts[0]) <= 31 and int(parts[1]) <= 12:  # DD/MM/YYYY
                    day, month, year = parts
                else:  # Assume MM/DD/YYYY
                    month, day, year = parts
                    
                # Validate date components
                try:
                    day_val = int(day)
                    month_val = int(month)
                    year_val = int(year)
                    
                    if not (1 <= month_val <= 12 and 1 <= day_val <= 31):
                        continue
                        
                    if month_val in [4, 6, 9, 11] and day_val > 30:
                        continue
                        
                    if month_val == 2:
                        leap_year = (year_val % 4 == 0 and year_val % 100 != 0) or (year_val % 400 == 0)
                        if (leap_year and day_val > 29) or (not leap_year and day_val > 28):
                            continue
                            
                    # Format as YYYY-MM-DD
                    standardized = f"{year_val:04d}-{month_val:02d}-{day_val:02d}"
                    return True, standardized
                    
                except ValueError:
                    continue
                    
        # Try direct datetime parsing as a fallback
        try:
            for fmt in ['%d/%m/%Y', '%m/%d/%Y', '%Y/%m/%d', '%d-%m-%Y', '%m-%d-%Y', '%Y-%m-%d']:
                try:
                    dt = datetime.strptime(date_str, fmt)
                    return True, dt.strftime('%Y-%m-%d')
                except ValueError:
                    continue
        except:
            pass
            
        return False, ""
    
    def validate_state(self, state: str) -> Tuple[bool, str]:
        """Validate and standardize Indian state name"""
        if not state:
            return False, ""
            
        # Clean input
        state_clean = state.strip().upper()
        
        # Check if it's a state code
        if state_clean in self.state_codes:
            return True, self.state_codes[state_clean]
            
        # Check if it's a state name
        for valid_state in self.indian_states:
            if state_clean == valid_state.upper():
                return True, valid_state
                
        # Check partial matches
        for valid_state in self.indian_states:
            if valid_state.upper() in state_clean or state_clean in valid_state.upper():
                return True, valid_state
                
        return False, ""
    
    def validate_invoice_data(self, data: Dict[str, Any]) -> Tuple[List[str], List[str]]:
        """Comprehensive validation of extracted invoice data"""
        errors = []
        warnings = []
        
        # Required field validation
        required_fields = ['billing_customer_name', 'billing_address']
        for field in required_fields:
            if not data.get(field):
                errors.append(f"Missing required field: {field}")
        
        # GSTIN validation
        if data.get('billing_gstin') and not self.validate_gstin(data['billing_gstin']):
            warnings.append("Invalid GSTIN format")
        
        # Pincode validation
        if data.get('billing_pincode') and not self.validate_pincode(data['billing_pincode']):
            warnings.append("Invalid billing pincode format")
            
        if data.get('shipping_pincode') and not self.validate_pincode(data['shipping_pincode']):
            warnings.append("Invalid shipping pincode format")
        
        # Phone validation
        if data.get('billing_phone') and not self.validate_phone(data['billing_phone']):
            warnings.append("Invalid billing phone number format")
            
        if data.get('shipping_phone') and not self.validate_phone(data['shipping_phone']):
            warnings.append("Invalid shipping phone number format")
        
        # Email validation
        if data.get('billing_email') and not self.validate_email(data['billing_email']):
            warnings.append("Invalid billing email format")
            
        if data.get('shipping_email') and not self.validate_email(data['shipping_email']):
            warnings.append("Invalid shipping email format")
            
        # Date validation
        if data.get('order_date'):
            is_valid, standardized = self.validate_date(data['order_date'])
            if not is_valid:
                warnings.append("Invalid order date format")
            else:
                data['order_date'] = standardized
                
        # State validation
        if data.get('billing_state'):
            is_valid, standardized = self.validate_state(data['billing_state'])
            if not is_valid:
                warnings.append("Invalid billing state")
            else:
                data['billing_state'] = standardized
                
        if data.get('shipping_state'):
            is_valid, standardized = self.validate_state(data['shipping_state'])
            if not is_valid:
                warnings.append("Invalid shipping state")
            else:
                data['shipping_state'] = standardized
                
        # Amount validation
        if data.get('sub_total') is not None:
            try:
                data['sub_total'] = float(data['sub_total'])
                if data['sub_total'] < 0:
                    warnings.append("Negative subtotal amount")
            except (ValueError, TypeError):
                warnings.append("Invalid subtotal amount format")
                
        if data.get('tax_amount') is not None:
            try:
                data['tax_amount'] = float(data['tax_amount'])
                if data['tax_amount'] < 0:
                    warnings.append("Negative tax amount")
            except (ValueError, TypeError):
                warnings.append("Invalid tax amount format")
                
        if data.get('total_amount') is not None:
            try:
                data['total_amount'] = float(data['total_amount'])
                if data['total_amount'] < 0:
                    warnings.append("Negative total amount")
            except (ValueError, TypeError):
                warnings.append("Invalid total amount format")
                
        # Validate order items
        if data.get('order_items'):
            if not isinstance(data['order_items'], list):
                warnings.append("Order items should be a list")
                data['order_items'] = []
            else:
                for i, item in enumerate(data['order_items']):
                    if not isinstance(item, dict):
                        warnings.append(f"Order item {i+1} should be an object")
                        continue
                        
                    if not item.get('name'):
                        warnings.append(f"Order item {i+1} missing name")
                        
                    if item.get('units') is not None:
                        try:
                            item['units'] = int(item['units'])
                            if item['units'] <= 0:
                                warnings.append(f"Order item {i+1} has invalid quantity")
                        except (ValueError, TypeError):
                            warnings.append(f"Order item {i+1} has invalid quantity format")
                            
                    if item.get('selling_price') is not None:
                        try:
                            item['selling_price'] = float(item['selling_price'])
                            if item['selling_price'] < 0:
                                warnings.append(f"Order item {i+1} has negative price")
                        except (ValueError, TypeError):
                            warnings.append(f"Order item {i+1} has invalid price format")
        
        return errors, warnings 