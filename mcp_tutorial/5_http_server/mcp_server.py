#!/usr/bin/env python3
import json
import random
from http.server import BaseHTTPRequestHandler, HTTPServer


class MCPHandler(BaseHTTPRequestHandler):
    def do_POST(self) -> None:
        if self.path != "/":
            self.send_response(404)
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
    server.serve_forever()


if __name__ == "__main__":
    main()
