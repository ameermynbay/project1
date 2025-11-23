import os
from dotenv import load_dotenv

# Load .env file when the app starts
load_dotenv()

class Settings:
    def __init__(self):
        self.DATABASE_URL: str = os.getenv("DATABASE_URL", "")

        if not self.DATABASE_URL:
            raise ValueError("DATABASE_URL is not set in the environment variables")
        

        # Auth / JWT
        self.SECRET_KEY: str = os.getenv("SECRET_KEY", "change-me-in-production")
        self.ALGORITHM: str = "HS256"
        self.ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
            os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60")
        )

# Single global settings instance
settings = Settings()
