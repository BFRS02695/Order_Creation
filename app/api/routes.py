from fastapi import APIRouter, UploadFile, File, HTTPException, Form, BackgroundTasks, Depends
from fastapi.responses import JSONResponse, HTMLResponse
import shutil
import os
from pathlib import Path
import uuid
import logging
from typing import Optional, Dict, Any

from app.services.ocr_service import MultiOCRService
from app.services.llm_service import LLMInvoiceProcessor
from app.services.validation_service import InvoiceValidator
from app.services.shiprocket_service import ShiprocketAPI
from app.core.config import config

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

# Initialize services
ocr_service = MultiOCRService()
llm_processor = LLMInvoiceProcessor(model=config.OLLAMA_MODEL, ollama_url=config.OLLAMA_HOST)
validator = InvoiceValidator()

# In-memory cache for processing results
processing_cache = {}

def get_shiprocket_api(email: str, password: str) -> ShiprocketAPI:
    """Get a configured ShiprocketAPI instance"""
    return ShiprocketAPI(email=email, password=password)

@router.get("/", response_class=HTMLResponse)
async def root():
    """Root endpoint that displays a simple UI"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Invoice to Order Processor</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }
            h1 { color: #2c3e50; }
            form { background: #f9f9f9; padding: 20px; border-radius: 8px; max-width: 500px; }
            input, button { margin: 10px 0; padding: 10px; width: 100%; }
            button { background: #3498db; color: white; border: none; cursor: pointer; }
            button:hover { background: #2980b9; }
            .footer { margin-top: 40px; font-size: 0.8em; color: #7f8c8d; }
        </style>
    </head>
    <body>
        <h1>Invoice to Order Processor</h1>
        <p>Upload an invoice image or PDF to extract information and create a Shiprocket order.</p>
        
        <form action="/process-invoice/" method="post" enctype="multipart/form-data">
            <h3>Upload Invoice</h3>
            <input type="file" name="file" accept=".jpg,.jpeg,.png,.pdf,.tiff">
            
            <h3>Shiprocket Credentials (Optional)</h3>
            <input type="email" name="shiprocket_email" placeholder="Shiprocket Email">
            <input type="password" name="shiprocket_password" placeholder="Shiprocket Password">
            
            <button type="submit">Process Invoice</button>
        </form>
        
        <div class="footer">
            <p>API Documentation: <a href="/docs">/docs</a></p>
        </div>
    </body>
    </html>
    """

@router.post("/process-invoice/")
async def process_invoice(
    file: UploadFile = File(...),
    shiprocket_email: Optional[str] = Form(None),
    shiprocket_password: Optional[str] = Form(None),
    background_tasks: BackgroundTasks = None
):
    """
    Process invoice image/PDF and create Shiprocket order
    
    This endpoint:
    1. Accepts an invoice file (image or PDF)
    2. Extracts text using multi-OCR approach
    3. Parses information using LLM
    4. Validates the extracted data
    5. Optionally creates a Shiprocket order
    """
    try:
        # Validate file type
        if not file.content_type.startswith(('image/', 'application/pdf')):
            raise HTTPException(
                status_code=400, 
                detail="Only image and PDF files are supported"
            )
        
        # Save uploaded file
        file_id = str(uuid.uuid4())
        file_extension = os.path.splitext(file.filename)[1].lower()
        file_path = config.UPLOAD_DIR / f"{file_id}{file_extension}"
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        logger.info(f"File uploaded: {file_path}")
        
        # Step 1: OCR Processing
        logger.info("Starting OCR processing...")
        
        try:
            # Select processing method based on file type
            if file_extension == '.pdf':
                ocr_text = ocr_service.extract_text_from_pdf(str(file_path))
            else:
                ocr_text = ocr_service.extract_text_multi_ocr(str(file_path))
                
            logger.info(f"OCR text extracted, length: {len(ocr_text)}")
        except Exception as e:
            logger.error(f"OCR processing failed: {e}")
            raise HTTPException(status_code=500, detail=f"OCR processing failed: {str(e)}")
        
        if not ocr_text.strip():
            raise HTTPException(
                status_code=400, 
                detail="No text could be extracted from the image"
            )
        
        # Step 2: LLM Field Extraction
        logger.info("Extracting fields using LLM...")
        try:
            extracted_data = llm_processor.extract_invoice_fields(ocr_text)
            extracted_data = llm_processor.refine_extraction(extracted_data, ocr_text)
            logger.info(f"Fields extracted: {len(extracted_data)}")
        except Exception as e:
            logger.error(f"Field extraction failed: {e}")
            raise HTTPException(status_code=500, detail=f"Field extraction failed: {str(e)}")
        
        # Step 3: Data Validation
        logger.info("Validating extracted data...")
        errors, warnings = validator.validate_invoice_data(extracted_data)
        
        # Save processed file to processed directory
        processed_path = config.PROCESSED_DIR / f"{file_id}{file_extension}"
        shutil.copy(file_path, processed_path)
        
        # Step 4: Create Shiprocket Order (if credentials provided)
        order_response = None
        if shiprocket_email and shiprocket_password:
            logger.info("Creating Shiprocket order...")
            try:
                shiprocket_api = get_shiprocket_api(shiprocket_email, shiprocket_password)
                order_response = shiprocket_api.create_order_from_invoice(extracted_data)
                logger.info(f"Shiprocket order created: {order_response}")
            except Exception as e:
                logger.error(f"Shiprocket order creation failed: {e}")
                warnings.append(f"Order creation failed: {str(e)}")
        
        # Cache the results
        result = {
            "status": "error" if errors else "success",
            "file_id": file_id,
            "filename": file.filename,
            "extracted_data": extracted_data,
            "validation_errors": errors,
            "validation_warnings": warnings,
            "shiprocket_order": order_response,
            "ocr_text": ocr_text
        }
        processing_cache[file_id] = result
        
        # Clean up uploaded file
        os.remove(file_path)
        
        if errors:
            return JSONResponse(
                status_code=400,
                content=result
            )
        
        return result
        
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Processing failed: {e}")
        
        # Cleanup file if exists
        if 'file_path' in locals() and os.path.exists(file_path):
            os.remove(file_path)
        
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/extract-text/")
async def extract_text_only(
    file: UploadFile = File(...)
):
    """
    Extract text from invoice using OCR only
    
    This endpoint:
    1. Accepts an invoice file (image or PDF)
    2. Extracts text using multi-OCR approach
    3. Returns the extracted text without further processing
    """
    try:
        # Validate file type
        if not file.content_type.startswith(('image/', 'application/pdf')):
            raise HTTPException(
                status_code=400, 
                detail="Only image and PDF files are supported"
            )
        
        # Save uploaded file
        file_id = str(uuid.uuid4())
        file_extension = os.path.splitext(file.filename)[1].lower()
        file_path = config.UPLOAD_DIR / f"{file_id}{file_extension}"
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        logger.info(f"File uploaded for OCR: {file_path}")
        
        # OCR Processing
        try:
            if file_extension == '.pdf':
                ocr_text = ocr_service.extract_text_from_pdf(str(file_path))
            else:
                ocr_text = ocr_service.extract_text_multi_ocr(str(file_path))
                
            logger.info(f"OCR text extracted, length: {len(ocr_text)}")
        except Exception as e:
            logger.error(f"OCR processing failed: {e}")
            raise HTTPException(status_code=500, detail=f"OCR processing failed: {str(e)}")
        
        # Cleanup uploaded file
        os.remove(file_path)
        
        return {
            "status": "success",
            "ocr_text": ocr_text,
            "file_processed": file.filename
        }
        
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"OCR processing failed: {e}")
        
        # Cleanup file if exists
        if 'file_path' in locals() and os.path.exists(file_path):
            os.remove(file_path)
        
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/results/{file_id}")
async def get_processing_results(file_id: str):
    """Get the results of a previously processed file"""
    if file_id not in processing_cache:
        raise HTTPException(status_code=404, detail=f"Results for file ID {file_id} not found")
    
    return processing_cache[file_id]

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    # Check if OCR service is working
    ocr_status = "up"
    try:
        # Test OCR with a minimal initialization
        ocr_service.logger.info("Health check")
    except:
        ocr_status = "down"
    
    # Check if LLM service is working
    llm_status = "up"
    try:
        # Test LLM connection
        llm_processor.test_connection()
    except:
        llm_status = "down"
    
    return {
        "status": "healthy" if ocr_status == "up" and llm_status == "up" else "degraded",
        "version": "1.0.0",
        "services": {
            "ocr": ocr_status,
            "llm": llm_status
        }
    } 