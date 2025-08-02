from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    # MongoDB Configuration
    mongodb_url: str = "mongodb+srv://shri66688:4mrOf12CkYQWUuAf@fastapicloud.g5qhi.mongodb.net/"
    mongodb_db: str = "email_scheduler"
    
    # Google OAuth2 Configuration
    google_client_id: str = "383809440934-j3j60ub8fmmfgf1b34p65lp5pqvt0g8k.apps.googleusercontent.com"
    google_client_secret: str
    google_redirect_uri: str = "http://localhost:8000/auth/google/callback"
    
    # JWT Configuration
    jwt_secret_key: str = "your_super_secret_jwt_key_that_should_be_at_least_32_characters_long_for_security"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Application Configuration
    app_name: str = "Email Scheduler"
    debug: bool = False  # Set to False for production
    host: str = "0.0.0.0"
    port: int = int(os.getenv("PORT", 8000))
    
    # File Upload Configuration
    max_file_size: int = 10485760  # 10MB
    upload_dir: str = "uploads"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Create settings instance
settings = Settings()

# Ensure upload directory exists
os.makedirs(settings.upload_dir, exist_ok=True) 