"""
Working memory vs long-term memory.

Working memory is the message list for this run. A new session starts empty.
Long-term memory is a JSON file. remember() writes it, recall() reads it
back after the messages are gone.

Run: python -m examples.05_agent_memory
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from shared.config import get_settings
from shared.memory import MemoryStore
from shared.tools import get_memory_tools, search_market_intel


def _brief(topic: str, remembered: str | None) -> str:
    intel = search_market_intel.invoke({"query": topic}).splitlines()[0]
    lines = [f"# Research Brief: {topic}", "", "## Market", intel]
    if remembered:
        lines.extend(["", "## Constraint from an earlier session", remembered])
    return "\n".join(lines)


def run(topic: str | None = None) -> str:
    settings = get_settings()
    topic = topic or settings.default_topic
    store = MemoryStore(ROOT / "data" / "demo_memory.json")
    store.clear()
    remember, recall = get_memory_tools(store)
    note = f"For {topic}: flag IP leakage and prefer on-prem before any rollout."

    print(f"\n=== Agent memory | mock={settings.use_mock} ===")
    print("Working memory is the chat. Long-term memory is data/demo_memory.json.\n")

    working = [f"user: {note}"]
    print("Session 1")
    print(f"  messages: {working}")
    print(f"  {remember.invoke({'note': note})}")

    working = []
    print("\nSession 2 — new chat, message list discarded")
    print(f"  messages: {working}")
    missed = _brief(topic, None)
    found = recall.invoke({"query": topic})
    kept = _brief(topic, None if found.startswith("No memories") else found)

    print("\n--- brief with empty chat and no recall ---")
    print(missed)
    print("\n--- same empty chat after recall(topic) ---")
    print(kept)
    print(
        "\nrecall hit because the saved note contains the topic words."
        "\nThis store matches keywords. It does not understand synonyms."
    )
    assert "prefer on-prem" in kept
    assert "prefer on-prem" not in missed
    return kept


if __name__ == "__main__":
    run()
