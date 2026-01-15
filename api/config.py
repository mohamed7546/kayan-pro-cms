import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Telegram
    TELEGRAM_TOKEN: str = os.getenv("TELEGRAM_TOKEN", "")
    ADMIN_ID: str = os.getenv("ADMIN_ID", "")
    
    # AI (Groq)
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    
    # Database (Supabase)
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")
    SUPABASE_SERVICE_KEY: str = os.getenv("SUPABASE_SERVICE_KEY", "")
    
    # Storage (Cloudinary)
    CLOUDINARY_CLOUD_NAME: str = os.getenv("CLOUDINARY_CLOUD_NAME", "")
    CLOUDINARY_API_KEY: str = os.getenv("CLOUDINARY_API_KEY", "")
    CLOUDINARY_API_SECRET: str = os.getenv("CLOUDINARY_API_SECRET", "")
    
    # Admin Panel
    ADMIN_USERNAME: str = os.getenv("ADMIN_USERNAME", "admin")
    ADMIN_PASSWORD: str = os.getenv("ADMIN_PASSWORD", "")
    JWT_SECRET: str = os.getenv("JWT_SECRET", "change-this-secret-key")
    
    # Domains
    PUBLIC_DOMAIN: str = os.getenv("PUBLIC_DOMAIN", "kayan-pro.vercel.app")
    ADMIN_DOMAIN: str = os.getenv("ADMIN_DOMAIN", "kayan-admin.vercel.app")
    
    class Config:
        env_file = ".env"

settings = Settings()
