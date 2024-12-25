from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID


@dataclass
class Prompt:
    """Represents a prompt record in the database."""

    id: UUID
    created_at: datetime
    feature_input: str
    feature: str
    strength: float
    generated_prompt: str
    image_url: Optional[str] = None
