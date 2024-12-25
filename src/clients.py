from typing import Any, Dict
import goodfire
import fal_client
from supabase import create_client, Client
from .config import Config


def init_goodfire(config: Config) -> goodfire.Client:
    """Initialize Goodfire client."""
    return goodfire.Client(api_key=config.goodfire_api_key)


def init_supabase(config: Config) -> Client:
    """Initialize Supabase client with service role key for full access."""
    return create_client(config.supabase_url, config.supabase_service_key)


def generate_image(prompt: str) -> Dict[str, Any]:
    """Generate an image using fal-ai."""
    return fal_client.subscribe(
        "fal-ai/flux/schnell",
        arguments={
            "prompt": prompt,
            "image_size": "landscape_4_3",
            "seed": 42,
            "enable_safety_checker": False,
        },
        with_logs=True,
    )
