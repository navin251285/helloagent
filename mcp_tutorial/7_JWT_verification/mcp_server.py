#!/usr/bin/env python3
import base64
import hashlib
import hmac
import json
import random
from http.server import BaseHTTPRequestHandler, HTTPServer


JWT_SECRET = "demo-secret"


def base64url_decode(data: str) -> bytes:
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + padding)


def verify_jwt(token: str) -> bool:
    parts = token.split(".")
    if len(parts) != 3:
        return False

    header_b64, payload_b64, sig_b64 = parts
    try:
        header = json.loads(base64url_decode(header_b64))
    except (ValueError, json.JSONDecodeError):
        return False

    if header.get("alg") != "HS256":
        return False

    signing_input = f"{header_b64}.{payload_b64}".encode("utf-8")
    expected_sig = hmac.new(JWT_SECRET.encode("utf-8"), signing_input, hashlib.sha256).digest()
    expected_b64 = base64.urlsafe_b64encode(expected_sig).decode("utf-8").rstrip("=")
    return hmac.compare_digest(expected_b64, sig_b64)


class MCPHandler(BaseHTTPRequestHandler):
    def do_POST(self) -> None:
        if self.path != "/":
            self.send_response(404)
            self.end_headers()
            return

        auth = self.headers.get("Authorization", "")
        if not auth.startswith("Bearer "):
            self.send_response(401)
            self.end_headers()
            return

        token = auth.split(" ", 1)[1]
        if not verify_jwt(token):
            self.send_response(401)
            self.end_headers()
            return

        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length).decode("utf-8")
        request = json.loads(raw) if raw else {}

        method = request.get("method", "")
        if method == "random_op":
            params = request.get("params", {})
            number = int(params.get("number", 0))
            rand_num = random.randint(1, 5)
            op = random.choice(["+", "-"])
            value = number + rand_num if op == "+" else number - rand_num
            response = {
                "jsonrpc": "2.0",
                "id": request.get("id", 1),
                "result": {
                    "input": number,
                    "operation": op,
                    "random": rand_num,
                    "value": value,
                },
            }
        else:
            response = {
                "jsonrpc": "2.0",
                "id": request.get("id", 1),
                "error": {"code": -32601, "message": "Method not found"},
            }

        body = json.dumps(response).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def main() -> None:
    server = HTTPServer(("127.0.0.1", 3000), MCPHandler)
    print("HTTP MCP server listening on http://127.0.0.1:3000")
    print("JWT secret: demo-secret")
    server.serve_forever()


if __name__ == "__main__":
    main()
