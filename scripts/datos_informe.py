# Genera datos-informe.json (raíz del sitio) para la web de informes de Plexum.
# Especificación: «Datos que cada web publica», v1.3, parte común + apartado 6 (Monitor Electoral):
#   agenda = elecciones provinciales y municipales de los próximos 60 días;
#   novedades «encuesta» y «elección» de los últimos 90 días, con alcance.
# Solo usa lo que el sitio ya muestra (datos/encuestas.js y datos/calendario2027.js).
# Uso, desde la raíz del repositorio: python3 scripts/datos_informe.py
import json, re, datetime as dt, unicodedata

SITIO = 'https://francomartinlopez.github.io/eleccionesargentina/'
TZ = dt.timezone(dt.timedelta(hours=-3))
AHORA = dt.datetime.now(TZ).replace(microsecond=0)
HOY = AHORA.date()
PROV = {'02': 'CABA', '06': 'Buenos Aires', '10': 'Catamarca', '14': 'Córdoba', '18': 'Corrientes', '22': 'Chaco', '26': 'Chubut',
        '30': 'Entre Ríos', '34': 'Formosa', '38': 'Jujuy', '42': 'La Pampa', '46': 'La Rioja', '50': 'Mendoza', '54': 'Misiones',
        '58': 'Neuquén', '62': 'Río Negro', '66': 'Salta', '70': 'San Juan', '74': 'San Luis', '78': 'Santa Cruz', '82': 'Santa Fe',
        '86': 'Santiago del Estero', '90': 'Tucumán', '94': 'Tierra del Fuego'}
NAC = {'nivel': 'nacional', 'provincia': '', 'localidad': '', 'pais': 'Argentina'}
EJE = 'Política nacional'
NOV = ('Blanco', 'Indecisos', 'Otros', 'Blanco/Indecisos', 'No contesta', 'Ninguno', 'No votaría')
FUERZA = {'LLA': 'La Libertad Avanza', 'PRO_JxC': 'PRO/JxC', 'Peronismo': 'peronismo', 'Provincias Unidas': 'Provincias Unidas', 'Izquierda': 'izquierda', 'UCR': 'UCR'}

def js(nombre):
    s = open('datos/' + nombre, encoding='utf-8').read().strip()
    return json.loads(re.sub(r'^const \w+=', '', s).rstrip(';'))

def slug(t):
    t = unicodedata.normalize('NFKD', t).encode('ascii', 'ignore').decode().lower()
    return re.sub(r'[^a-z0-9]+', '-', t).strip('-')

def f1(v): return ('%.1f' % v).replace('.', ',').replace(',0', '') if isinstance(v, (int, float)) else str(v)

def fecha(s):
    try: return dt.date.fromisoformat(s)
    except Exception: return None

def palabras(t, n=60):
    w = t.split()
    return t if len(w) <= n else ' '.join(w[:n]).rstrip(',;') + '…'

# ---------- Novedades «encuesta»: una por consultora y fecha de campo, últimos 90 días ----------
ENC = js('encuestas.js')
desde = HOY - dt.timedelta(days=90)
grupos = {}
for r in ENC:
    d = fecha(r['fecha'])
    if not d or d < desde or d > HOY: continue
    grupos.setdefault((r['fecha'], r['encuestadora']), []).append(r)

def frase(r):
    v = {k: x for k, x in r['valores'].items() if k not in NOV}
    orden = sorted(v.items(), key=lambda kv: -kv[1])
    if r['serie'] == 'balotaje':
        return 'balotaje ' + ' vs. '.join(f'{k} {f1(x)} %' for k, x in orden)
    if r['serie'] == 'imagen':
        return 'imagen positiva: ' + ', '.join(f'{k} {f1(x)} %' for k, x in orden[:4])
    if r['serie'] == 'fuerzas':
        return 'intención de voto por fuerza: ' + ', '.join(f'{FUERZA.get(k, k)} {f1(x)} %' for k, x in orden[:3])
    return 'primera vuelta: ' + ', '.join(f'{k} {f1(x)} %' for k, x in orden[:3])

novedades = []
for (f, enc), rows in sorted(grupos.items(), reverse=True):
    partes = [frase(r) for r in rows]
    muestra = next((r.get('muestra') for r in rows if r.get('muestra')), None)
    aprox = any(r.get('fecha_aprox') for r in rows)
    res = f'Encuesta nacional de {enc}' + (f' ({muestra:,} casos)'.replace(',', '.') if muestra else '') + ' sobre la elección presidencial de 2027: ' + '; '.join(partes) + '.'
    if aprox: res += ' Fecha de publicación; no se informó el fin del trabajo de campo.'
    if any('Cristina' in r['valores'] for r in rows):
        res += ' Cristina Fernández de Kirchner está inhabilitada por condena firme.'
    novedades.append({
        'id': f'{f}-encuesta-{slug(enc)}', 'fecha_dato': f,
        'titulo': f'Encuesta de {enc}: ' + ('balotaje' if all(r['serie'] == 'balotaje' for r in rows) else 'imagen de dirigentes' if all(r['serie'] == 'imagen' for r in rows) else 'intención de voto presidencial 2027'),
        'resumen': palabras(res), 'tipo': 'encuesta', 'eje': EJE, 'alcance': NAC, 'rubros': [], 'subrubros': [], 'exposicion': [],
        'url': rows[0].get('fuente') or SITIO + '#encuestas'})

# ---------- Novedades «elección»: definiciones del calendario provincial 2027 (últimos 90 días) ----------
CAL = js('calendario2027.js')
relev = fecha(CAL.get('actualizado', '')) or HOY
FIRMES = {'oficial', 'convocada', 'anunciada', 'con Nación'}
MES = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']
def ftxt(s):
    d = fecha(s)
    return f'{d.day} de {MES[d.month - 1]} de {d.year}' if d else s
if relev >= desde:
    for r in CAL['provincias']:
        if r['estado'] not in FIRMES or not fecha(r.get('fecha') or ''): continue
        p = PROV[r['prov']]
        t = (f'{p} votará con la elección nacional del {ftxt(r["fecha"])}' if r['estado'] == 'con Nación'
             else f'{p} fija sus elecciones provinciales para el {ftxt(r["fecha"])}')
        res = f'{t}. Cargos: {re.sub(r"^cargos ", "", r["cargos"].lower())}.' + (f' PASO provinciales el {ftxt(r["paso"])}.' if r.get('paso') else '') + (f' {re.sub(r"^PASO[^;]*; ?", "", r["nota"]).capitalize() if r.get("paso") else r["nota"]}' if r.get('nota') else '') + f' Estado: {r["estado"]}, según el relevamiento del sitio al {ftxt(CAL["actualizado"])}.'
        novedades.append({'id': f'{CAL["actualizado"]}-eleccion-{slug(p)}-2027', 'fecha_dato': CAL['actualizado'], 'titulo': t,
                          'resumen': palabras(res), 'tipo': 'elección', 'eje': EJE,
                          'alcance': {'nivel': 'provincia', 'provincia': p, 'localidad': '', 'pais': 'Argentina'},
                          'rubros': [], 'subrubros': [], 'exposicion': [], 'url': r['fuente']})
    n = CAL.get('nacional', {})
    if n.get('paso'):
        novedades.append({'id': f'{CAL["actualizado"]}-eleccion-paso-nacionales-2027', 'fecha_dato': CAL['actualizado'],
                          'titulo': 'Estado de las PASO nacionales 2027', 'resumen': palabras(n['paso'] + f' Elección presidencial: {ftxt(n.get("fecha"))}.'),
                          'tipo': 'elección', 'eje': EJE, 'alcance': NAC, 'rubros': [], 'subrubros': [], 'exposicion': [],
                          'url': n.get('fuente') or SITIO + '#proyeccion'})
novedades.sort(key=lambda x: x['fecha_dato'], reverse=True)

# ---------- Agenda: elecciones provinciales con fecha exacta en los próximos 60 días ----------
hasta = HOY + dt.timedelta(days=60)
agenda = []
for r in CAL['provincias']:
    for campo, nombre in (('paso', 'PASO provinciales'), ('fecha', 'Elecciones provinciales')):
        d = fecha(r.get(campo) or '')
        if d and HOY <= d <= hasta:
            p = PROV[r['prov']]
            agenda.append({'fecha': d.isoformat(), 'evento': f'{nombre} en {p} ({r["cargos"].lower()}; {r["estado"]})', 'eje': EJE,
                           'alcance': {'nivel': 'provincia', 'provincia': p, 'localidad': '', 'pais': 'Argentina'}, 'rubros': [], 'url': r['fuente']})
for campo, nombre in (('fecha', 'Elección presidencial y legislativa nacional'), ('balotaje', 'Balotaje presidencial (si corresponde)')):
    d = fecha(CAL.get('nacional', {}).get(campo) or '')
    if d and HOY <= d <= hasta:
        agenda.append({'fecha': d.isoformat(), 'evento': nombre, 'eje': EJE, 'alcance': NAC, 'rubros': [], 'url': SITIO + '#proyeccion'})
agenda.sort(key=lambda x: x['fecha'])

out = {'web': 'Monitor Electoral', 'version': '1.3', 'generado': AHORA.isoformat(),
       'indicadores': [], 'novedades': novedades, 'agenda': agenda, 'faltantes': []}
json.dump(out, open('datos-informe.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(f'datos-informe.json: {len(novedades)} novedades ({sum(n["tipo"] == "encuesta" for n in novedades)} encuestas, '
      f'{sum(n["tipo"] == "elección" for n in novedades)} elecciones), {len(agenda)} eventos de agenda')
