"""Serve Prometheus textfiles from a directory (eval harness exports)."""

from __future__ import annotations

import argparse
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path


def _combine(directory: Path) -> bytes:
    parts: list[bytes] = []
    for path in sorted(directory.glob("*.prom")):
        parts.append(f"# SOURCE {path.name}\n".encode())
        parts.append(path.read_bytes())
        if not parts[-1].endswith(b"\n"):
            parts.append(b"\n")
    if not parts:
        parts.append(b"# no eval metrics yet - run scripts/export_eval_metrics.py\n")
    return b"".join(parts)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dir", default="/textfile")
    parser.add_argument("--port", type=int, default=9101)
    parser.add_argument("--host", default="0.0.0.0")
    args = parser.parse_args()
    directory = Path(args.dir)

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:  # noqa: N802
            if self.path not in {"/metrics", "/"}:
                self.send_response(404)
                self.end_headers()
                return
            body = _combine(directory)
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; version=0.0.4; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, fmt: str, *a) -> None:
            return

    server = HTTPServer((args.host, args.port), Handler)
    print(f"eval-exporter serving {directory} on :{args.port}", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
