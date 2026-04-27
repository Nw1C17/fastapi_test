import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@db:5432/wallet_db")
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"

settings = Settings()