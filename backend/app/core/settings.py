import os

from dotenv import load_dotenv

load_dotenv(override=True)


class Settings:
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./temp.db")
    DEBUG_MODE = os.getenv("DEBUG_MODE", "false").lower() == "true"
    TIMEOUT_TIME = int(os.getenv("TIMEOUT_TIME", "30"))
    ORIGIN_URLS = os.getenv(
        "ORIGIN_URLS",
        "http://localhost|http://localhost:5173|http://127.0.0.1|http://127.0.0.1:5173",
    )
    LOCALE = os.getenv("LOCALE", "zh-cn")
    MODEL_QUALITY = os.getenv("MODEL_QUALITY", "gpt-5.1")
    MODEL_BALANCED = os.getenv("MODEL_BALANCED", "gpt-5-mini")
    MODEL_SPEED = os.getenv("MODEL_SPEED", "gpt-5-nano")


SETTINGS = Settings()
