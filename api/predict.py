import json
from http.server import BaseHTTPRequestHandler

from backend.config import MAX_INPUT_CHARS, MIN_INPUT_CHARS
from backend.inference import ModelConfigurationError, classify_text


class handler(BaseHTTPRequestHandler):
    def _send_json(self, status_code, payload):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Allow", "POST, OPTIONS")
        self.end_headers()

    def do_POST(self):
        try:
            content_length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            content_length = 0

        if content_length <= 0:
            self._send_json(400, {"detail": "Request body is required."})
            return

        try:
            payload = json.loads(self.rfile.read(content_length).decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            self._send_json(400, {"detail": "Request body must be valid JSON."})
            return

        text = str(payload.get("text", "")).strip()

        if len(text) < MIN_INPUT_CHARS:
            self._send_json(
                422,
                {"detail": f"Text must contain at least {MIN_INPUT_CHARS} characters."},
            )
            return

        if len(text) > MAX_INPUT_CHARS:
            self._send_json(
                422,
                {"detail": f"Text must be no longer than {MAX_INPUT_CHARS} characters."},
            )
            return

        try:
            result = classify_text(text)
            self._send_json(200, result)
        except ModelConfigurationError as exc:
            self._send_json(503, {"detail": str(exc)})
        except Exception as exc:
            self._send_json(
                502,
                {
                    "detail": "The model inference request failed.",
                    "error_type": exc.__class__.__name__,
                },
            )
