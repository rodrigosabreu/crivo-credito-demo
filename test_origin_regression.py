import http.client
import json
import re
import urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parent

def test_login_origin_and_csrf():
    info = json.loads((ROOT / 'connection.json').read_text())
    host = '127.0.0.1:' + str(info['proxy_port'])
    def request(method, path, body=None, headers=None):
        c = http.client.HTTPConnection('127.0.0.1', info['proxy_port'], timeout=5)
        try:
            c.request(method, path, body, headers or {})
            r = c.getresponse()
            return r.status, dict(r.getheaders()), r.read()
        finally:
            c.close()
    status, headers, page = request('GET', '/login')
    assert status == 200
    assert headers['Referrer-Policy'] == 'same-origin'
    cookie = headers['Set-Cookie'].split(';')[0]
    token = re.search(rb'name="csrf" value="([^"]+)', page).group(1).decode()
    body = urllib.parse.urlencode({'csrf': token, 'password': 'synthetic-incorrect-password'})
    common = {'Cookie': cookie, 'Content-Type': 'application/x-www-form-urlencoded'}
    for origin in ('null', 'https://evil.invalid', None):
        h = dict(common)
        if origin is not None: h['Origin'] = origin
        status, _, result = request('POST', '/login', body, h)
        assert status == 403 and result == b'Origem invalida'
    status, _, result = request('POST', '/login', body, dict(common, Origin='http://' + host))
    assert status == 403 and result == b'Acesso negado'
    bad_body = urllib.parse.urlencode({'csrf': 'wrong', 'password': 'synthetic-incorrect-password'})
    status, _, result = request('POST', '/login', bad_body, dict(common, Origin='http://' + host))
    assert status == 403 and result == b'Acesso negado'
