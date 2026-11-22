import os, sys, re, json, time, secrets, threading, subprocess, http.client, html, urllib.parse, socket
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

os.umask(0o077)
os.environ.clear()
os.environ.update({'PATH':'/usr/bin:/bin', 'HOME':'/nonexistent', 'CRIVO_MODO':'simulado'})
ROOT=Path(__file__).resolve().parent
os.chdir(ROOT)
sys.path.insert(0, str(ROOT))
from crivo import service, server
password=secrets.token_urlsafe(24)
(ROOT/'password').write_text(password)
os.chmod(ROOT/'password', 0o600)
service.initialize(ROOT/'demo.sqlite3')
backend=server.make_server(ROOT/'demo.sqlite3', port=0, adapters=None)
threading.Thread(target=backend.serve_forever, daemon=True).start()
backend_port=backend.server_port
lock=threading.RLock(); sessions={}; attempts=[]; public_host=None; deadline=time.monotonic()+7200

class Handler(BaseHTTPRequestHandler):
    protocol_version='HTTP/1.1'
    def log_message(self,*args): pass
    def setup(self):
        super().setup(); self.connection.settimeout(8)
    def response(self,status,body=b'',ctype='text/plain; charset=utf-8',headers=()):
        self.send_response(status); self.send_header('Content-Type',ctype); self.send_header('Content-Length',str(len(body)))
        self.send_header('Cache-Control','no-store, max-age=0'); self.send_header('Pragma','no-cache')
        self.send_header('X-Content-Type-Options','nosniff'); self.send_header('Referrer-Policy','same-origin')
        self.send_header('X-Frame-Options','DENY'); self.send_header('Content-Security-Policy',"default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; connect-src 'self'; form-action 'self'; base-uri 'none'; frame-ancestors 'none'")
        for k,v in headers: self.send_header(k,v)
        self.send_header('Connection','close'); self.end_headers()
        if self.command != 'HEAD': self.wfile.write(body)
        self.close_connection=True
    def valid_host(self):
        hosts=self.headers.get_all('Host',[])
        return len(hosts)==1 and hosts[0] in (public_host, '127.0.0.1:'+str(self.server.server_port)) and public_host is not None
    def origin_ok(self):
        host=self.headers.get('Host'); expected=('http://' if host.startswith('127.0.0.1:') else 'https://')+host
        return self.headers.get_all('Origin',[]) == [expected]
    def cookie(self):
        raw=self.headers.get_all('Cookie',[])
        if len(raw)!=1: return None
        parts=[p.strip().split('=',1) for p in raw[0].split(';')]
        vals=[p[1] for p in parts if len(p)==2 and p[0]=='__Host-crivo']
        return vals[0] if len(vals)==1 else None
    def session(self):
        sid=self.cookie()
        with lock:
            s=sessions.get(sid)
            if s and s['until']>time.monotonic(): return s
        return None
    def guard(self):
        if time.monotonic()>deadline: self.response(503,b'Indisponivel'); return False
        if not self.valid_host(): self.response(400,b'Requisicao invalida'); return False
        if self.headers.get('Transfer-Encoding') is not None: self.response(400,b'Requisicao invalida'); return False
        return True
    def body(self, maximum):
        lengths=self.headers.get_all('Content-Length',[])
        if len(lengths)!=1 or not lengths[0].isascii() or not lengths[0].isdigit(): return None
        n=int(lengths[0]); return self.rfile.read(n) if 0<n<=maximum else None
    def do_GET(self):
        if not self.guard(): return
        if self.path=='/login':
            sid=secrets.token_urlsafe(32); token=secrets.token_urlsafe(32)
            with lock:
                if len(sessions)>1000: sessions.clear()
                sessions[sid]={'csrf':token,'auth':False,'until':time.monotonic()+600}
            page=('<!doctype html><html lang="pt-BR"><meta charset="utf-8"><title>Crivo demonstração</title><h1>Crivo — demonstração sintética</h1><form method="post" action="/login"><input type="hidden" name="csrf" value="'+token+'"><label>Senha <input type="password" name="password" required autocomplete="current-password"></label> <button>Entrar</button></form></html>').encode()
            return self.response(200,page,'text/html; charset=utf-8',[('Set-Cookie','__Host-crivo='+sid+'; Path=/; Secure; HttpOnly; SameSite=Strict')])
        s=self.session()
        if not s or not s['auth']: return self.response(401,b'Autenticacao necessaria')
        if self.path=='/':
            page=server.HTML.replace(b"'Content-Type':'application/json'", ("'Content-Type':'application/json','X-CSRF-Token':'"+s['csrf']+"'").encode())
            return self.response(200,page,'text/html; charset=utf-8')
        if self.path=='/api/cenarios' or re.fullmatch(r'/api/execucoes/[a-f0-9]{32}(?:/eventos)?', self.path): return self.forward('GET')
        return self.response(404,b'Nao encontrado')
    def do_POST(self):
        if not self.guard(): return
        if not self.origin_ok(): return self.response(403,b'Origem invalida')
        s=self.session()
        if self.path=='/login':
            raw=self.body(512)
            try:
                data=urllib.parse.parse_qs(raw.decode('utf-8'),strict_parsing=True, max_num_fields=2) if raw else {}
                valid=set(data)=={'csrf','password'} and all(len(x)==1 for x in data.values())
            except (ValueError,UnicodeError): valid=False
            with lock:
                now=time.monotonic(); attempts[:]=[t for t in attempts if now-t<600]
                if len(attempts)>=8: return self.response(429,b'Tente mais tarde')
                if not valid or not s or s['auth'] or not secrets.compare_digest(data['csrf'][0],s['csrf']) or not secrets.compare_digest(data['password'][0],password):
                    attempts.append(now); return self.response(403,b'Acesso negado')
                sessions.pop(self.cookie(),None)
                sid=secrets.token_urlsafe(32); sessions[sid]={'csrf':secrets.token_urlsafe(32),'auth':True,'until':min(deadline,now+3600)}
            return self.response(303,b'',headers=[('Location','/'),('Set-Cookie','__Host-crivo='+sid+'; Path=/; Secure; HttpOnly; SameSite=Strict')])
        if not s or not s['auth']: return self.response(401,b'Autenticacao necessaria')
        if self.path!='/api/execucoes': return self.response(404,b'Nao encontrado')
        if self.headers.get_all('X-CSRF-Token',[]) != [s['csrf']]: return self.response(403,b'Token invalido')
        if self.headers.get_content_type()!='application/json': return self.response(400,b'Requisicao invalida')
        raw=self.body(1024)
        try:
            data=json.loads(raw,object_pairs_hook=server.unique_keys) if raw else None
            if not isinstance(data,dict) or set(data)!={'cenario'} or data['cenario'] not in service.CASES: raise ValueError()
        except (ValueError,TypeError,UnicodeError): return self.response(400,b'Requisicao invalida')
        return self.forward('POST',json.dumps(data).encode())
    def forward(self,method,body=None):
        conn=http.client.HTTPConnection('127.0.0.1',backend_port,timeout=5)
        try:
            conn.request(method,self.path,body,{'Content-Type':'application/json','Origin':'http://127.0.0.1:'+str(backend_port),'Connection':'close'})
            resp=conn.getresponse(); content=resp.read(1000001)
            if len(content)>1000000 or resp.status not in (200,201,400,404): return self.response(502,b'Indisponivel')
            return self.response(resp.status,content,'application/json; charset=utf-8')
        except Exception: return self.response(502,b'Indisponivel')
        finally: conn.close()
    def do_HEAD(self): self.response(405,b'')
    def do_PUT(self): self.response(405,b'')
    def do_DELETE(self): self.response(405,b'')
    def do_OPTIONS(self): self.response(405,b'')
    def do_PATCH(self): self.response(405,b'')
    def send_error(self,code,message=None,explain=None):
        try: self.response(400,b'Requisicao invalida')
        except Exception: pass

class QuietServer(ThreadingHTTPServer):
    daemon_threads=True
    def handle_error(self,*args): pass
proxy=QuietServer(('127.0.0.1',0),Handler)
threading.Thread(target=proxy.serve_forever,daemon=True).start()
proc=subprocess.Popen([str(ROOT/'cloudflared'),'tunnel','--no-autoupdate','--url','http://127.0.0.1:'+str(proxy.server_port)],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,env={'PATH':'/usr/bin:/bin','HOME':'/nonexistent'},text=True,bufsize=1)
def tunnel_reader():
    global public_host
    for line in proc.stdout:
        match=re.search(r'https://([a-z0-9-]+\.trycloudflare\.com)',line)
        if match and public_host is None:
            public_host=match.group(1)
            (ROOT/'connection.json').write_text(json.dumps({'url':'https://'+public_host+'/login','proxy_port':proxy.server_port,'backend_port':backend_port,'pid':os.getpid()}))
            os.chmod(ROOT/'connection.json',0o600)
threading.Thread(target=tunnel_reader,daemon=True).start()
try:
    while time.monotonic()<deadline and proc.poll() is None: time.sleep(1)
finally:
    proc.terminate()
    try: proc.wait(timeout=5)
    except subprocess.TimeoutExpired: proc.kill(); proc.wait()
    proxy.shutdown(); backend.shutdown()
    (ROOT/'connection.json').unlink(missing_ok=True)
