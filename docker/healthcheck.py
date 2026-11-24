"""Docker HEALTHCHECK for the PostPix API.

Exits 0 when GET /api/health answers 200, otherwise 1. Uses only the standard
library because the slim base image has no curl/wget.
"""
import os
import sys
import urllib.request

URL = f"http://127.0.0.1:{os.environ.get('PORT', '8000')}/api/health"

try:
    with urllib.request.urlopen(URL, timeout=4) as response:
        sys.exit(0 if response.status == 200 else 1)
except Exception as error:  # connection refused, timeout, HTTP error...
    print(f"healthcheck failed: {error}", file=sys.stderr)
    sys.exit(1)
