from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import unquote

from repository import get_identity_access, get_routes

HOST = "127.0.0.1"
PORT = 8001


class IGARequestHandler(BaseHTTPRequestHandler):
    def _send_json(self, status_code: int, payload: object) -> None:
        response = json.dumps(payload, indent=2).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(response)))
        self.end_headers()
        self.wfile.write(response)

    def do_GET(self) -> None:  # noqa: N802 - BaseHTTPRequestHandler uses this name
        path = unquote(self.path.split("?", 1)[0])
        routes = get_routes()

        if path in routes:
            self._send_json(200, routes[path])
            return

        identity_prefix = "/governance/identity/"
        identity_suffix = "/access"
        if path.startswith(identity_prefix) and path.endswith(identity_suffix):
            identity_id = path.removeprefix(identity_prefix).removesuffix(identity_suffix)
            payload = get_identity_access(identity_id)
            if payload is None:
                self._send_json(404, {"error": "identity_not_found", "identity_id": identity_id})
                return
            self._send_json(200, payload)
            return

        self._send_json(
            404,
            {
                "error": "route_not_found",
                "path": path,
                "available_routes": sorted(routes.keys())
                + ["/governance/identity/{identity_id}/access"],
            },
        )

    def log_message(self, format: str, *args: object) -> None:
        # Keep local development output simple and deterministic.
        print(f"iga-service {self.address_string()} - {format % args}")


def run_server(host: str = HOST, port: int = PORT) -> None:
    server = HTTPServer((host, port), IGARequestHandler)
    print(f"iga-service read-only API running at http://{host}:{port}")
    print("Press Ctrl+C to stop.")
    server.serve_forever()


if __name__ == "__main__":
    run_server()
