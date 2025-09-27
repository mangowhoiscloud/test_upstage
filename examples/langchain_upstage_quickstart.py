"""LangChain helper script for exercising Upstage integrations.

This module demonstrates how to run chat, document parsing, and
information extraction flows with LangChain's Upstage integrations.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from langchain_upstage import (
    ChatUpstage,
    UpstageDocumentParseLoader,
    UpstageUniversalInformationExtraction,
)


def run_chat(question: str, model: str = "solar-mini", temperature: float | None = None) -> str:
    """Send a single-turn chat completion request."""
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "You are a helpful assistant that answers in Korean."),
            ("human", "{question}"),
        ]
    )
    llm = ChatUpstage(model=model, temperature=temperature)
    chain = prompt | llm | StrOutputParser()
    return chain.invoke({"question": question})


def run_document_parse(file_path: Path, split: str = "page", output_format: str = "markdown") -> Dict[str, Any]:
    """Parse a document and return structured JSON for inspection."""
    loader = UpstageDocumentParseLoader(
        file_path=file_path,
        split=split,
        output_format=output_format,
        coordinates=True,
    )
    docs = loader.load()
    # LangChain loaders return Document objects; convert to JSON-serializable form.
    return {
        "count": len(docs),
        "preview": [
            {
                "page": doc.metadata.get("page"),
                "source": doc.metadata.get("source"),
                "text": doc.page_content[:400],
            }
            for doc in docs[:3]
        ],
    }


def run_information_extraction(text: str, schema: Dict[str, Any]) -> Dict[str, Any]:
    """Call the universal information extraction model with a schema."""
    extractor = UpstageUniversalInformationExtraction()
    response = extractor.invoke({"input": text, "schema": schema})
    return response


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="LangChain + Upstage quickstart demos")
    subparsers = parser.add_subparsers(dest="command", required=True)

    chat_parser = subparsers.add_parser("chat", help="Run a single chat completion")
    chat_parser.add_argument("question", help="User question to send to the model")
    chat_parser.add_argument("--model", default="solar-mini", help="Upstage chat model alias")
    chat_parser.add_argument("--temperature", type=float, default=None, help="Sampling temperature")

    parse_parser = subparsers.add_parser("parse", help="Parse a document via Upstage Document Parse")
    parse_parser.add_argument("file", type=Path, help="Path to a PDF or image to upload")
    parse_parser.add_argument(
        "--split",
        choices=["none", "page", "element"],
        default="page",
        help="How to split the parsed output into LangChain documents",
    )
    parse_parser.add_argument(
        "--format",
        choices=["text", "html", "markdown"],
        default="markdown",
        help="Desired output format",
    )

    ie_parser = subparsers.add_parser("extract", help="Run the universal information extraction model")
    ie_parser.add_argument("text", help="Raw text to analyze")
    ie_parser.add_argument(
        "--schema",
        type=Path,
        required=True,
        help="Path to a JSON schema describing the fields to extract",
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.command == "chat":
        answer = run_chat(args.question, model=args.model, temperature=args.temperature)
        print(answer)
    elif args.command == "parse":
        result = run_document_parse(args.file, split=args.split, output_format=args.format)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.command == "extract":
        schema = json.loads(args.schema.read_text(encoding="utf-8"))
        result = run_information_extraction(args.text, schema)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        raise ValueError(f"Unknown command: {args.command}")


if __name__ == "__main__":
    main()
