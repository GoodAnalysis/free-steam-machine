#!/usr/bin/env python3
"""bigpicture_server - open Steam Big Picture on this PC from a LAN request.

Companion to controller_bigpicture.py for the iOS "remote" use case: run this on
the PC, then have an iPhone Shortcut hit http://<pc-ip>:8765/bigpicture to open
Big Picture on the PC. See ios/README.md for the iPhone side.

Windows only (uses os.startfile for the steam:// handler). LAN use only - there
is no real authentication beyond an optional shared token.
"""

from __future__ import annotations

import argparse
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

STEAM_BIGPICTURE_URL = "steam://open/bigpicture"
DEFAULT_PORT = 8765


def launch_big_picture() -> None:
    # os.startfile uses ShellExecute, which respects the steam:// protocol handler.
    os.startfile(STEAM_BIGPICTURE_URL)


def make_handler(token: "str | None"):
    class Handler(BaseHTTPRequestHandler):
        # Stay quiet by default; remove this to log every request.
        def log_message(self, *args):
            pass

        def _send(self, code: int, body: str) -> None:
            payload = body.encode("utf-8")
            self.send_response(code)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)

        def do_GET(self) -> None:
            parsed = urlparse(self.path)
            if parsed.path.rstrip("/") not in ("/bigpicture", "/big-picture"):
                self._send(404, "not found - try /bigpicture\n")
                return
            if token is not None:
                supplied = parse_qs(parsed.query).get("token", [None])[0]
                if supplied != token:
                    self._send(403, "bad or missing token\n")
                    return
            try:
                launch_big_picture()
            except OSError as exc:
                self._send(500, f"failed: {exc}\n")
                return
            self._send(200, "opening Big Picture\n")

    return Handler


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Open Steam Big Picture on this PC from a LAN request."
    )
    parser.add_argument(
        "--port", type=int, default=DEFAULT_PORT,
        help=f"port to listen on (default {DEFAULT_PORT})",
    )
    parser.add_argument(
        "--host", default="0.0.0.0",
        help="address to bind (default all interfaces)",
    )
    parser.add_argument(
        "--token", default=None,
        help="optional shared secret; requests must pass ?token=...",
    )
    args = parser.parse_args()

    server = ThreadingHTTPServer((args.host, args.port), make_handler(args.token))
    where = f"http://{args.host}:{args.port}/bigpicture"
    if args.token:
        where += "?token=..."
    print(f"listening on {where}  (Ctrl+C to stop)", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nstopping", flush=True)
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
