import cv2
import numpy as np
import pytesseract
from PIL import Image
import logging
import os
from paddleocr import PaddleOCR
import easyocr
from collections import Counter
import re

class MultiOCRService:
    def __init__(self):
        # Initialize OCR engines
        self.paddle_ocr = PaddleOCR(use_angle_cls=True, lang='en')
        self.easy_reader = easyocr.Reader(['en'])
        
        # Configure logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
    def preprocess_image(self, image_path):
        """Advanced image preprocessing for better OCR accuracy"""
        self.logger.info(f"Preprocessing image: {image_path}")
        
        # Read image
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"Could not read image: {image_path}")
            
        # Get image dimensions
        h, w = img.shape[:2]
        
        # Resize if too large or too small (optimal size for OCR)
        if max(h, w) > 3000:
            scale = 3000 / max(h, w)
            img = cv2.resize(img, (int(w * scale), int(h * scale)))
        elif min(h, w) < 300:
            scale = 300 / min(h, w)
            img = cv2.resize(img, (int(w * scale), int(h * scale)))
            
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Apply threshold to get black and white image
        _, binary = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)
        
        # Count white pixels (text)
        text_pixel_count = np.sum(binary == 255)
        
        # If very few text pixels, adjust threshold
        if text_pixel_count < (binary.shape[0] * binary.shape[1] * 0.01):
            # Use adaptive thresholding for better results
            binary = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                          cv2.THRESH_BINARY_INV, 11, 2)
        
        # Invert back to black text on white background
        binary = cv2.bitwise_not(binary)
        
        # Noise removal using median blur
        denoised = cv2.medianBlur(binary, 3)
        
        # Contrast enhancement using CLAHE
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray)
        
        # Deskewing if needed
        try:
            coords = np.column_stack(np.where(denoised > 0))
            angle = cv2.minAreaRect(coords)[-1]
            
            if angle < -45:
                angle = -(90 + angle)
            else:
                angle = -angle
                
            # Only deskew if angle is significant
            if abs(angle) > 0.5:
                (h, w) = denoised.shape[:2]
                center = (w // 2, h // 2)
                M = cv2.getRotationMatrix2D(center, angle, 1.0)
                denoised = cv2.warpAffine(denoised, M, (w, h), 
                                        flags=cv2.INTER_CUBIC, 
                                        borderMode=cv2.BORDER_REPLICATE)
        except:
            self.logger.warning("Skipping deskew - not enough contours")
        
        # Save preprocessed image temporarily
        preprocessed_path = f"{os.path.splitext(image_path)[0]}_preprocessed.jpg"
        cv2.imwrite(preprocessed_path, denoised)
        
        return preprocessed_path, enhanced, denoised
    
    def parse_paddle_result(self, result):
        """Parse PaddleOCR results into a string"""
        if not result or len(result) == 0:
            return ""
            
        text_lines = []
        
        # PaddleOCR format varies by version, handle both formats
        try:
            # Newer versions
            for line in result:
                if isinstance(line, list):
                    for item in line:
                        if len(item) >= 2 and isinstance(item[1], str):
                            text_lines.append(item[1])
                elif isinstance(line, dict) and 'text' in line:
                    text_lines.append(line['text'])
        except:
            # Older versions or different format
            for block in result:
                if isinstance(block, list):
                    for line in block:
                        if len(line) >= 2:
                            text_lines.append(line[1][0])
        
        return '\n'.join(text_lines)
    
    def parse_easy_result(self, result):
        """Parse EasyOCR results into a string"""
        if not result:
            return ""
            
        text_lines = []
        
        for detection in result:
            if len(detection) >= 2:
                text_lines.append(detection[1])
                
        return '\n'.join(text_lines)
    
    def consolidate_ocr_results(self, results):
        """Consolidate results from multiple OCR engines intelligently"""
        self.logger.info("Consolidating OCR results")
        
        # Extract texts from each engine
        paddle_text = results.get('paddle', '')
        easy_text = results.get('easy', '')
        tess_text = results.get('tesseract', '')
        
        # If any engine failed, use the others
        if not paddle_text.strip():
            self.logger.warning("PaddleOCR failed to produce results")
        if not easy_text.strip():
            self.logger.warning("EasyOCR failed to produce results")
        if not tess_text.strip():
            self.logger.warning("Tesseract failed to produce results")
        
        # Count successful engines
        successful_engines = sum(1 for text in [paddle_text, easy_text, tess_text] if text.strip())
        
        if successful_engines == 0:
            raise ValueError("All OCR engines failed to extract text")
        
        # Split texts into lines for line-by-line comparison
        paddle_lines = paddle_text.splitlines() if paddle_text else []
        easy_lines = easy_text.splitlines() if easy_text else []
        tess_lines = tess_text.splitlines() if tess_text else []
        
        # Get the maximum number of lines
        max_lines = max(len(paddle_lines), len(easy_lines), len(tess_lines))
        
        # Normalize line counts
        paddle_lines = paddle_lines + [''] * (max_lines - len(paddle_lines))
        easy_lines = easy_lines + [''] * (max_lines - len(easy_lines))
        tess_lines = tess_lines + [''] * (max_lines - len(tess_lines))
        
        # Consolidate line by line
        consolidated_lines = []
        
        for i in range(max_lines):
            line_candidates = []
            
            if paddle_lines[i].strip():
                line_candidates.append(paddle_lines[i])
            if easy_lines[i].strip():
                line_candidates.append(easy_lines[i])
            if tess_lines[i].strip():
                line_candidates.append(tess_lines[i])
                
            if line_candidates:
                # Use the most common line among engines
                if len(line_candidates) > 1:
                    counter = Counter(line_candidates)
                    most_common = counter.most_common(1)[0][0]
                    consolidated_lines.append(most_common)
                else:
                    consolidated_lines.append(line_candidates[0])
        
        # Additional cleaning of the consolidated text
        result_text = '\n'.join(consolidated_lines)
        
        # Remove duplicate consecutive lines
        clean_lines = []
        prev_line = None
        
        for line in result_text.splitlines():
            if line != prev_line:
                clean_lines.append(line)
                prev_line = line
                
        result_text = '\n'.join(clean_lines)
        
        # Some common OCR error corrections
        result_text = self.clean_ocr_text(result_text)
        
        return result_text
    
    def clean_ocr_text(self, text):
        """Clean common OCR errors"""
        # Replace common OCR mistakes
        replacements = {
            'l\'lVOICE': 'INVOICE',
            'lNVOlCE': 'INVOICE',
            'lNVOICE': 'INVOICE',
            'INV0ICE': 'INVOICE',
            'GSTlN': 'GSTIN',
            'GST|N': 'GSTIN',
            'GST!N': 'GSTIN',
            # Add more common replacements as needed
        }
        
        for old, new in replacements.items():
            text = text.replace(old, new)
            
        # Fix common GSTIN format issues
        gstin_pattern = r'[0-9]{2}[A-Za-z]{5}[0-9]{4}[A-Za-z]{1}[1-9A-Za-z]{1}[Zz]{1}[0-9A-Za-z]{1}'
        gstin_matches = re.finditer(gstin_pattern, text, re.IGNORECASE)
        
        for match in gstin_matches:
            original = match.group(0)
            corrected = original.upper()  # Ensure GSTIN is uppercase
            text = text.replace(original, corrected)
            
        return text
    
    def extract_text_multi_ocr(self, image_path):
        """Extract text using multiple OCR engines and consolidate results"""
        self.logger.info(f"Starting multi-OCR extraction for: {image_path}")
        
        try:
            # Preprocess the image for better OCR results
            preprocessed_path, enhanced, denoised = self.preprocess_image(image_path)
            
            results = {}
            
            # PaddleOCR
            try:
                self.logger.info("Running PaddleOCR")
                paddle_result = self.paddle_ocr.ocr(preprocessed_path, cls=True)
                results['paddle'] = self.parse_paddle_result(paddle_result)
                self.logger.info(f"PaddleOCR extracted {len(results['paddle'])} chars")
            except Exception as e:
                self.logger.error(f"PaddleOCR failed: {e}")
                results['paddle'] = ""
            
            # EasyOCR
            try:
                self.logger.info("Running EasyOCR")
                easy_result = self.easy_reader.readtext(preprocessed_path)
                results['easy'] = self.parse_easy_result(easy_result)
                self.logger.info(f"EasyOCR extracted {len(results['easy'])} chars")
            except Exception as e:
                self.logger.error(f"EasyOCR failed: {e}")
                results['easy'] = ""
            
            # Tesseract
            try:
                self.logger.info("Running Tesseract OCR")
                # Use different preprocessing for Tesseract
                custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.,:;₹$@#%&*()+-/\|<> "'
                tess_result = pytesseract.image_to_string(Image.fromarray(enhanced), config=custom_config)
                results['tesseract'] = tess_result
                self.logger.info(f"Tesseract extracted {len(results['tesseract'])} chars")
            except Exception as e:
                self.logger.error(f"Tesseract failed: {e}")
                results['tesseract'] = ""
            
            # Clean up temp file
            try:
                if os.path.exists(preprocessed_path):
                    os.remove(preprocessed_path)
            except:
                self.logger.warning(f"Failed to remove temporary file: {preprocessed_path}")
            
            # Consolidate results from all engines
            consolidated_text = self.consolidate_ocr_results(results)
            self.logger.info(f"Consolidated text length: {len(consolidated_text)} chars")
            
            return consolidated_text
            
        except Exception as e:
            self.logger.error(f"Error in OCR processing: {str(e)}")
            raise Exception(f"OCR processing failed: {str(e)}")
    
    def extract_text_from_pdf(self, pdf_path):
        """Extract text from PDF files using OCR"""
        try:
            import pdf2image
            
            self.logger.info(f"Converting PDF to images: {pdf_path}")
            
            # Convert PDF to images
            images = pdf2image.convert_from_path(pdf_path)
            
            all_text = []
            
            # Process each page
            for i, image in enumerate(images):
                self.logger.info(f"Processing PDF page {i+1}/{len(images)}")
                
                # Save temporary image
                temp_img_path = f"{os.path.splitext(pdf_path)[0]}_page_{i+1}.jpg"
                image.save(temp_img_path, 'JPEG')
                
                # Extract text from the image
                text = self.extract_text_multi_ocr(temp_img_path)
                all_text.append(text)
                
                # Remove temporary image
                try:
                    if os.path.exists(temp_img_path):
                        os.remove(temp_img_path)
                except:
                    self.logger.warning(f"Failed to remove temporary file: {temp_img_path}")
            
            return "\n\n----- PAGE BREAK -----\n\n".join(all_text)
            
        except ImportError:
            self.logger.error("pdf2image not installed. Install with: pip install pdf2image")
            raise ImportError("pdf2image library is required for PDF processing")
        except Exception as e:
            self.logger.error(f"Error processing PDF: {str(e)}")
            raise Exception(f"PDF processing failed: {str(e)}")
            
    def process_document(self, file_path):
        """Process any document (image or PDF) and extract text"""
        self.logger.info(f"Processing document: {file_path}")
        
        # Check file extension
        _, ext = os.path.splitext(file_path)
        ext = ext.lower()
        
        if ext in ['.pdf']:
            return self.extract_text_from_pdf(file_path)
        elif ext in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif']:
            return self.extract_text_multi_ocr(file_path)
        else:
            raise ValueError(f"Unsupported file format: {ext}") 