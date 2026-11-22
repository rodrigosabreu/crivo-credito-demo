#!/usr/bin/env python3
"""Run the Crivo Crédito demo server."""
import sys
sys.path.insert(0, '/opt/data/projects/crivo-credito-demo')

from crivo.server import make_server
from crivo.service import initialize
import tempfile
import os

db_path = os.path.join(tempfile.gettempdir(), 'crivo_demo.db')
initialize(db_path)
server = make_server(db_path, port=8000, adapters=None)
print('Server ready on port 8000', flush=True)
server.serve_forever()