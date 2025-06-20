# Invoice to Order Processing System

## Overview

The Invoice to Order Processing System automates the conversion of B2B invoice documents (images or PDFs) into Shiprocket orders. It uses open-source OCR technology and locally-run LLM models to extract and process invoice data without relying on proprietary cloud APIs.

## Key Features

- **Multi-OCR Processing**: Combines PaddleOCR, EasyOCR, and Tesseract for maximum accuracy
- **Local LLM Processing**: Uses Llama 3 via Ollama for privacy-focused data extraction
- **Advanced Image Preprocessing**: Improves OCR accuracy with sophisticated image enhancement
- **GSTIN Validation**: Validates Indian business documents
- **Shiprocket Integration**: Seamlessly creates orders from extracted invoice data
- **REST API**: FastAPI-based interface for easy integration

## Project Structure

```
/
├── app/                      # Main application package
│   ├── api/                  # API endpoints and routes
│   ├── core/                 # Core configuration
│   ├── models/               # Data models
│   ├── services/             # Service implementations
│   └── utils/                # Utility functions
├── samples/                  # Sample invoice files
├── tests/                    # Test cases
├── Technical_Documentation.md   # Technical documentation
├── Feature_and_Architecture_Documentation.md   # Feature and architecture documentation
├── app.py                    # Simple test application
├── main.py                   # Application entry point
├── requirements.txt          # Package dependencies
└── README.md                 # This file
```

## Prerequisites

- Python 3.9+
- [Optional] Ollama for local LLM processing
- [Optional] Tesseract OCR for additional OCR capabilities

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/invoice-to-order.git
   cd invoice-to-order
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. [Optional] Set up Ollama:
   ```bash
   # Run the setup script
   ./setup_ollama.sh
   ```

## Configuration

The system can be configured using environment variables or by creating a `.env` file:

```
# Core settings
DEBUG=True
LOG_LEVEL=INFO
PORT=8000
HOST=0.0.0.0

# OCR settings
OCR_PREPROCESSOR=standard
OCR_ENGINES=paddle,easy,tesseract
OCR_CONFIDENCE_THRESHOLD=0.5
OCR_USE_GPU=False

# LLM settings
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama3

# API settings
CORS_ORIGINS=*
API_KEY=
```

## Running the Application

### Quick Start (Simple Test Server)

```bash
python app.py
```

This will start a simplified test server on http://localhost:8080.

### Full Application

```bash
python main.py
```

This will start the full application with all services.

## Testing

1. Run the test script:
   ```bash
   python test_api.py
   ```

2. Try the web interface:
   Open http://localhost:8080 in your browser and upload an invoice.

3. Use the API directly:
   ```bash
   # Health check
   curl http://localhost:8080/health
   
   # Process an invoice
   curl -X POST -F "file=@samples/invoice.pdf" http://localhost:8080/extract-text/
   ```

## Documentation

For more detailed information, refer to:

- [Technical Documentation](Technical_Documentation.md): Detailed technical information about the system implementation
- [Feature and Architecture Documentation](Feature_and_Architecture_Documentation.md): Overview of features and system architecture

## License

This project is open source under the MIT License.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
