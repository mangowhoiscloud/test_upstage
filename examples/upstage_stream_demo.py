"""Streaming demo for Upstage's solar-pro2 chat model."""
from __future__ import annotations

import os
from dataclasses import dataclass

from openai import OpenAI


@dataclass
class ChatConfig:
    model: str = "solar-pro2"
    base_url: str = "https://api.upstage.ai/v1"
    system_prompt: str = "You are a cheerful assistant."
    user_prompt: str = "Hi, how are you?"
    reasoning_effort: str = "high"


def stream_chat(config: ChatConfig) -> None:
    api_key = os.getenv("UPSTAGE_API_KEY")
    if not api_key:
        raise RuntimeError("Set the UPSTAGE_API_KEY environment variable before running the demo.")

    client = OpenAI(api_key=api_key, base_url=config.base_url)

    stream = client.chat.completions.create(
        model=config.model,
        messages=[
            {"role": "system", "content": config.system_prompt},
            {"role": "user", "content": config.user_prompt},
        ],
        reasoning_effort=config.reasoning_effort,
        stream=True,
    )

    print("Streaming response:\n")
    for chunk in stream:
        delta = chunk.choices[0].delta
        if delta.content:
            print(delta.content, end="", flush=True)
    print()


if __name__ == "__main__":
    stream_chat(ChatConfig())
