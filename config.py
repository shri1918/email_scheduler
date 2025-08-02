from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    # MongoDB Configuration
    mongodb_url: str = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    mongodb_db: str = os.getenv("MONGODB_DB", "email_scheduler")
    
    # Alternative MongoDB connection for Railway (if main one fails)
    mongodb_url_alt: str = os.getenv("MONGODB_URL_ALT", "")
    
    # Google OAuth2 Configuration
    google_client_id: str = os.getenv("GOOGLE_CLIENT_ID", "383809440934-j3j60ub8fmmfgf1b34p65lp5pqvt0g8k.apps.googleusercontent.com")
    google_client_secret: str = os.getenv("GOOGLE_CLIENT_SECRET", "")
    google_redirect_uri: str = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8000/auth/google/callback")
    
    # JWT Configuration
    jwt_secret_key: str = os.getenv("JWT_SECRET_KEY", "your_super_secret_jwt_key_that_should_be_at_least_32_characters_long_for_security")
    jwt_algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    # Application Configuration
    app_name: str = os.getenv("APP_NAME", "Email Scheduler")
    debug: bool = os.getenv("DEBUG", "False").lower() == "true"
    host: str = os.getenv("HOST", "0.0.0.0")
    port: int = int(os.getenv("PORT", "8000"))
    
    # File Upload Configuration
    max_file_size: int = int(os.getenv("MAX_FILE_SIZE", "10485760"))  # 10MB
    upload_dir: str = os.getenv("UPLOAD_DIR", "uploads")
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Create settings instance
settings = Settings()

# Ensure upload directory exists
os.makedirs(settings.upload_dir, exist_ok=True) 