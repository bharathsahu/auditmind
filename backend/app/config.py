import os

class Settings:
    PROJECT_NAME: str = "AuditMind API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./auditmind.db")
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "auditmind_super_secret_key_change_in_production_2026")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 # 24 hours
    
    # Hindsight Memory Engine
    HINDSIGHT_URL: str = os.getenv("HINDSIGHT_URL", "http://localhost:8888")
    HINDSIGHT_BANK_ID: str = os.getenv("HINDSIGHT_BANK_ID", "auditmind_org")
    
    # LLM Settings
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")

settings = Settings()
