import os
from dotenv import load_dotenv

# Load .env file when the app starts
load_dotenv()

class Settings:
    def __init__(self):
        self.DATABASE_URL: str = os.getenv("DATABASE_URL", "")

        if not self.DATABASE_URL:
            raise ValueError("DATABASE_URL is not set in the environment variables")

# Single global settings instance
settings = Settings()
