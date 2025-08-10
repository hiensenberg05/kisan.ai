import logging
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime


logger = logging.getLogger(__name__)


@dataclass
class Message:
    role: str  # 'user' or 'assistant'
    content: str
    timestamp: str


class ConversationMemory:
    """In-memory conversation store keyed by session_id.

    Keeps the last N exchanges to provide short-term memory across requests.
    """

    def __init__(self, max_messages: int = 20):
        self._store: Dict[str, List[Message]] = {}
        self.max_messages = max_messages

    def get_history(self, session_id: str) -> List[Dict[str, str]]:
        messages = self._store.get(session_id, [])
        # Return as list of dicts for easier serialization/use in prompts
        return [
            {"role": m.role, "content": m.content, "timestamp": m.timestamp}
            for m in messages[-self.max_messages :]
        ]

    def add_exchange(self, session_id: str, user_text: str, assistant_text: str) -> None:
        ts = datetime.utcnow().isoformat()
        convo = self._store.setdefault(session_id, [])
        convo.append(Message(role="user", content=user_text, timestamp=ts))
        convo.append(Message(role="assistant", content=assistant_text, timestamp=ts))
        # Trim
        if len(convo) > self.max_messages:
            self._store[session_id] = convo[-self.max_messages :]

    def reset(self, session_id: str) -> None:
        if session_id in self._store:
            del self._store[session_id]

    @staticmethod
    def format_history_for_context(history: List[Dict[str, str]], max_chars: int = 2000) -> str:
        """Format history into a compact context string for prompts."""
        if not history:
            return ""
        lines: List[str] = []
        for m in history[-20:]:
            prefix = "User:" if m.get("role") == "user" else "Assistant:"
            content = (m.get("content") or "").strip()
            if content:
                lines.append(f"{prefix} {content}")
        context = "\n".join(lines)
        if len(context) > max_chars:
            context = context[-max_chars:]
        return context



