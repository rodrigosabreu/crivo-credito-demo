POLICY_VERSION = 'demonstrativa-1.0'
POLICY = {'versao': POLICY_VERSION, 'descricao': 'Simulação: verifica presença, valores positivos e consistência aritmética. Não há limites de crédito.'}

def evaluate(data):
    valor, parcelas, total = (data.get(k) for k in ('valor', 'parcelas', 'total_declarado'))
    missing = [k for k in ('valor', 'parcelas', 'total_declarado') if data.get(k) is None]
    presence = {'regra': 'Presença dos campos', 'status': 'ausente' if missing else 'observado', 'evidencia': 'Campos ausentes: ' + ', '.join(missing) if missing else 'Todos os campos presentes no cenário sintético.'}
    invalid = [k for k in ('valor', 'parcelas', 'total_declarado') if data.get(k) is not None and (type(data[k]) is not int or data[k] <= 0)]
    positive = {'regra': 'Valores inteiros positivos', 'status': 'violacao' if invalid else ('ausente' if missing else 'observado'), 'evidencia': 'Campos inválidos: ' + ', '.join(invalid) if invalid else ('Não verificável integralmente: campos ausentes.' if missing else 'Valores positivos observados.')}
    status = 'ausente' if valor is None or total is None else ('divergente' if valor != total else 'observado')
    consistency = {'regra': 'Total declarado igual ao valor', 'status': status, 'evidencia': f'Valor: {valor}; total declarado: {total}. Fonte: cenário sintético.'}
    installment = round(valor / parcelas, 2) if type(valor) is int and valor > 0 and type(parcelas) is int and parcelas > 0 else None
    return {'politica': POLICY_VERSION, 'regras': [presence, positive, consistency], 'valor_por_parcela': installment, 'nota_calculo': 'Divisão demonstrativa sem juros; não é oferta.'}
