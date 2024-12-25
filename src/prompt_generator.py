from typing import Dict, List
from textwrap import dedent
import goodfire
import logging

logger = logging.getLogger(__name__)


def get_prompt_template(topic: str) -> List[Dict[str, str]]:
    """Get the prompt template for text generation."""
    return [
        {
            "role": "user",
            "content": dedent(f"""Design a prompt for the following: "{topic}"
        Do not generate anything else."""),
        }
    ]


def generate_prompt(
    goodfire_client: goodfire.Client,
    variant: goodfire.Variant,
    features: List[goodfire.Feature],
    prompt: List[Dict[str, str]],
    strength: float,
) -> str:
    """Generate a single prompt with the given feature strength."""
    logger.info(
        f"Prompt: {prompt[0]['content']} | Features: {features} | Strength: {strength}"
    )
    for feature in features:
        variant.set(feature, strength)

    response = goodfire_client.chat.completions.create(
        messages=prompt,
        model=variant,
        seed=42,
        max_completion_tokens=2048,
        temperature=0,
    )

    generated_prompt = response.choices[0].message["content"]
    logger.info(f"Generated prompt: {generated_prompt}")

    return generated_prompt
