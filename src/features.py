from typing import Tuple, List
from uuid import UUID
import goodfire
from supabase import Client


class FeatureManager:
    def __init__(self, goodfire_client: goodfire.Client, supabase: Client):
        self.goodfire_client = goodfire_client
        self.supabase = supabase

    def find_or_create_feature(
        self, feature_input: str
    ) -> Tuple[UUID, goodfire.Feature, goodfire.Variant]:
        """Find existing feature or create new one."""
        variant = goodfire.Variant("meta-llama/Llama-3.3-70B-Instruct")

        # Check if feature exists
        result = (
            self.supabase.table("features")
            .select("*")
            .eq("input_text", feature_input)
            .execute()
        )

        if result.data:
            feature_id = result.data[0]["id"]
            discovered_features = result.data[0]["discovered_features"]
            selected_feature = goodfire.Feature.from_json(discovered_features[0])
        else:
            features = self.goodfire_client.features.search(
                feature_input, model=variant, top_k=5
            )

            # Save to database
            feature_data = {
                "input_text": feature_input,
                "discovered_features": [f.json() for f in features],
            }
            result = self.supabase.table("features").insert(feature_data).execute()

            feature_id = result.data[0]["id"]
            selected_feature = features[0]

        return feature_id, selected_feature, variant

    def get_discovered_features(self, feature_id: UUID) -> List[str]:
        """Get all discovered features for a feature input."""
        result = (
            self.supabase.table("features")
            .select("discovered_features")
            .eq("id", feature_id)
            .execute()
        )
        return result.data[0]["discovered_features"]
