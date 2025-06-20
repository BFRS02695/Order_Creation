"""
OCR Service module for the Invoice to Order Processing System.
Combines multiple OCR engines for maximum text extraction accuracy.
"""
import cv2
import numpy as np
import pytesseract
import logging
from PIL import Image
import os
from pathlib import Path
import io
import re

# Set up logging
logger = logging.getLogger(__name__)

class MultiOCRService:
    """
    Multi-engine OCR service that combines PaddleOCR, EasyOCR, and Tesseract
    with advanced image preprocessing for maximum accuracy.
    """
    
    def __init__(self):
        """Initialize the OCR service with multiple engines."""
        logger.info("Initializing MultiOCRService")
        
        # Initialize OCR engines
        self.paddle_ocr = self._init_paddle_ocr()
        self.easy_reader = self._init_easy_ocr()
        self.logger = logger
        
    def _init_paddle_ocr(self):
        """Initialize PaddleOCR engine."""
        try:
            from paddleocr import PaddleOCR
            return PaddleOCR(use_angle_cls=True, lang='en')
        except ImportError:
            logger.warning("PaddleOCR not available. Continuing without it.")
            return None
        except Exception as e:
            logger.error(f"Error initializing PaddleOCR: {e}")
            return None
    
    def _init_easy_ocr(self):
        """Initialize EasyOCR engine."""
        try:
            import easyocr
            return easyocr.Reader(['en'])
        except ImportError:
            logger.warning("EasyOCR not available. Continuing without it.")
            return None
        except Exception as e:
            logger.error(f"Error initializing EasyOCR: {e}")
            return None
    
    def preprocess_image(self, image_path):
        """
        Advanced image preprocessing for better OCR accuracy.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Preprocessed image as numpy array
        """
        try:
            # Read the image
            img = cv2.imread(str(image_path))
            if img is None:
                raise ValueError(f"Could not read image at {image_path}")
            
            # Convert to grayscale
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Noise removal
            denoised = cv2.fastNlMeansDenoising(gray, h=10)
            
            # Contrast enhancement
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
            enhanced = clahe.apply(denoised)
            
            # Deskewing (if needed)
            coords = np.column_stack(np.where(enhanced > 0))
            if len(coords) > 0:  # Ensure we have non-zero pixels
                angle = cv2.minAreaRect(coords)[-1]
                if angle < -45:
                    angle = -(90 + angle)
                else:
                    angle = -angle
                    
                if abs(angle) > 0.5:  # Only deskew if angle is significant
                    (h, w) = enhanced.shape[:2]
                    center = (w // 2, h // 2)
                    M = cv2.getRotationMatrix2D(center, angle, 1.0)
                    enhanced = cv2.warpAffine(enhanced, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
            
            # Adaptive thresholding
            binary = cv2.adaptiveThreshold(enhanced, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
            
            return binary
        except Exception as e:
            logger.error(f"Error preprocessing image: {e}")
            # Return the original image if preprocessing fails
            return cv2.imread(str(image_path))
    
    def parse_paddle_result(self, result):
        """
        Parse PaddleOCR result into plain text.
        
        Args:
            result: PaddleOCR result object
            
        Returns:
            Extracted text as string
        """
        text = ""
        for line in result:
            for word_info in line:
                if len(word_info) >= 2:
                    text += word_info[1][0] + " "
            text += "\n"
        return text
    
    def parse_easy_result(self, result):
        """
        Parse EasyOCR result into plain text.
        
        Args:
            result: EasyOCR result object
            
        Returns:
            Extracted text as string
        """
        text = ""
        current_line_y = -1
        line_text = ""
        
        # Sort by y-coordinate first, then by x-coordinate
        sorted_result = sorted(result, key=lambda x: (x[0][0][1] + x[0][2][1]) / 2)
        
        for detection in sorted_result:
            box, text_detected, confidence = detection
            
            # Calculate center y-coordinate of the current text box
            curr_y = (box[0][1] + box[2][1]) / 2
            
            # If y-coordinate is significantly different, start a new line
            if current_line_y != -1 and abs(curr_y - current_line_y) > 20:
                text += line_text + "\n"
                line_text = text_detected + " "
            else:
                line_text += text_detected + " "
            
            current_line_y = curr_y
        
        # Add the last line
        if line_text:
            text += line_text
        
        return text
    
    def consolidate_ocr_results(self, results):
        """
        Combine results from multiple OCR engines intelligently.
        
        Args:
            results: Dictionary of OCR results from different engines
            
        Returns:
            Consolidated text as string
        """
        # If only one engine worked, return its result
        non_empty_results = {k: v for k, v in results.items() if v.strip()}
        if len(non_empty_results) == 0:
            return ""
        elif len(non_empty_results) == 1:
            return list(non_empty_results.values())[0]
        
        # Split all results into lines for comparison
        lines_by_engine = {
            engine: text.split('\n') 
            for engine, text in non_empty_results.items()
        }
        
        # Consolidate line by line
        max_lines = max(len(lines) for lines in lines_by_engine.values())
        consolidated = []
        
        for i in range(max_lines):
            line_candidates = []
            for engine, lines in lines_by_engine.items():
                if i < len(lines):
                    line = lines[i].strip()
                    if line:
                        line_candidates.append((engine, line))
            
            if not line_candidates:
                continue
                
            # Choose the best line based on heuristics
            if len(line_candidates) == 1:
                consolidated.append(line_candidates[0][1])
            else:
                # Simple heuristic: prefer the longer line, which likely has more information
                # Could be improved with more sophisticated voting or confidence-based selection
                best_line = max(line_candidates, key=lambda x: len(x[1]))[1]
                consolidated.append(best_line)
        
        return '\n'.join(consolidated)
    
    def extract_text_multi_ocr(self, image_path):
        """
        Extract text from an image using multiple OCR engines.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Extracted text as string
        """
        logger.info(f"Extracting text from image: {image_path}")
        
        # Preprocess image for better OCR accuracy
        preprocessed_img = self.preprocess_image(image_path)
        
        # Use a temporary file for the preprocessed image
        preprocessed_path = str(Path(image_path).with_suffix('.preproc.jpg'))
        cv2.imwrite(preprocessed_path, preprocessed_img)
        
        results = {}
        
        # PaddleOCR
        if self.paddle_ocr:
            try:
                logger.info("Running PaddleOCR")
                paddle_result = self.paddle_ocr.ocr(preprocessed_path, cls=True)
                results['paddle'] = self.parse_paddle_result(paddle_result)
                logger.info(f"PaddleOCR extracted {len(results['paddle'])} characters")
            except Exception as e:
                logger.error(f"PaddleOCR failed: {e}")
                results['paddle'] = ""
        else:
            results['paddle'] = ""
        
        # EasyOCR
        if self.easy_reader:
            try:
                logger.info("Running EasyOCR")
                easy_result = self.easy_reader.readtext(preprocessed_path)
                results['easy'] = self.parse_easy_result(easy_result)
                logger.info(f"EasyOCR extracted {len(results['easy'])} characters")
            except Exception as e:
                logger.error(f"EasyOCR failed: {e}")
                results['easy'] = ""
        else:
            results['easy'] = ""
        
        # Tesseract (with custom config)
        try:
            logger.info("Running Tesseract OCR")
            custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz@.-:,/() '
            tess_result = pytesseract.image_to_string(Image.open(preprocessed_path), config=custom_config)
            results['tesseract'] = tess_result
            logger.info(f"Tesseract extracted {len(results['tesseract'])} characters")
        except Exception as e:
            logger.error(f"Tesseract failed: {e}")
            results['tesseract'] = ""
        
        # Clean up temporary file
        try:
            os.remove(preprocessed_path)
        except:
            pass
        
        # Consolidate results from all engines
        consolidated = self.consolidate_ocr_results(results)
        logger.info(f"Consolidated text: {len(consolidated)} characters")
        
        return consolidated
    
    def extract_text_from_pdf(self, pdf_path):
        """
        Extract text from a PDF file by converting to images and using OCR.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Extracted text as string
        """
        logger.info(f"Extracting text from PDF: {pdf_path}")
        
        try:
            from pdf2image import convert_from_path
            
            # Convert PDF to images
            images = convert_from_path(pdf_path)
            
            # Process each page
            all_text = []
            for i, image in enumerate(images):
                # Save image temporarily
                temp_image_path = f"{pdf_path}_page_{i+1}.jpg"
                image.save(temp_image_path, 'JPEG')
                
                # Extract text using OCR
                page_text = self.extract_text_multi_ocr(temp_image_path)
                all_text.append(f"--- Page {i+1} ---\n{page_text}")
                
                # Clean up temporary image
                try:
                    os.remove(temp_image_path)
                except:
                    pass
            
            return "\n\n".join(all_text)
        
        except ImportError:
            logger.error("pdf2image not available. Cannot process PDF.")
            return "ERROR: pdf2image library not available. Please install it to process PDFs."
        except Exception as e:
            logger.error(f"Error processing PDF: {e}")
            return f"ERROR: Failed to process PDF: {e}"
    
    def process_document(self, file_path):
        """Process any document (image or PDF) and extract text"""
        logger.info(f"Processing document: {file_path}")
        
        # Check file extension
        _, ext = os.path.splitext(file_path)
        ext = ext.lower()
        
        if ext in ['.pdf']:
            return self.extract_text_from_pdf(file_path)
        elif ext in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif']:
            return self.extract_text_multi_ocr(file_path)
        else:
            raise ValueError(f"Unsupported file format: {ext}") 