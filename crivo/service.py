"""Orquestração simulada. Adaptadores são funções injetáveis, sem rede."""
import json
import sqlite3
import uuid
from datetime import datetime, timezone
from contextlib import closing
from . import engine

CASES = {
    'completo': {'titulo': 'Completo e consistente', 'valor': 1000, 'parcelas': 10, 'total_declarado': 1000},
    'ausente': {'titulo': 'Dados ausentes', 'valor': None, 'parcelas': 10, 'total_declarado': None},
    'divergente': {'titulo': 'Total divergente', 'valor': 1000, 'parcelas': 10, 'total_declarado': 900},
    'violacao': {'titulo': 'Quantidade de parcelas inválida', 'valor': 1000, 'parcelas': 0, 'total_declarado': 1000},
}

def initialize(path):
    with closing(sqlite3.connect(path)) as db, db:
        db.executescript('CREATE TABLE IF NOT EXISTS runs (id TEXT PRIMARY KEY, result TEXT NOT NULL); CREATE TABLE IF NOT EXISTS events (seq INTEGER PRIMARY KEY AUTOINCREMENT, run_id TEXT NOT NULL, timestamp TEXT NOT NULL, tipo TEXT NOT NULL, detalhes TEXT NOT NULL);')

def analyst_simulado(case, result):
    issues = [r['regra'] for r in result['regras'] if r['status'] != 'observado']
    return {'status': 'concluido', 'texto': 'Simulação determinística: ' + ('pontos para revisão: ' + ', '.join(issues) if issues else 'nenhuma inconsistência nas regras demonstrativas; isso não é decisão de crédito.')}

def reviewer_simulado(case, result, analysis):
    issues = [r['regra'] for r in result['regras'] if r['status'] != 'observado']
    return {'status': 'inconclusivo' if issues else 'concorda', 'texto': 'Simulação: ' + ('há pontos que exigem revisão humana: ' + ', '.join(issues) if issues else 'o resumo acompanha as regras demonstrativas; concordância não prova correção.')}

def _valid(value, statuses):
    return isinstance(value, dict) and set(value) == {'status', 'texto'} and value['status'] in statuses and isinstance(value['texto'], str) and 0 < len(value['texto']) <= 2000

def run(path, scenario, analyst=analyst_simulado, reviewer=reviewer_simulado):
    if scenario not in CASES: raise ValueError('Cenário desconhecido')
    case = dict(CASES[scenario]); rules = engine.evaluate(case); events_list = []
    def event(kind, details): events_list.append((kind, details))
    event('cenario_selecionado', {'cenario': scenario, 'fonte': 'catálogo sintético local'})
    event('regras_executadas', rules)
    try:
        a = analyst(dict(case), json.loads(json.dumps(rules)))
        if not _valid(a, {'concluido'}): raise ValueError('saída inválida')
    except Exception:
        a = {'status': 'falha', 'texto': 'Falha ou saída inválida do analista; revisão humana necessária.'}
    from .hermes import HermesAdapter
    def origin(adapter, simulated, role):
        if adapter is simulated: return 'simulado_local'
        if type(adapter) is HermesAdapter and adapter.role == role: return 'adaptador_hermes_local_perfil_solicitado_crivo_' + role + '_modelo_nao_verificado'
        return 'adaptador_injetado_origem_nao_verificada'
    origins = {'analista': origin(analyst, analyst_simulado, 'analista'), 'revisor': origin(reviewer, reviewer_simulado, 'revisor')}
    event('analista', {'origem': origins['analista'], 'resultado': a})
    if a['status'] == 'falha':
        r = {'status': 'nao_executado', 'texto': 'Revisor não executado após falha do analista.'}
    else:
        try:
            r = reviewer(dict(case), json.loads(json.dumps(rules)), dict(a))
            if not _valid(r, {'concorda', 'contesta', 'inconclusivo'}): raise ValueError('saída inválida')
        except Exception:
            r = {'status': 'falha', 'texto': 'Falha ou saída inválida do revisor; revisão humana necessária.'}
    event('revisor', {'origem': origins['revisor'], 'resultado': r})
    ident = uuid.uuid4().hex
    result = {'id': ident, 'simulacao': True, 'aviso': 'Simulação exclusivamente sintética. Não é decisão de crédito.', 'cenario_id': scenario, 'cenario': case, 'politica': engine.POLICY, 'motor': rules, 'analista': a, 'revisor': r, 'adaptadores': origins, 'estado': 'revisao_humana', 'revisao_humana': 'pendente'}
    event('revisao_humana_necessaria', {'estado': result['estado']})
    with closing(sqlite3.connect(path)) as db, db:
        db.execute('INSERT INTO runs VALUES (?, ?)', (ident, json.dumps(result, ensure_ascii=False)))
        for kind, details in events_list:
            db.execute('INSERT INTO events (run_id,timestamp,tipo,detalhes) VALUES (?,?,?,?)', (ident, datetime.now(timezone.utc).isoformat(), kind, json.dumps(details, ensure_ascii=False)))
    return result

def get_run(path, ident):
    with closing(sqlite3.connect(path)) as db: row = db.execute('SELECT result FROM runs WHERE id=?', (ident,)).fetchone()
    return json.loads(row[0]) if row else None

def events(path, ident):
    with closing(sqlite3.connect(path)) as db: rows = db.execute('SELECT seq,timestamp,tipo,detalhes FROM events WHERE run_id=? ORDER BY seq', (ident,)).fetchall()
    return [{'sequencia': s, 'timestamp': t, 'tipo': k, 'detalhes': json.loads(d)} for s,t,k,d in rows]
