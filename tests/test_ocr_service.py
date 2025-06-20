import os
import sys
import unittest
from pathlib import Path
import logging

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ocr_service import MultiOCRService

# Disable logging during tests
logging.disable(logging.CRITICAL)

class TestOCRService(unittest.TestCase):
    """Test cases for the MultiOCRService class"""
    
    def setUp(self):
        """Set up test environment"""
        self.ocr_service = MultiOCRService()
        
        # Create test directory if it doesn't exist
        self.test_dir = Path(__file__).parent / 'test_data'
        self.test_dir.mkdir(exist_ok=True)
        
        # Create a simple test image with text
        self.test_image_path = self.test_dir / 'test_image.jpg'
        self.create_test_image()
    
    def create_test_image(self):
        """Create a simple test image with text"""
        try:
            import cv2
            import numpy as np
            
            # Create a white image
            img = np.ones((300, 800), dtype=np.uint8) * 255
            
            # Add text to the image
            text = "INVOICE #12345"
            cv2.putText(img, text, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
            
            text = "Customer: John Doe"
            cv2.putText(img, text, (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
            
            text = "Amount: $500.00"
            cv2.putText(img, text, (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
            
            text = "Date: 2023-01-15"
            cv2.putText(img, text, (50, 200), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
            
            # Save the image
            cv2.imwrite(str(self.test_image_path), img)
        except ImportError:
            # If OpenCV is not available, create a blank image
            from PIL import Image, ImageDraw, ImageFont
            
            # Create a white image
            img = Image.new('RGB', (800, 300), color='white')
            draw = ImageDraw.Draw(img)
            
            # Add text
            draw.text((50, 50), "INVOICE #12345", fill='black')
            draw.text((50, 100), "Customer: John Doe", fill='black')
            draw.text((50, 150), "Amount: $500.00", fill='black')
            draw.text((50, 200), "Date: 2023-01-15", fill='black')
            
            # Save the image
            img.save(str(self.test_image_path))
    
    def tearDown(self):
        """Clean up after tests"""
        # Remove test image
        if self.test_image_path.exists():
            self.test_image_path.unlink()
    
    def test_preprocess_image(self):
        """Test image preprocessing"""
        try:
            preprocessed_path, enhanced, denoised = self.ocr_service.preprocess_image(str(self.test_image_path))
            
            # Check if preprocessed image was created
            self.assertTrue(Path(preprocessed_path).exists())
            
            # Check if enhanced and denoised images are not None
            self.assertIsNotNone(enhanced)
            self.assertIsNotNone(denoised)
            
            # Cleanup
            if Path(preprocessed_path).exists():
                Path(preprocessed_path).unlink()
        except Exception as e:
            self.fail(f"Preprocessing failed with error: {str(e)}")
    
    def test_extract_text_multi_ocr(self):
        """Test text extraction using multiple OCR engines"""
        try:
            text = self.ocr_service.extract_text_multi_ocr(str(self.test_image_path))
            
            # Check if text was extracted
            self.assertIsNotNone(text)
            self.assertIsInstance(text, str)
            
            # Text should contain at least some of the expected keywords
            expected_keywords = ['INVOICE', '12345', 'John', 'Doe', '500', 'Date']
            found_keywords = sum(1 for keyword in expected_keywords if keyword.lower() in text.lower())
            
            # At least 3 keywords should be found for the test to pass
            # This is a lenient test since OCR accuracy can vary
            self.assertGreaterEqual(found_keywords, 3, 
                f"Expected to find at least 3 keywords from {expected_keywords}, but found {found_keywords} in: {text}")
            
        except Exception as e:
            self.fail(f"Text extraction failed with error: {str(e)}")
    
    def test_clean_ocr_text(self):
        """Test OCR text cleaning"""
        # Test text with common OCR errors
        test_text = """
        lNVOICE #12345
        GSTlN: 22AAAAA0000A1Z5
        Customer: John Doe
        Amount: $500.00
        """
        
        cleaned_text = self.ocr_service.clean_ocr_text(test_text)
        
        # Check if common errors were corrected
        self.assertIn("INVOICE", cleaned_text)
        self.assertIn("GSTIN", cleaned_text)

if __name__ == '__main__':
    unittest.main() 