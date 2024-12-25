import logging

import goodfire
import numpy as np
import typer
from rich.console import Console
from rich.progress import (
    Progress,
    SpinnerColumn,
    TextColumn,
    BarColumn,
    TaskProgressColumn,
)

from src.config import load_config
from src.clients import init_goodfire, init_supabase, generate_image
from src.prompt_generator import get_prompt_template, generate_prompt
from src.features import FeatureManager
from src.storage import StorageManager
from uuid import UUID


app = typer.Typer(help="Generate and store AI-enhanced prompts and images")
console = Console()
logger = logging.getLogger(__name__)


def setup_logging(level: str) -> None:
    """Setup logging configuration."""
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.FileHandler("app.log"), logging.StreamHandler()],
    )


def generate_and_save(
    goodfire_client: goodfire.Client,
    feature_manager: FeatureManager,
    storage_manager: StorageManager,
    concept: str,
    feature_input: str,
    strength: float,
    progress: Progress,
    feature_index: int = 0,
) -> UUID:
    """Generate a prompt and image, then save both."""
    # Get or create feature
    task = progress.add_task("Finding/creating feature...", total=None)
    feature_id, feature, variant = feature_manager.find_or_create_feature(feature_input)
    progress.remove_task(task)

    # Get all discovered features
    all_features = feature_manager.get_discovered_features(feature_id)
    logger.debug(f"Discovered features: {all_features}")

    # Generate prompt
    task = progress.add_task("Generating prompt...", total=None)
    prompt_template = get_prompt_template(concept)
    generated_prompt = generate_prompt(
        goodfire_client, variant, feature, prompt_template, strength
    )
    progress.remove_task(task)
    logger.debug(f"Generated prompt: {generated_prompt}")

    # Generate image
    task = progress.add_task("Generating image...", total=None)
    image_result = generate_image(generated_prompt)
    if not image_result:
        raise RuntimeError("Failed to generate image")
    progress.remove_task(task)

    image_url = image_result["images"][0]["url"]
    logger.debug(f"Generated image URL: {image_url}")

    # Save everything
    task = progress.add_task("Saving to database...", total=None)
    generation_id = storage_manager.save_concept_and_generation(
        concept=concept,
        feature_id=feature_id,
        feature_index=feature_index,
        feature_strength=strength,
        generated_prompt=generated_prompt,
        image_url=image_url,
    )
    progress.remove_task(task)

    return generation_id


@app.command()
def generate(
    concept: str = typer.Argument(..., help="The concept to generate images for"),
    feature: str = typer.Argument(..., help="The feature to apply to the concept"),
    num_variations: int = typer.Option(
        1, "--variations", "-n", help="Number of strength variations to generate"
    ),
    min_strength: float = typer.Option(
        -0.5, "--min-strength", help="Minimum feature strength"
    ),
    max_strength: float = typer.Option(
        0.5, "--max-strength", help="Maximum feature strength"
    ),
    feature_index: int = typer.Option(
        0, "--feature-index", "-i", help="Index of the feature to use (0-4)"
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose output"
    ),
) -> None:
    """Generate images for a concept with varying feature strengths."""
    if not -0.5 <= min_strength <= max_strength <= 0.5:
        raise typer.BadParameter("Strength must be between -0.5 and 0.5")

    if not 0 <= feature_index <= 4:
        raise typer.BadParameter("Feature index must be between 0 and 4")

    # Load configuration
    config = load_config()
    setup_logging("DEBUG" if verbose else "WARNING")

    # Initialize clients
    goodfire_client = init_goodfire(config)
    supabase_client = init_supabase(config)

    # Initialize managers
    feature_manager = FeatureManager(goodfire_client, supabase_client)
    storage_manager = StorageManager(supabase_client)

    # Generate prompts and images for different strengths
    strengths = np.linspace(min_strength, max_strength, num_variations)

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console,
    ) as progress:
        overall_task = progress.add_task(
            "[cyan]Overall progress...", total=len(strengths)
        )

        for strength in strengths:
            progress.update(
                overall_task, description=f"[cyan]Processing strength {strength:.2f}"
            )
            generation_id = generate_and_save(
                goodfire_client,
                feature_manager,
                storage_manager,
                concept,
                feature,
                float(strength),
                progress,
                feature_index,
            )
            if verbose:
                console.print(
                    f"[green]Generated and saved with ID:[/green] {generation_id}"
                )
            progress.advance(overall_task)


@app.command()
def list_features(
    feature_input: str = typer.Argument(..., help="The feature input to look up"),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose output"
    ),
) -> None:
    """List all discovered features for a given input."""
    # Load configuration and initialize clients
    config = load_config()
    setup_logging("DEBUG" if verbose else "WARNING")

    supabase_client = init_supabase(config)
    goodfire_client = init_goodfire(config)

    # Initialize feature manager
    feature_manager = FeatureManager(goodfire_client, supabase_client)

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Looking up features...", total=None)
        feature_id, _, _ = feature_manager.find_or_create_feature(feature_input)
        features = feature_manager.get_discovered_features(feature_id)
        progress.remove_task(task)

        if verbose:
            console.print("\n[bold]Discovered features:[/bold]")
        for i, feature in enumerate(features):
            console.print(f"{i}: {feature}")


if __name__ == "__main__":
    app()