#!/usr/bin/env python3
"""
Local development server that mimics Vercel serverless for api/upload.py
Usage: python scripts/dev-api.py
Then: cd frontend && npm run dev
"""
import sys
import os
from http.server import HTTPServer

# Add api/ to path so we can import the handler
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'api'))
from upload import handler

PORT = 8787
print(f'Dev API server running on http://localhost:{PORT}')
print('Frontend Vite proxy: /api → http://localhost:8787')
HTTPServer(('', PORT), handler).serve_forever()
