"""Simple proxy server to forward requests to Upstage APIs.

This script exposes minimal HTTP endpoints that forward requests to
Upstage's public APIs. The proxy allows local testing without exposing
API keys to client-side code. Configure the `UPSTAGE_API_KEY`
environment variable before running the server.
"""
from __future__ import annotations

import json
import os
import threading
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any, Dict, Optional
from urllib import request, error


UPSTAGE_CHAT_URL = "https://api.upstage.ai/v1/chat/completions"
UPSTAGE_OCR_URL = "https://api.upstage.ai/v1/document-digitization"
UPSTAGE_EXTRACTION_URL = "https://api.upstage.ai/v1/information-extraction"


class UpstageProxyHandler(BaseHTTPRequestHandler):
    """HTTP handler that proxies requests to Upstage services."""

    server_version = "UpstageProxy/0.1"

    def _get_api_key(self) -> Optional[str]:
        return os.getenv("UPSTAGE_API_KEY")

    # BaseHTTPRequestHandler override requires camelCase names
    def do_POST(self) -> None:  # noqa: N802 - pylint: disable=invalid-name
        api_key = self._get_api_key()
        if not api_key:
            self._send_json({"error": "UPSTAGE_API_KEY is not set"}, HTTPStatus.INTERNAL_SERVER_ERROR)
            return

        content_length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(content_length) if content_length else b"{}"
        payload: Dict[str, Any]
        try:
            payload = json.loads(body.decode("utf-8"))
        except json.JSONDecodeError as exc:  # pragma: no cover - defensive
            self._send_json({"error": f"Invalid JSON payload: {exc}"}, HTTPStatus.BAD_REQUEST)
            return

        if self.path == "/chat":
            upstream_url = UPSTAGE_CHAT_URL
        elif self.path == "/ocr":
            upstream_url = UPSTAGE_OCR_URL
        elif self.path == "/extraction":
            upstream_url = UPSTAGE_EXTRACTION_URL
        else:
            self._send_json({"error": f"Unsupported path: {self.path}"}, HTTPStatus.NOT_FOUND)
            return

        try:
            response = self._forward_request(upstream_url, api_key, payload)
        except error.HTTPError as exc:
            body_bytes = exc.read()
            message = body_bytes.decode("utf-8", errors="replace") if body_bytes else exc.reason
            self._send_json({"status": exc.code, "error": message}, HTTPStatus.BAD_GATEWAY)
            return
        except error.URLError as exc:  # pragma: no cover - network failure
            self._send_json({"error": str(exc.reason)}, HTTPStatus.BAD_GATEWAY)
            return

        self._send_json(response, HTTPStatus.OK)

    def do_GET(self) -> None:  # noqa: N802 - pylint: disable=invalid-name
        """Provide a small health-check endpoint."""
        if self.path != "/healthz":
            self._send_json({"error": f"Unsupported path: {self.path}"}, HTTPStatus.NOT_FOUND)
            return
        self._send_json({"status": "ok"}, HTTPStatus.OK)

    def log_message(self, format: str, *args: Any) -> None:  # noqa: A003 - signature fixed
        # Reduce console noise during automated tests
        thread_name = threading.current_thread().name
        message = f"[{thread_name}] {self.address_string()} - {format % args}"
        print(message)

    def _forward_request(self, url: str, api_key: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        req = request.Request(url, method="POST")
        req.add_header("Content-Type", "application/json")
        req.add_header("Authorization", f"Bearer {api_key}")
        data = json.dumps(payload).encode("utf-8")
        with request.urlopen(req, data=data, timeout=30) as response:  # noqa: S310 - upstream HTTPS call
            response_bytes = response.read()
        return json.loads(response_bytes.decode("utf-8")) if response_bytes else {}

    def _send_json(self, payload: Dict[str, Any], status: HTTPStatus) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status.value)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def run(host: str = "0.0.0.0", port: int = 8080) -> None:
    server = HTTPServer((host, port), UpstageProxyHandler)
    print(f"Starting Upstage proxy on http://{host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:  # pragma: no cover - manual shutdown
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    run()
