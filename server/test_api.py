"""Client helper to test the local Upstage proxy server."""
from __future__ import annotations

import argparse
import json
import os
import sys
import mimetypes
import pathlib
import uuid
from typing import Any, Dict, Tuple
from urllib import error, request


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Send a test request to the Upstage proxy")
    parser.add_argument("--host", default="127.0.0.1", help="Proxy host (default: %(default)s)")
    parser.add_argument("--port", type=int, default=8080, help="Proxy port (default: %(default)d)")
    parser.add_argument("--endpoint", choices=["chat", "ocr", "extraction"], default="chat")
    parser.add_argument("--message", default="Ping", help="Message to send for chat testing")
    parser.add_argument(
        "--payload",
        help="Optional raw JSON payload. Overrides --message for chat endpoint.",
    )
    parser.add_argument(
        "--file",
        default=pathlib.Path("sample/documents/irs-form-w9.pdf"),
        type=pathlib.Path,
        help=(
            "Document path for OCR tests in direct mode. Download the IRS W-9 sample with "
            "`curl -L -o sample/documents/irs-form-w9.pdf https://www.irs.gov/pub/irs-pdf/fw9.pdf` "
            "before running or provide your own file."
        ),
    )
    parser.add_argument(
        "--output-format",
        default="markdown",
        help="Desired output format for OCR direct calls (default: %(default)s).",
    )
    parser.add_argument(
        "--mode",
        choices=["proxy", "direct"],
        default="proxy",
        help="Send the request to the local proxy or directly to Upstage's public API.",
    )
    parser.add_argument(
        "--api-key",
        help="Explicit Upstage API key for direct mode. Defaults to UPSTAGE_API_KEY env var.",
    )
    return parser.parse_args()


def build_payload(args: argparse.Namespace) -> Dict[str, Any]:
    if args.payload:
        return json.loads(args.payload)

    if args.endpoint == "chat":
        return {
            "model": "solar-1-mini-chat",
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": args.message},
            ],
        }

    if args.endpoint == "ocr":
        payload: Dict[str, Any] = {"model": "document-parse"}
        if args.mode == "proxy":
            payload.update(
                {
                    "task": "document_digitization",
                    "file_url": "https://example.com/sample.pdf",
                }
            )
        return payload

    return {
        "task": "information_extraction",
        "document_text": "Invoice #1234, Total: $56.00",
    }


def encode_multipart(
    fields: Dict[str, str], files: Dict[str, pathlib.Path]
) -> Tuple[bytes, str]:
    boundary = uuid.uuid4().hex
    body: list[bytes] = []

    for name, value in fields.items():
        body.append(f"--{boundary}\r\n".encode("utf-8"))
        body.append(
            f"Content-Disposition: form-data; name=\"{name}\"\r\n\r\n{value}\r\n".encode(
                "utf-8"
            )
        )

    for name, path in files.items():
        file_path = path.expanduser()
        if not file_path.is_file():
            raise FileNotFoundError(f"File not found: {file_path}")
        filename = file_path.name
        mime_type, _ = mimetypes.guess_type(filename)
        mime_type = mime_type or "application/octet-stream"
        body.append(f"--{boundary}\r\n".encode("utf-8"))
        body.append(
            (
                f"Content-Disposition: form-data; name=\"{name}\"; filename=\"{filename}\"\r\n"
                f"Content-Type: {mime_type}\r\n\r\n"
            ).encode("utf-8")
        )
        body.append(file_path.read_bytes())
        body.append(b"\r\n")

    body.append(f"--{boundary}--\r\n".encode("utf-8"))
    return b"".join(body), f"multipart/form-data; boundary={boundary}"


def main() -> int:
    args = parse_args()
    payload = build_payload(args)

    if args.mode == "proxy":
        url = f"http://{args.host}:{args.port}/{args.endpoint}"
        req = request.Request(url, method="POST")
    else:
        upstream_urls = {
            "chat": "https://api.upstage.ai/v1/agents/chats",
            "ocr": "https://api.upstage.ai/v1/document-digitization",
            "extraction": "https://api.upstage.ai/v1/information-extraction",
        }
        url = upstream_urls[args.endpoint]
        req = request.Request(url, method="POST")
        api_key = args.api_key or os.getenv("UPSTAGE_API_KEY")
        if not api_key:
            print("Direct mode requires an API key via --api-key or UPSTAGE_API_KEY.")
            return 2
        req.add_header("Authorization", f"Bearer {api_key}")

    if args.mode == "direct" and args.endpoint == "ocr":
        fields = {"model": payload.get("model", "document-parse")}
        if output_format := args.output_format:
            fields["output_format"] = output_format
        try:
            data, content_type = encode_multipart(fields, {"document": args.file})
        except FileNotFoundError as exc:
            print(exc)
            return 3
        req.add_header("Content-Type", content_type)
    else:
        req.add_header("Content-Type", "application/json")
        data = json.dumps(payload).encode("utf-8")

    try:
        with request.urlopen(req, data=data, timeout=60) as response:
            body = response.read().decode("utf-8")
            print(body)
    except error.HTTPError as exc:
        error_body = exc.read().decode("utf-8", errors="replace")
        print(f"HTTP error {exc.code}: {error_body}")
        return exc.code
    except error.URLError as exc:
        print(f"Network error: {exc.reason}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
