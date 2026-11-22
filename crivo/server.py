import json
import sqlite3
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from . import service

HTML = (Path(__file__).parent / 'index.html').read_bytes()

def unique_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('duplicate key')
        result[key] = value
    return result

DB_ERROR = {'erro': 'Armazenamento indisponível; operação não confirmada. Evento não persistido ou persistência não confirmada; não há registro de revisão humana.', 'auditoria': 'nao_confirmada'}

def make_server(db_path, port=8000, adapters=None):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, format, *args): pass
        def send(self, status, data, kind='application/json; charset=utf-8'):
            data = json.dumps(data, ensure_ascii=False).encode() if kind.startswith('application/json') else data
            self.send_response(status); self.send_header('Content-Type', kind); self.send_header('Content-Length', str(len(data))); self.send_header('Cache-Control', 'no-store'); self.send_header('X-Content-Type-Options', 'nosniff'); self.end_headers(); self.wfile.write(data)
        def do_GET(self):
            path = self.path.split('?', 1)[0]
            if path in ('/', '/ui'): return self.send(200, HTML, 'text/html; charset=utf-8')
            if path == '/api/cenarios': return self.send(200, [{'id': k, 'titulo': v['titulo'], 'simulacao': True} for k,v in service.CASES.items()])
            parts = path.strip('/').split('/')
            if len(parts) in (3,4) and parts[:2] == ['api','execucoes']:
                try:
                    run = service.get_run(db_path, parts[2])
                    if run and len(parts) == 3: return self.send(200, run)
                    if run and len(parts) == 4 and parts[3] == 'eventos': return self.send(200, service.events(db_path, parts[2]))
                except sqlite3.Error:
                    return self.send(503, DB_ERROR)
            self.send(404, {'erro': 'Não encontrado'})
        def do_POST(self):
            if self.path != '/api/execucoes': return self.send(404, {'erro':'Não encontrado'})
            # Prevent cross-origin web pages from driving local requests.
            # Allow localhost, 127.0.0.1, and HTTPS tunnel origins (cloudflared, ngrok, etc.)
            origin = self.headers.get('Origin')
            allowed = (
                None,
                f'http://127.0.0.1:{self.server.server_port}',
                f'http://localhost:{self.server.server_port}',
            )
            if origin and origin not in allowed and not origin.startswith('https://'):
                return self.send(403, {'erro':'Origem não permitida'})
            try:
                length = int(self.headers.get('Content-Length', '0'))
                if not 0 < length <= 1024 or self.headers.get_content_type() != 'application/json': raise ValueError()
                data = json.loads(self.rfile.read(length), object_pairs_hook=unique_keys)
                if not isinstance(data, dict) or set(data) != {'cenario'} or not isinstance(data['cenario'], str): raise ValueError()
                result = service.run(db_path, data['cenario'], analyst=adapters[0], reviewer=adapters[1]) if adapters else service.run(db_path, data['cenario'])
            except (ValueError, UnicodeDecodeError): return self.send(400, {'erro': 'Informe somente um ID de cenário sintético válido.'})
            except sqlite3.Error: return self.send(503, DB_ERROR)
            self.send(201, result)
    return ThreadingHTTPServer(('127.0.0.1', port), Handler)
