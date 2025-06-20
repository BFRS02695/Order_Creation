import cv2
import numpy as np
import os
from pathlib import Path

def create_sample_invoice(output_path: str = None):
    """
    Create a sample invoice image for testing
    
    Args:
        output_path: Path to save the invoice image
        
    Returns:
        Path to the created invoice image
    """
    # Default output path if not provided
    if output_path is None:
        samples_dir = Path(__file__).parent.parent.parent / 'samples'
        samples_dir.mkdir(exist_ok=True)
        output_path = samples_dir / 'sample_invoice.jpg'
    
    # Create a white image
    img = np.ones((1200, 900), dtype=np.uint8) * 255
    
    # Add invoice header
    cv2.putText(img, "INVOICE", (350, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 0), 2)
    cv2.putText(img, "Invoice #: INV-2023-001", (300, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 1)
    cv2.putText(img, "Date: 2023-06-15", (300, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 1)
    
    # Add horizontal line
    cv2.line(img, (50, 150), (850, 150), (0, 0, 0), 2)
    
    # Add billing information
    cv2.putText(img, "Bill To:", (50, 200), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 1)
    cv2.putText(img, "ABC Company Pvt Ltd", (50, 230), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 1)
    cv2.putText(img, "123 Main Street, Suite 101", (50, 260), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 1)
    cv2.putText(img, "Mumbai, Maharashtra 400001", (50, 290), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 1)
    cv2.putText(img, "Phone: +91 9876543210", (50, 320), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 1)
    cv2.putText(img, "Email: accounts@abccompany.com", (50, 350), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 1)
    cv2.putText(img, "GSTIN: 27AABCU9603R1ZX", (50, 380), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 1)
    
    # Add shipping information
    cv2.putText(img, "Ship To:", (450, 200), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 1)
    cv2.putText(img, "XYZ Enterprises", (450, 230), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 1)
    cv2.putText(img, "456 Commerce Road", (450, 260), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 1)
    cv2.putText(img, "Delhi, Delhi 110001", (450, 290), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 1)
    cv2.putText(img, "Phone: +91 8765432109", (450, 320), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 1)
    cv2.putText(img, "Email: orders@xyzenterprises.com", (450, 350), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 1)
    
    # Add items table header
    cv2.putText(img, "Item", (50, 430), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 1)
    cv2.putText(img, "Quantity", (350, 430), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 1)
    cv2.putText(img, "Unit Price", (450, 430), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 1)
    cv2.putText(img, "HSN Code", (550, 430), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 1)
    cv2.putText(img, "Tax Rate", (650, 430), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 1)
    cv2.putText(img, "Amount", (750, 430), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 1)
    
    # Add horizontal line
    cv2.line(img, (50, 450), (850, 450), (0, 0, 0), 1)
    
    # Add items
    cv2.putText(img, "Product A - Premium Widget", (50, 480), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 1)
    cv2.putText(img, "2", (350, 480), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 1)
    cv2.putText(img, "₹1000.00", (450, 480), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 1)
    cv2.putText(img, "8471", (550, 480), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 1)
    cv2.putText(img, "18%", (650, 480), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 1)
    cv2.putText(img, "₹2000.00", (750, 480), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 1)
    
    cv2.putText(img, "Product B - Standard Component", (50, 510), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 1)
    cv2.putText(img, "5", (350, 510), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 1)
    cv2.putText(img, "₹500.00", (450, 510), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 1)
    cv2.putText(img, "8473", (550, 510), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 1)
    cv2.putText(img, "12%", (650, 510), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 1)
    cv2.putText(img, "₹2500.00", (750, 510), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 1)
    
    # Add horizontal line
    cv2.line(img, (50, 550), (850, 550), (0, 0, 0), 1)
    
    # Add totals
    cv2.putText(img, "Subtotal:", (550, 580), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 1)
    cv2.putText(img, "₹4500.00", (750, 580), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 1)
    
    cv2.putText(img, "IGST (18%):", (550, 610), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 1)
    cv2.putText(img, "₹810.00", (750, 610), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 1)
    
    cv2.putText(img, "Total:", (550, 640), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)
    cv2.putText(img, "₹5310.00", (750, 640), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)
    
    # Add payment information
    cv2.putText(img, "Payment Information:", (50, 700), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 1)
    cv2.putText(img, "Payment Method: Prepaid", (50, 730), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 1)
    cv2.putText(img, "Bank: HDFC Bank", (50, 760), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 1)
    cv2.putText(img, "Account: 1234567890", (50, 790), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 1)
    
    # Add terms
    cv2.putText(img, "Terms & Conditions:", (50, 850), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 1)
    cv2.putText(img, "1. Payment due within 30 days", (50, 880), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 1)
    cv2.putText(img, "2. Goods once sold cannot be returned", (50, 910), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 1)
    
    # Add footer
    cv2.putText(img, "Thank you for your business!", (300, 980), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 1)
    
    # Save the image
    cv2.imwrite(str(output_path), img)
    
    print(f"Sample invoice created at: {output_path}")
    return output_path

if __name__ == "__main__":
    create_sample_invoice() 