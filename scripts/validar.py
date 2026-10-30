# Valida los archivos de datos. Uso: python3 scripts/validar.py (desde la raíz del repositorio)
import json, re, os, sys, datetime
D = 'datos/'
err = []
def js(name):
    s = open(D + name, encoding='utf-8').read().strip()
    m = re.match(r'^const (\w+)=', s)
    if not m: raise ValueError('no empieza con const NOMBRE=')
    return json.loads(s[m.end():].rstrip(';'))
data = {}
for f in sorted(os.listdir(D)):
    if not f.endswith('.js') or f in ('meta.js', 'linea_de_tiempo.js'): continue
    try: data[f] = js(f)
    except Exception as e: err.append(f'{f}: {e}')
enc = data.get('encuestas.js', [])
vistos = set()
for i, r in enumerate(enc):
    try:
        datetime.date.fromisoformat(r['fecha'])
        assert r['serie'] in ('candidatos', 'fuerzas', 'balotaje', 'imagen'), 'serie'
        assert all(isinstance(v, (int, float)) and 0 <= v <= 100 for v in r.get('negativa', {}).values()), 'negativa fuera de 0-100'
        assert r.get('encuestadora'), 'encuestadora'
        assert isinstance(r['valores'], dict) and r['valores'], 'valores'
        assert all(isinstance(v, (int, float)) and 0 <= v <= 100 for v in r['valores'].values()), 'valores fuera de 0-100'
        assert str(r.get('fuente', '')).startswith('http'), 'fuente'
        k = (r['encuestadora'], r['fecha'], r['serie'], r.get('escenario'), tuple(sorted(c for c in r['valores'] if c not in ('Blanco', 'Indecisos', 'Otros'))) if r['serie'] == 'balotaje' else None)
        assert k not in vistos, 'duplicada'; vistos.add(k)
    except Exception as e: err.append(f'encuestas fila {i} ({r.get("encuestadora")} {r.get("fecha")}): {e}')
icg = data.get('icg.js')
if icg:
    meses = [r['mes'] for r in icg['serie']]
    if meses != sorted(meses) or len(set(meses)) != len(meses): err.append('icg: meses desordenados o repetidos')
    if any(not (0 <= r['icg'] <= 5) for r in icg['serie']): err.append('icg: valores fuera de 0-5')
for f in ('meta.js', 'linea_de_tiempo.js'):
    s = open(D + f, encoding='utf-8').read()
    if s.count('{') != s.count('}') or s.count('[') != s.count(']'): err.append(f'{f}: llaves o corchetes desbalanceados')
print('\n'.join(err) if err else f'OK: {len(data)} archivos, {len(enc)} encuestas, ICG hasta {icg["serie"][-1]["mes"] if icg else "—"}')
sys.exit(1 if err else 0)
