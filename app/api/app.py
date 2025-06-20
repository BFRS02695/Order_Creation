from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.api.routes import router
from app.core.config import config

# Configure logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("app.log")
    ]
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Invoice to Order Processor",
    description="Process invoice images/PDFs and create Shiprocket orders using open source OCR + LLM",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include router
app.include_router(router)

# Startup event
@app.on_event("startup")
async def startup_event():
    logger.info("Starting Invoice to Order Processing System")
    logger.info(f"Configuration: {config.as_dict()}")
    
    # Ensure required directories exist
    config.UPLOAD_DIR.mkdir(exist_ok=True)
    config.PROCESSED_DIR.mkdir(exist_ok=True)

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down Invoice to Order Processing System") 