import os
from typing import List
from dotenv import load_dotenv

# Load .env file when the app starts
load_dotenv()

def _split_csv(value: str) -> List[str]:
    """
    Split comma-separated values, trimming whitespace.
    Example: "http://a.com, http://b.com"
    """
    return [v.strip() for v in value.split(",") if v.strip()]




class Settings:
    def __init__(self):
        # Environment
        self.ENV: str = os.getenv("ENV", "local")  # local | prod
        cors_raw = os.getenv("CORS_ORIGINS", "")
        self.CORS_ORIGINS: List[str] = _split_csv(cors_raw) if cors_raw else []

        self.DATABASE_URL: str = os.getenv("DATABASE_URL", "")
        if not self.DATABASE_URL:
            raise ValueError("DATABASE_URL is not set in the environment variables")
        

        # Auth / JWT
        self.SECRET_KEY: str = os.getenv("SECRET_KEY", "")
        if not self.SECRET_KEY:
            # You can allow blank in local, but I recommend always setting it.
            raise ValueError("SECRET_KEY is not set in the environment variables")
        self.ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
        self.ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
            os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "15")
        )
        # Refresh token (used in Session 12)
        self.REFRESH_TOKEN_EXPIRE_DAYS: int = int(
            os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "14")
        )

# Single global settings instance
settings = Settings()
