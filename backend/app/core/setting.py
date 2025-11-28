import os

from dotenv import load_dotenv

load_dotenv(override=True)


class Setting:
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./temp.db")
    DEBUG_MODE = os.getenv("DEBUG_MODE", "true").lower() == "true"
    TIMEOUT_TIME = int(os.getenv("DEBUG_MODE", "30"))
    ORIGIN_URLS = os.getenv(
        "ORIGIN_URLS",
        "http://localhost|http://localhost:5173|http://127.0.0.1|http://127.0.0.1:5173",
    )


SETTING = Setting()
