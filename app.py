"""
Simplified FastAPI application for testing the Invoice to Order Processing System
"""
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import HTMLResponse
import shutil
import os
import logging
from pathlib import Path
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Invoice to Order Processor",
    description="Process invoice images/PDFs and extract text",
    version="1.0.0"
)

# Ensure upload directory exists
UPLOAD_DIR = Path("app/uploads")
UPLOAD_DIR.mkdir(exist_ok=True, parents=True)

@app.get("/", response_class=HTMLResponse)
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
        <p>Upload an invoice image or PDF to extract information.</p>
        
        <form action="/extract-text/" method="post" enctype="multipart/form-data">
            <h3>Upload Invoice</h3>
            <input type="file" name="file" accept=".jpg,.jpeg,.png,.pdf,.tiff,.txt">
            <button type="submit">Extract Text</button>
        </form>
        
        <div class="footer">
            <p>API Documentation: <a href="/docs">/docs</a></p>
        </div>
    </body>
    </html>
    """

@app.post("/extract-text/")
async def extract_text(file: UploadFile = File(...)):
    """
    Extract text from an invoice file (image, PDF, or text).
    """
    try:
        # Validate file type
        content_type = file.content_type or ""
        if not (content_type.startswith(('image/', 'application/pdf')) or content_type == "text/plain"):
            raise HTTPException(
                status_code=400, 
                detail="Only image, PDF, and text files are supported"
            )
        
        # Save uploaded file
        file_id = str(uuid.uuid4())
        file_extension = os.path.splitext(file.filename)[1].lower()
        file_path = UPLOAD_DIR / f"{file_id}{file_extension}"
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        logger.info(f"File uploaded: {file_path}")
        
        # For demonstration purposes, just read the file if it's a text file
        # In a real implementation, this would use OCR for images/PDFs
        if file_extension == '.txt':
            with open(file_path, "r") as f:
                text_content = f.read()
        else:
            # Simulate OCR processing
            text_content = f"[This would contain OCR text from {file.filename}]\n" + \
                          "For testing purposes, we're just returning this placeholder.\n" + \
                          "In a real implementation, this would use the OCR service."
        
        # Clean up the file
        os.remove(file_path)
        
        return {
            "status": "success",
            "filename": file.filename,
            "content_type": file.content_type,
            "file_size": file.size,
            "text_content": text_content
        }
        
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error processing file: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy", "version": "1.0.0"}

if __name__ == "__main__":
    import uvicorn
    print("Starting server on http://0.0.0.0:8080")
    uvicorn.run(app, host="0.0.0.0", port=8080) 