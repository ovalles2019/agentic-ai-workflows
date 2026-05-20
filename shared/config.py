"""Environment and runtime configuration."""

from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    openai_api_key: str | None
    openai_model: str
    mock_llm: bool
    default_topic: str

    @property
    def use_mock(self) -> bool:
        return self.mock_llm or not self.openai_api_key


@lru_cache
def get_settings() -> Settings:
    mock = os.getenv("MOCK_LLM", "").lower() in {"1", "true", "yes"}
    return Settings(
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        openai_model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        mock_llm=mock,
        default_topic=os.getenv(
            "RESEARCH_TOPIC",
            "AI coding assistants for enterprise software teams",
        ),
    )
