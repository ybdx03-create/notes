"""Entrypoint to run the Liquid Notes WSGI application."""
from __future__ import annotations

import os
from wsgiref.simple_server import make_server

from app import create_app


def main() -> None:
    port = int(os.getenv("PORT", "5000"))
    app = create_app()
    with make_server("0.0.0.0", port, app) as server:
        print(f"Liquid Notes available at http://localhost:{port}")
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down...")


if __name__ == "__main__":
    main()
