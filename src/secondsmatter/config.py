"""Application settings, read from environment variables.

Locally they come from a `.env` file; on Streamlit Community Cloud from the
app's Secrets. To change the model, edit LLM_MODEL below.
"""

import os
from dataclasses import dataclass

from dotenv import load_dotenv

LLM_MODEL = "claude-opus-5-5"


@dataclass(frozen=True)
class Settings:
    llm_model: str
    has_api_key: bool


def get_settings(load_env_file: bool = True) -> Settings:
    """Build settings from the environment (optionally loading `.env` first)."""
    if load_env_file:
        load_dotenv()
    return Settings(
        llm_model=LLM_MODEL,
        has_api_key=bool(os.environ.get("ANTHROPIC_API_KEY", "").strip()),
    )
