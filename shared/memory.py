"""Long-term memory: notes that outlive the chat.

Working memory is the message list for the current run. It dies when the
run ends. This file is the other kind. remember() writes a note, recall()
finds it on a later run that starts with no messages.
"""

from __future__ import annotations

import json
from pathlib import Path


def _tokens(text: str) -> set[str]:
    words = "".join(ch.lower() if ch.isalnum() else " " for ch in text).split()
    return {word for word in words if len(word) > 2}


class MemoryStore:
    def __init__(self, path: Path | None = None) -> None:
        self.path = path or Path(__file__).resolve().parents[1] / "data" / "memory.json"

    def remember(self, note: str) -> str:
        text = " ".join(note.split())
        if not text:
            return "Nothing to remember."
        notes = self._load()
        if text in notes:
            return f"Already remembered: {text}"
        notes.append(text)
        self._save(notes)
        return f"Remembered: {text}"

    def recall(self, query: str, limit: int = 3) -> str:
        # ponytail: keyword overlap, swap for embeddings when notes no longer fit one file
        notes = self._load()
        if not notes:
            return "No memories yet."
        wanted = _tokens(query)
        ranked = sorted(
            ((len(wanted & _tokens(note)), note) for note in notes),
            key=lambda item: item[0],
            reverse=True,
        )
        hits = [note for score, note in ranked if score > 0][:limit]
        if not hits:
            return "No memories matched. The query has to share words with the note."
        return "\n".join(hits)

    def clear(self) -> None:
        if self.path.exists():
            self.path.unlink()

    def _load(self) -> list[str]:
        if not self.path.exists():
            return []
        data = json.loads(self.path.read_text())
        if not isinstance(data, list) or not all(isinstance(item, str) for item in data):
            raise ValueError(f"Memory file must be a list of strings: {self.path}")
        return data

    def _save(self, notes: list[str]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(notes, indent=2) + "\n")


def _demo() -> None:
    import tempfile

    store = MemoryStore(Path(tempfile.mkdtemp()) / "memory.json")
    assert store.recall("hipaa") == "No memories yet."
    note = "For healthcare briefs, flag HIPAA and prefer on-prem."
    assert store.remember(note).startswith("Remembered:")
    assert store.remember(note).startswith("Already remembered:")
    assert "HIPAA" in store.recall("healthcare on-prem")
    assert store.recall("kubernetes pricing").startswith("No memories matched")
    assert store._load() == [note]
    store.clear()
    assert store.recall("healthcare") == "No memories yet."
    print("memory ok")


if __name__ == "__main__":
    _demo()
