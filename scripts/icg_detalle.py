# Análisis detallado del Índice de Confianza en el Gobierno (UTDT) a partir de los microdatos oficiales.
# Uso (desde la raíz del repositorio):
#   python scripts/icg_detalle.py "ruta/Base_histórica_2001-presente-ICG.dta"
# Requiere pandas. Genera datos/icg_detalle.js (const ICGD=...).
import sys, json
import numpy as np, pandas as pd

df = pd.read_stata(sys.argv[1], convert_categoricals=False)
o = df.ola.astype(int) - 502 + 10              # ola 502 = noviembre de 2001
df['t'] = 2001 * 12 + o                         # meses absolutos (año*12 + mes-1)
df['k'] = (df.t // 12).astype(str) + '-' + (df.t % 12 + 1).map('{:02d}'.format)
df['w'] = df.ponderacion_UTDT

# Ciudad -> provincia (códigos INDEC) -> región UTDT
CP = {0:'06',1:'02',3:'14',4:'82',5:'50',6:'90',7:'06',8:'06',9:'66',10:'82',11:'70',12:'22',13:'18',14:'38',15:'30',16:'58',17:'34',18:'74',19:'46',20:'26',21:'06',22:'50',23:'74',24:'06',25:'78',26:'18',27:'54',28:'62',29:'90',30:'14',31:'06',32:'86',33:'50',34:'22',35:'30',36:'66',37:'54',38:'62',39:'70',40:'10',42:'06',43:'06',53:'34',65:'86',66:'94'}
RP = {'02':1,'06':2,'14':2,'82':2,'30':2,'42':2,'50':3,'70':3,'74':3,'90':4,'66':4,'38':4,'10':4,'86':4,'46':4,'22':5,'18':5,'54':5,'34':5,'58':6,'62':6,'26':6,'78':6,'94':6}
df['reg'] = df.Ciudad.map(CP).map(RP)
df.loc[df.Ciudad == 0, 'reg'] = 1               # Gran Buenos Aires -> AMBA
df.loc[df.reg.isna(), 'reg'] = df.get('Region')

df['nucleo'] = (df.ICG >= 4) * 1.0              # confía en 4 o 5 de las 5 preguntas
df['rechazo'] = (df.ICG == 0) * 1.0             # no confía en ninguna

def wm(g, c='ICG'):
    x = g[[c, 'w']].dropna()
    x = x[x.w > 0]
    return float(np.average(x[c], weights=x.w)) if len(x) else None

def r1(v): return None if v is None or np.isnan(v) else round(v, 1)

T = int(df.t.max()); TK = df.loc[df.t == T, 'k'].iloc[0]
out = {'actualizado': TK, 'n': int(len(df))}

# 1. Luna de miel: primeros 48 meses de cada gobierno
# (nombre, primer mes completo, último mes antes del traspaso, color)
GOV = [('Kirchner','2003-06','2007-11','#0277BD'),('Cristina I','2008-01','2011-11','#29B6F6'),('Cristina II','2012-01','2015-11','#4FC3F7'),
       ('Macri','2016-01','2019-11','#E8B800'),('Fernández','2020-01','2023-11','#1F88E5'),('Milei','2024-01','2027-11','#6C4C99')]
mon = df.groupby('t').apply(lambda g: wm(g) * 20)
luna = []
for n, s, e, c in GOV:
    y, m = map(int, s.split('-')); t0 = y * 12 + m - 1
    y2, m2 = map(int, e.split('-')); t1 = min(t0 + 48, y2 * 12 + m2, T + 1)
    luna.append({'n': n, 'c': c, 'v': [r1(mon[t]) for t in range(t0, t1) if t in mon.index]})
out['luna'] = luna

# 1b. Margen de error mensual (95 %, escala 0-100): 1,96 × desvío ponderado / raíz del n efectivo (Kish)
moe = {}
for k, g in df.groupby('k'):
    w = g.w.values; x = g.ICG.values; m = np.average(x, weights=w)
    neff = w.sum() ** 2 / (w ** 2).sum(); sd = np.sqrt(np.average((x - m) ** 2, weights=w))
    moe[k] = round(1.96 * sd / np.sqrt(neff) * 20, 2)
out['margen'] = moe

# 2. Las cinco preguntas por gobierno (promedio del mandato, 0-100)
COMP = [('eval_gob_rec','Evaluación general'),('benef_gob_rec','Gobierna para la mayoría'),('adm_gp_rec','Eficiencia del gasto'),
        ('cor_gob_rec','Honestidad'),('resol_prob_rec','Resuelve los problemas')]
G2 = [('Duhalde','2002-01')] + [(n, s) for n, s, _, _ in GOV]
comp = []
for i, (n, s) in enumerate(G2):
    y, m = map(int, s.split('-')); t0 = y * 12 + m - 1
    t1 = (lambda a: int(a[0]) * 12 + int(a[1]) - 1)(G2[i + 1][1].split('-')) if i + 1 < len(G2) else T + 1
    g = df[(df.t >= t0) & (df.t < t1)]
    comp.append({'n': n, 'v': [r1(wm(g, c) * 20) for c, _ in COMP], 'icg': r1(wm(g) * 20)})
out['comp'] = {'preguntas': [l for _, l in COMP], 'gob': comp}
# variación de cada pregunta: últimos 3 meses contra los mismos meses del año anterior
cur = df[df.t > T - 3]; prev = df[(df.t > T - 15) & (df.t <= T - 12)]
out['comp']['actual'] = [r1(wm(cur, c) * 20) for c, _ in COMP]
out['comp']['anterior'] = [r1(wm(prev, c) * 20) for c, _ in COMP]

# 3 y 4. Series trimestrales por región y por segmento
df['q'] = (df.t // 3) * 3
def qser(col, codes, min_n=150, field='ICG', scale=20):
    res = {}
    for code, lab in codes.items():
        g = df[df[col] == code].groupby('q')
        pts = []
        for q, x in g:
            if len(x) >= min_n:
                v = wm(x, field)
                if v is not None: pts.append([min(f"{q // 12}-{q % 12 + 2:02d}", TK), r1(v * scale)])
        res[lab] = pts
    return res
REG = {1:'AMBA',2:'Pampeana',3:'Cuyo',4:'NOA',5:'NEA',6:'Patagonia'}
SEG = {
  'region': ('reg', REG),
  'edad': ('edad', {1:'18 a 29',2:'30 a 49',3:'50 o más'}),
  'sexo': ('sexo', {0:'Mujeres',1:'Varones'}),
  'educacion': ('edu', {1:'Primario',2:'Secundario',3:'Terciario o universitario'}),
}
out['seg'] = {k: qser(c, codes, 80 if k == 'region' else 150) for k, (c, codes) in SEG.items()}
df['_all'] = 1
out['seg']['distribucion'] = {'Núcleo (4 o 5 de 5)': qser('_all', {1:'x'}, field='nucleo', scale=100)['x'],
                              'Rechazo total (0 de 5)': qser('_all', {1:'x'}, field='rechazo', scale=100)['x']}

# Región: ahora (últimos 3 meses) contra la elección de octubre de 2025 (septiembre-octubre 2025)
ref = df[df.k.isin(['2025-09', '2025-10'])]
reg = {}
for code, lab in REG.items():
    a = cur[cur.reg == code]; b = ref[ref.reg == code]
    reg[lab] = {'ahora': r1(wm(a) * 20), 'oct2025': r1(wm(b) * 20), 'n': int(len(a))}
nat_now, nat_ref = wm(cur) * 20, wm(ref) * 20
for v in reg.values():
    v['cambio'] = r1(v['ahora'] - v['oct2025'])
    v['relativo'] = r1((v['ahora'] - v['oct2025']) - (nat_now - nat_ref))   # cambio respecto del país
out['region'] = {'datos': reg, 'pais': {'ahora': r1(nat_now), 'oct2025': r1(nat_ref)},
                 'periodo': f"{cur.k.min()} a {TK}", 'k': 0.4,
                 'nota': 'Entre elecciones consecutivas de diputados (2005-2025), cuando la confianza de una región cambia 1 punto más que el promedio del país, el voto oficialista allí cambia en promedio 0,6 puntos más (correlación 0,39; 38 casos). La proyección usa 0,4 para no sobrerreaccionar al ruido de muestras regionales chicas.'}

# 5. Hallazgos sobre capacidad predictiva (elecciones de diputados 2005-2025)
out['prediccion'] = {'nota': 'Probadas como predictor del voto oficialista nacional (11 elecciones de diputados): el índice general, cada una de las cinco preguntas, el núcleo, el rechazo total y las expectativas económicas. Todas quedan entre 4,9 y 6,1 puntos de error medio; ninguna supera claramente al índice general (5,2).'}

open('datos/icg_detalle.js', 'w', encoding='utf-8').write('const ICGD=' + json.dumps(out, ensure_ascii=False, separators=(',', ':')) + ';\n')
print('ok', TK, {k: v['relativo'] for k, v in reg.items()})
