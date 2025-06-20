import os
from pathlib import Path
from typing import List, Optional, Union, Dict, Any
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv("config.env")

class Config:
    """Configuration settings loaded from environment variables"""
    
    # Application settings
    DEBUG: bool = os.getenv("DEBUG", "false").lower() in ("true", "1", "t", "yes")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    PORT: int = int(os.getenv("PORT", "8000"))
    HOST: str = os.getenv("HOST", "0.0.0.0")
    
    # Paths
    BASE_DIR: Path = Path(__file__).parent.absolute()
    UPLOAD_DIR: Path = Path(os.getenv("UPLOAD_DIR", "uploads"))
    PROCESSED_DIR: Path = Path(os.getenv("PROCESSED_DIR", "processed"))
    
    # Ensure directories exist
    UPLOAD_DIR.mkdir(exist_ok=True)
    PROCESSED_DIR.mkdir(exist_ok=True)
    
    # Ollama configuration
    OLLAMA_HOST: str = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama3:8b")
    
    # OCR settings
    OCR_PREPROCESSOR: str = os.getenv("OCR_PREPROCESSOR", "advanced")
    OCR_ENGINES: List[str] = os.getenv("OCR_ENGINES", "paddle,easy,tesseract").split(",")
    OCR_CONFIDENCE_THRESHOLD: float = float(os.getenv("OCR_CONFIDENCE_THRESHOLD", "0.5"))
    OCR_USE_GPU: bool = os.getenv("OCR_USE_GPU", "false").lower() in ("true", "1", "t", "yes")
    
    # Tesseract configuration
    TESSERACT_CMD: Optional[str] = os.getenv("TESSERACT_CMD")
    if TESSERACT_CMD:
        os.environ["TESSERACT_CMD"] = TESSERACT_CMD
    
    # Processing options
    ENABLE_CACHING: bool = os.getenv("ENABLE_CACHING", "true").lower() in ("true", "1", "t", "yes")
    MAX_WORKERS: int = int(os.getenv("MAX_WORKERS", "4"))
    
    # Database settings
    DB_TYPE: str = os.getenv("DB_TYPE", "sqlite")
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: int = int(os.getenv("DB_PORT", "5432"))
    DB_NAME: str = os.getenv("DB_NAME", "invoice_db")
    DB_USER: str = os.getenv("DB_USER", "postgres")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "password")
    
    # Construct database URL
    @property
    def DATABASE_URL(self) -> str:
        if self.DB_TYPE == "sqlite":
            return f"sqlite:///{self.BASE_DIR / 'invoice_db.sqlite'}"
        elif self.DB_TYPE == "postgresql":
            return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        else:
            raise ValueError(f"Unsupported database type: {self.DB_TYPE}")
    
    # Redis settings
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_DB: int = int(os.getenv("REDIS_DB", "0"))
    REDIS_PASSWORD: Optional[str] = os.getenv("REDIS_PASSWORD")
    
    @property
    def REDIS_URL(self) -> str:
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
    
    # Shiprocket settings
    SHIPROCKET_EMAIL: Optional[str] = os.getenv("SHIPROCKET_EMAIL")
    SHIPROCKET_PASSWORD: Optional[str] = os.getenv("SHIPROCKET_PASSWORD")
    SHIPROCKET_DEFAULT_PICKUP: str = os.getenv("SHIPROCKET_DEFAULT_PICKUP", "Primary")
    
    # Security settings
    CORS_ORIGINS: List[str] = os.getenv("CORS_ORIGINS", "*").split(",")
    API_KEY: Optional[str] = os.getenv("API_KEY")
    
    def as_dict(self) -> Dict[str, Any]:
        """Return configuration as a dictionary (for logging/debugging)"""
        # Convert to dict but exclude sensitive information
        config_dict = {
            key: value for key, value in self.__dict__.items() 
            if not key.startswith("_") and key not in ("SHIPROCKET_PASSWORD", "DB_PASSWORD", "REDIS_PASSWORD", "API_KEY")
        }
        
        # Add properties
        config_dict["DATABASE_URL"] = "******" if self.DB_PASSWORD else self.DATABASE_URL
        config_dict["REDIS_URL"] = "******" if self.REDIS_PASSWORD else self.REDIS_URL
        
        # Mask sensitive information
        if self.SHIPROCKET_EMAIL:
            config_dict["SHIPROCKET_EMAIL"] = "******"
        
        return config_dict

# Create a global config instance
config = Config()

# For debugging
if __name__ == "__main__":
    import json
    print(json.dumps(config.as_dict(), indent=2, default=str)) 