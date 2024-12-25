from dataclasses import dataclass
from typing import Optional
import os
from dotenv import load_dotenv


@dataclass
class Config:
    """Application configuration loaded from environment variables."""

    goodfire_api_key: str
    fal_key: str
    supabase_url: str
    supabase_key: str
    supabase_service_key: str
    log_level: Optional[str] = "INFO"


def load_config() -> Config:
    """Load configuration from environment variables."""
    load_dotenv()

    return Config(
        goodfire_api_key=os.getenv("GOODFIRE_API_KEY", ""),
        fal_key=os.getenv("FAL_KEY", ""),
        supabase_url=os.getenv("SUPABASE_URL", ""),
        supabase_key=os.getenv("SUPABASE_ANON_KEY", ""),
        supabase_service_key=os.getenv("SUPABASE_SERVICE_KEY", ""),
        log_level=os.getenv("LOG_LEVEL", "INFO"),
    )
