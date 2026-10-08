"""Serve the static preview with room for concurrent gallery requests."""

from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import json
from build_galleries import build_catalog


class PreviewHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path.split("?")[0] == "/assets/image-catalog.json":
            body = json.dumps(build_catalog(write=False)).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)
            return
        super().do_GET()


class PreviewServer(ThreadingHTTPServer):
    request_queue_size = 128


if __name__ == "__main__":
    handler = partial(PreviewHandler, directory=Path(__file__).parent)
    with PreviewServer(("127.0.0.1", 8000), handler) as server:
        print("Preview listening on http://127.0.0.1:8000", flush=True)
        server.serve_forever()
