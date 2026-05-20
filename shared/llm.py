"""LLM factory: real OpenAI or deterministic mock for offline demos."""

from __future__ import annotations

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_openai import ChatOpenAI

from functools import lru_cache

from shared.config import Settings


@lru_cache
def get_chat_model(settings: Settings) -> BaseChatModel:
    if settings.use_mock:
        from langchain_community.chat_models.fake import FakeListChatModel

        return FakeListChatModel(
            responses=[
                (
                    "Research notes:\n"
                    "- Enterprise AI assistant spend is growing quickly.\n"
                    "- Buyers require security review and IDE integration.\n"
                    "- Risks include IP leakage and uneven adoption."
                ),
                (
                    "## Market\nStrong enterprise demand with security-first buying.\n\n"
                    "## Competition\nCopilot, Cursor, and Q Developer lead mindshare.\n\n"
                    "## Risks\nIP, quality, and compliance gaps.\n\n"
                    "## Recommendation\nRun a 90-day pilot with PR-cycle metrics."
                ),
                "APPROVED",
            ]
        )

    return ChatOpenAI(
        model=settings.openai_model,
        api_key=settings.openai_api_key,
        temperature=0.2,
    )
