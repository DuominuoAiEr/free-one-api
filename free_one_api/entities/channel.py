import json

import tiktoken

from ..models.adapter import llm
from ..models import adapter


class Channel:
    """Entity for channel."""
    id: int

    name: str
    """Name of this channel."""

    adapter: llm.LLMLibAdapter

    model_mapping: dict
    """Mapping model name to another model name."""

    enabled: bool

    latency: int

    def __init__(self, id: int, name: str, adapter: llm.LLMLibAdapter, model_mapping: dict, enabled: bool, latency: int):
        self.id = id
        self.name = name
        self.adapter = adapter
        self.model_mapping = model_mapping
        self.enabled = enabled
        self.latency = latency

    @classmethod
    def dump_channel(cls, chan: 'Channel') -> dict:
        return {
            "id": chan.id,
            "name": chan.name,
            "adapter": adapter.dump_adapter(chan.adapter),
            "model_mapping": chan.model_mapping,
            "enabled": chan.enabled,
            "latency": chan.latency,
        }

    @classmethod
    def load_channel(cls, data: dict) -> 'Channel':
        return cls(
            data["id"],
            data["name"],
            adapter.load_adapter(data["adapter"]),
            data["model_mapping"],
            data["enabled"],
            data["latency"],
        )

    def count_tokens(
        self,
        model: str,
        messages: list[str],
    ) -> int:
        """Count message tokens."""
        try:
            encoding = tiktoken.encoding_for_model(model)
        except KeyError:
            encoding = tiktoken.get_encoding("cl100k_base")
        num_tokens = 0
        for message in messages:
            for key, value in message.items():
                num_tokens += len(encoding.encode(value))
        num_tokens += 3  # every reply is primed with <|start|>assistant<|message|>
        return num_tokens
