import os
import requests
from PIL import Image
from supabase import Client
from uuid import UUID


class StorageManager:
    def __init__(self, supabase: Client):
        self.supabase = supabase

    def save_concept_and_generation(
        self,
        concept: str,
        feature_id: UUID,
        feature_index: int,
        feature_strength: float,
        generated_prompt: str,
        image_url: str,
    ) -> UUID:
        """Save concept and generation data to Supabase."""
        # First, find or create concept
        concept_result = (
            self.supabase.table("concepts").select("id").eq("text", concept).execute()
        )

        if concept_result.data:
            concept_id = concept_result.data[0]["id"]
        else:
            concept_result = (
                self.supabase.table("concepts").insert({"text": concept}).execute()
            )
            concept_id = concept_result.data[0]["id"]

        # Download and save image
        response = requests.get(image_url, stream=True)
        image = Image.open(response.raw)

        # Create storage path
        storage_path = f"{concept_id}/{feature_id}_{feature_strength}.png"
        os.makedirs(f"images/{concept_id}", exist_ok=True)
        image.save(f"images/{storage_path}")

        # Upload to storage
        self.supabase.storage.from_("images").upload(
            storage_path,
            f"images/{storage_path}",
            {"upsert": "true", "content-type": "image/png"},
        )

        # Get public URL
        public_url = self.supabase.storage.from_("images").get_public_url(storage_path)

        # Save generation
        generation_data = {
            "concept_id": concept_id,
            "feature_id": feature_id,
            "feature_index": feature_index,
            "feature_strength": feature_strength,
            "generated_prompt": generated_prompt,
            "image_url": public_url,
        }

        result = self.supabase.table("generations").insert(generation_data).execute()
        return result.data[0]["id"]
