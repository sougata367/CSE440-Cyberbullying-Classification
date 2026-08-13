import json
from http.server import BaseHTTPRequestHandler

from backend.config import HF_PROVIDER, MODEL_ID


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        payload = {
            "status": "ok",
            "service": "CyberShield AI API",
            "model_configured": bool(MODEL_ID),
            "model_id": MODEL_ID or None,
            "provider": HF_PROVIDER,
        }

        body = json.dumps(payload).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)
