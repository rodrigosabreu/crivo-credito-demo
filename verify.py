import json, re, http.client, urllib.parse, ssl
from pathlib import Path
root=Path(__file__).resolve().parent
info=json.loads((root/'connection.json').read_text()); password=(root/'password').read_text(); host=urllib.parse.urlsplit(info['url']).netloc

def test(public):
    target=host if public else '127.0.0.1:'+str(info['proxy_port'])
    origin=('https://' if public else 'http://')+target
    def req(method,path,body=None,headers=None):
        conn=http.client.HTTPSConnection(host,timeout=20,context=ssl.create_default_context()) if public else http.client.HTTPConnection('127.0.0.1',info['proxy_port'],timeout=10)
        try:
            conn.request(method,path,body=body,headers=headers or {})
            resp=conn.getresponse(); content=resp.read(); return resp.status,dict(resp.getheaders()),content
        finally: conn.close()
    status,h,b=req('GET','/api/cenarios'); assert status==401
    assert h.get('Cache-Control','').startswith('no-store')
    status,h,b=req('GET','/login'); assert status==200
    cookie=h['Set-Cookie']; assert all(x in cookie for x in ('Secure','HttpOnly','SameSite=Strict','Path=/'))
    ck=cookie.split(';')[0]; csrf=re.search(rb'name="csrf" value="([^"]+)',b).group(1).decode()
    body=urllib.parse.urlencode({'csrf':csrf,'password':password})
    status,h,b=req('POST','/login',body,{'Origin':'https://evil.invalid','Cookie':ck,'Content-Type':'application/x-www-form-urlencoded'}); assert status==403
    status,h,b=req('POST','/login',body,{'Origin':origin,'Cookie':ck,'Content-Type':'application/x-www-form-urlencoded'}); assert status==303
    ck=h['Set-Cookie'].split(';')[0]
    status,h,b=req('GET','/',headers={'Cookie':ck}); assert status==200
    token=re.search(rb"'X-CSRF-Token':'([^']+)'",b).group(1).decode()
    status,h,b=req('GET','/api/cenarios',headers={'Cookie':ck}); cases=json.loads(b); assert status==200 and len(cases)>0 and all(x['simulacao'] for x in cases)
    headers={'Origin':origin,'Cookie':ck,'Content-Type':'application/json'}
    status,h,b=req('POST','/api/execucoes',json.dumps({'cenario':'completo'}),headers); assert status==403
    headers['X-CSRF-Token']=token
    status,h,b=req('POST','/api/execucoes',json.dumps({'cenario':'completo'}),headers); assert status==201
    result=json.loads(b); assert result['simulacao'] is True and result['cenario_id']=='completo' and set(result['adaptadores'].values())=={'simulado_local'} and result['revisao_humana']=='pendente'
    status,h,b=req('GET','/api/execucoes/'+result['id']+'/eventos',headers={'Cookie':ck}); assert status==200 and len(json.loads(b))>0
    status,h,b=req('GET','/api/unknown',headers={'Cookie':ck}); assert status==404
    print(('publico' if public else 'local')+': OK; anônimo=401; origem maliciosa=403; login=303; csrf ausente=403; execução=201; agentes=simulado_local; eventos=200; rota proibida=404')

test(False); test(True)
