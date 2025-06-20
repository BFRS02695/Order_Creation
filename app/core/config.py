"""
Configuration module for the Invoice to Order Processing System.
"""
import os
from pathlib import Path
from typing import List, Dict, Any

class Config:
    """
    Configuration class for the Invoice to Order Processing System.
    
    Loads configuration from environment variables with fallbacks to defaults.
    """
    # Base paths
    BASE_DIR = Path(__file__).parent.parent.parent
    UPLOAD_DIR = BASE_DIR / "app" / "uploads"
    PROCESSED_DIR = BASE_DIR / "app" / "processed"
    
    # Core settings
    DEBUG = os.getenv("DEBUG", "True").lower() in ("true", "1", "t")
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", "8000"))
    
    # OCR settings
    OCR_PREPROCESSOR = os.getenv("OCR_PREPROCESSOR", "standard")
    OCR_ENGINES = os.getenv("OCR_ENGINES", "paddle,easy,tesseract").split(",")
    OCR_CONFIDENCE_THRESHOLD = float(os.getenv("OCR_CONFIDENCE_THRESHOLD", "0.5"))
    OCR_USE_GPU = os.getenv("OCR_USE_GPU", "False").lower() in ("true", "1", "t")
    
    # LLM settings
    OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3")
    
    # API settings
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")
    API_KEY = os.getenv("API_KEY", "")
    
    def as_dict(self) -> Dict[str, Any]:
        """
        Return the configuration as a dictionary.
        
        Returns:
            Dict[str, Any]: Dictionary of configuration values
        """
        return {
            "debug": self.DEBUG,
            "log_level": self.LOG_LEVEL,
            "host": self.HOST,
            "port": self.PORT,
            "ocr_preprocessor": self.OCR_PREPROCESSOR,
            "ocr_engines": self.OCR_ENGINES,
            "ocr_confidence_threshold": self.OCR_CONFIDENCE_THRESHOLD,
            "ocr_use_gpu": self.OCR_USE_GPU,
            "ollama_host": self.OLLAMA_HOST,
            "ollama_model": self.OLLAMA_MODEL,
            "cors_origins": self.CORS_ORIGINS,
            "api_key": bool(self.API_KEY),  # Just show if it's set, not the actual value
        }

# Create global config instance
config = Config()

# For debugging
if __name__ == "__main__":
    import json
    print(json.dumps(config.as_dict(), indent=2, default=str)) 