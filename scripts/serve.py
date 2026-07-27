#!/usr/bin/env python3
"""
Production-style combined server for Docker.
Serves the built React frontend (static files) + /api/upload endpoint on one port.
Usage: python scripts/serve.py
"""
import sys
import os
from http.server import HTTPServer, SimpleHTTPRequestHandler

ROOT_DIR = os.path.join(os.path.dirname(__file__), '..')
STATIC_DIR = os.path.join(ROOT_DIR, 'frontend', 'dist')

sys.path.insert(0, os.path.join(ROOT_DIR, 'api'))
from upload import handler as api_handler


class CombinedHandler(api_handler):
    """Routes /api/* to the upload handler, everything else serves static files."""

    def do_GET(self):
        # Serve static frontend files
        path = self.path.split('?')[0]

        # Resolve file path
        if path == '/' or not os.path.exists(os.path.join(STATIC_DIR, path.lstrip('/'))):
            # SPA fallback: serve index.html for unknown paths
            file_path = os.path.join(STATIC_DIR, 'index.html')
        else:
            file_path = os.path.join(STATIC_DIR, path.lstrip('/'))

        if not os.path.isfile(file_path):
            file_path = os.path.join(STATIC_DIR, 'index.html')

        try:
            with open(file_path, 'rb') as f:
                content = f.read()
            self.send_response(200)
            self.send_header('Content-Type', self._guess_type(file_path))
            self.send_header('Content-Length', str(len(content)))
            self.end_headers()
            self.wfile.write(content)
        except Exception as e:
            self.send_error(500, str(e))

    def _guess_type(self, path):
        ext = os.path.splitext(path)[1].lower()
        types = {
            '.html': 'text/html; charset=utf-8',
            '.js': 'application/javascript',
            '.css': 'text/css',
            '.png': 'image/png',
            '.ico': 'image/x-icon',
            '.svg': 'image/svg+xml',
            '.json': 'application/json',
            '.woff2': 'font/woff2',
            '.woff': 'font/woff',
            '.ttf': 'font/ttf',
        }
        return types.get(ext, 'application/octet-stream')

    def do_POST(self):
        # Delegate all POST (i.e. /api/upload) to the API handler
        super().do_POST()

    def log_message(self, fmt, *args):
        print(f'[serve] {self.address_string()} - {fmt % args}')


PORT = int(os.environ.get('PORT', 8000))
print(f'LinuxAIO Performance server running on http://0.0.0.0:{PORT}')
print(f'Serving static files from: {STATIC_DIR}')
HTTPServer(('', PORT), CombinedHandler).serve_forever()
