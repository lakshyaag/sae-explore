import streamlit as st
from supabase import create_client
import os
from dotenv import load_dotenv
from typing import List, Tuple
from uuid import UUID
import pandas as pd

st.set_page_config(layout="wide", page_title="SAE Explorer")

# Load environment variables
load_dotenv()

# Initialize Supabase client
supabase = create_client(
    os.getenv("SUPABASE_URL", ""), os.getenv("SUPABASE_SERVICE_KEY", "")
)


def get_concepts() -> List[Tuple[UUID, str]]:
    """Get all unique concepts from the database."""
    result = supabase.table("concepts").select("*").execute()
    return [(row["id"], row["text"]) for row in result.data]


def get_features_for_concept(concept_id: UUID) -> List[Tuple[UUID, str, List[str]]]:
    """Get all features used with a concept."""
    result = (
        supabase.table("generations")
        .select("features(id, input_text, discovered_features)")
        .eq("concept_id", concept_id)
        .execute()
    )
    # Get unique features with their discovered features
    features = {
        row["features"]["id"]: (
            row["features"]["input_text"],
            row["features"]["discovered_features"],
        )
        for row in result.data
    }
    return [(id, text, disc) for id, (text, disc) in features.items()]


def get_generations(concept_id: UUID, feature_id: UUID) -> pd.DataFrame:
    """Get all generations for a concept-feature pair."""
    result = (
        supabase.table("generations")
        .select("*")
        .eq("concept_id", concept_id)
        .eq("feature_id", feature_id)
        .order("feature_strength")
        .execute()
    )
    return pd.DataFrame(result.data)


# App title
st.title("AI Generated Concepts Explorer")

# Sidebar for concept and feature selection

# Get and display concepts
concepts = get_concepts()
selected_concept_id = st.selectbox(
    "Select Concept",
    options=[c[0] for c in concepts],
    format_func=lambda x: next(c[1] for c in concepts if c[0] == x),
    key="concept",
)

if selected_concept_id:
    # Get and display features for selected concept
    features = get_features_for_concept(selected_concept_id)
    selected_feature_id = st.selectbox(
        "Select Feature Input",
        options=[f[0] for f in features],
        format_func=lambda x: next(f[1] for f in features if f[0] == x),
        key="feature",
    )


# Main content area
if selected_concept_id and selected_feature_id:
    # Get generations for selected concept and feature
    generations_df = get_generations(selected_concept_id, selected_feature_id)

    if not generations_df.empty:
        # Filter generations by number of features used
        # generations_df = generations_df[generations_df["feature_index"] < num_features]

        # Create strength slider
        min_strength = float(generations_df["feature_strength"].min())
        max_strength = float(generations_df["feature_strength"].max())
        selected_strength = st.slider(
            "Feature Strength",
            min_value=min_strength,
            max_value=max_strength,
            value=0.0,
            step=(max_strength - min_strength) / (len(generations_df) - 1),
        )

        # Find closest generation to selected strength
        closest_generation = generations_df.iloc[
            (generations_df["feature_strength"] - selected_strength).abs().argsort()[:1]
        ].iloc[0]

        # Display generation details
        col1, col2 = st.columns([2, 1])

        with col1:
            st.image(
                closest_generation["image_url"],
                caption=f"Strength: {closest_generation['feature_strength']:.2f}",
                use_container_width=True,
            )

        with col2:
            num_features = closest_generation["feature_index"] + 1
            st.text_area(
                "Generated Prompt",
                closest_generation["generated_prompt"],
                height=200,
                disabled=True,
            )

            # Add metadata
            st.markdown("### Metadata")
            discovered_features = next(
                f[2] for f in features if f[0] == selected_feature_id
            )

            # Display selected features
            st.markdown("### Selected Features")
            for i, feature in enumerate(discovered_features[:num_features]):
                st.text(f"{i+1}. {feature['label']}")

            st.write(f"Generation ID: {closest_generation['id']}")
            st.write(f"Created: {closest_generation['created_at']}")
    else:
        st.warning("No generations found for this concept-feature combination.")
else:
    st.info("Please select a concept and feature from the sidebar.")

# Footer
st.markdown("---")
st.markdown("[X (@lakshyaag)](https://x.com/lakshyaag)")
st.markdown(
    "Built with Streamlit • Data from Supabase • "
    "Images generated with Fal.ai • Features by Goodfire"
)
