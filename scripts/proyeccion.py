# Proyección 2027. Uso: python scripts/proyeccion.py  (desde la raíz del repositorio)
import json,datetime,statistics,os,re
D='datos/'
def js(name):
    p=D+name+'.js'
    if not os.path.exists(p): return None
    s=open(p,encoding='utf-8').read().strip()
    return json.loads(re.sub(r'^const \w+=','',s).rstrip(';'))
DIP=js('diputados');PR=js('presidente');ENC=js('encuestas') or [];ICG=js('icg');ICGD=js('icg_detalle')
# Ajuste regional: cambio de la confianza de cada región desde octubre de 2025, relativo al país (ver icg_detalle.py)
RP={'02':'AMBA','14':'Pampeana','82':'Pampeana','30':'Pampeana','42':'Pampeana','50':'Cuyo','70':'Cuyo','74':'Cuyo','90':'NOA','66':'NOA','38':'NOA','10':'NOA','86':'NOA','46':'NOA','22':'NEA','18':'NEA','54':'NEA','34':'NEA','58':'Patagonia','62':'Patagonia','26':'Patagonia','78':'Patagonia','94':'Patagonia'}
GBA={'06028','06035','06091','06260','06270','06274','06371','06408','06410','06412','06427','06434','06490','06515','06539','06560','06568','06658','06749','06756','06760','06805','06840','06861'}
def reg_shift(u):
    if not ICGD: return 0.0
    R=ICGD['region']['datos'];k=ICGD['region']['k']
    rel=lambda r:(R[r]['relativo'] or 0)
    if u=='06': v=.64*rel('AMBA')+.36*rel('Pampeana')
    elif u.startswith('06'): v=rel('AMBA') if u in GBA else rel('Pampeana')
    else:
        r=RP.get(u[:2]); v=rel(r) if r else 0
    return k*v/100
B=['LLA','Peronismo','PRO_JxC','Provincias Unidas','Izquierda','Otros']
MAPS={('dip','2025'):{'LLA':'LLA','DER':'LLA','PJ':'Peronismo','PU':'Provincias Unidas','UCR':'Provincias Unidas','PFED':'Provincias Unidas','CC':'Provincias Unidas','PS':'Provincias Unidas','PRO':'PRO_JxC','IZQ':'Izquierda'},
 ('pres','2023'):{'LLA':'LLA','UXP':'Peronismo','JXC':'PRO_JxC','HNP':'Provincias Unidas','FIT':'Izquierda'},
 ('dip','2021'):{'LLA':'LLA','DER':'LLA','PJ':'Peronismo','PRO':'PRO_JxC','UCR':'PRO_JxC','PFED':'Provincias Unidas','PS':'Provincias Unidas','CC':'PRO_JxC','IZQ':'Izquierda'},
 ('pres','2019'):{'AF':'Peronismo','MAC':'PRO_JxC','LAV':'Provincias Unidas','FIT':'Izquierda','GC':'LLA','ESP':'LLA'}}
W={('dip','2025'):.4,('pres','2023'):.3,('dip','2021'):.2,('pres','2019'):.1}
def src(k): return (DIP if k[0]=='dip' else PR)[k[1]]['i']['general']
def shares(v,m):
    o={b:0 for b in B};t=0
    for k,x in v.items():
        if k=='BL': continue
        o[m.get(k,'Otros')]+=x;t+=x
    return ({b:o[b]/t for b in B},t) if t else (None,0)
def base(level):
    keys=set()
    for k in W: keys|=set(src(k)[level])
    out={};wt={}
    for u in keys:
        acc={b:0 for b in B};ws=0;tot=0
        for k,w in W.items():
            v=src(k)[level].get(u)
            if not v: continue
            s,t=shares(v,MAPS[k])
            if not s: continue
            for b in B: acc[b]+=w*s[b]
            ws+=w;tot=max(tot,t)
        if ws:
            x={b:acc[b]/ws for b in B};l=min(.95,max(.01,x['LLA']+reg_shift(u)));r=1-x['LLA']
            out[u]={b:(l if b=='LLA' else x[b]*(1-l)/r) for b in B};wt[u]=tot
    return out,wt
def poll_avg(serie,days=45):
    rows=[r for r in ENC if r['serie']==serie and (serie!='balotaje' or ('Milei' in r['valores'] and 'Kicillof' in r['valores']))]
    if not rows: return None,0,None
    last=max(r['fecha'] for r in rows);ld=datetime.date.fromisoformat(last)
    rec={}
    for r in rows:
        d=datetime.date.fromisoformat(r['fecha'])
        if (ld-d).days<=days and (r['encuestadora'] not in rec or rec[r['encuestadora']]['fecha']<r['fecha']): rec[r['encuestadora']]=r
    agg={}
    for r in rec.values():
        for k,v in r['valores'].items(): agg.setdefault(k,[]).append(v)
    return {k:statistics.mean(v) for k,v in agg.items()},len(rec),last
F,nF,lastF=poll_avg('fuerzas');C,nC,lastC=poll_avg('candidatos');BAL,nB,lastB=poll_avg('balotaje')
# objetivo nacional por bloque (sin indecisos)
def target():
    if F:
        g={'LLA':F.get('LLA',0),'Peronismo':F.get('Peronismo',0)+F.get('Kirchnerismo',0),'PRO_JxC':F.get('PRO_JxC',0)+F.get('Oposición no peronista',0),'Provincias Unidas':F.get('Provincias Unidas',0)+F.get('UCR',0)+F.get('Peronismo no K',0)+F.get('Fuerza de gobernadores',0),'Izquierda':F.get('Izquierda',0),'Otros':F.get('Otros',0)+F.get('Partidos provinciales',0)}
    elif C:
        g={'LLA':C.get('Milei',0),'Peronismo':C.get('Kicillof',0)+C.get('Massa',0)+C.get('Grabois',0)+C.get('Cristina',0),'PRO_JxC':C.get('Bullrich',0)+C.get('Macri',0)+C.get('Larreta',0),'Provincias Unidas':C.get('Schiaretti',0),'Izquierda':C.get('Izquierda',0),'Otros':C.get('Otros',0)+C.get('Villarruel',0)}
    else: return None
    s=sum(g.values());return {k:v/s for k,v in g.items()}
T=target()
fit=None
if ICG and T:
    # ajuste ICG -> voto oficialista (generales), oficialismo 2027 = LLA
    pts=[]
    OF={'2003':('NK','2003-03'),'2007':('CFK','2007-09'),'2011':('CFK','2011-09'),'2015':('SCI','2015-09'),'2019':('MAC','2019-09'),'2023':('UXP','2023-09')}
    ser={r['mes']:r['icg']*20 for r in ICG['serie']}
    for y,(k,m) in OF.items():
        o=PR[y].get('ofi',{}).get('general',{}).get(k)
        if o is None:
            t={};[t.__setitem__(q,t.get(q,0)+x) for p in PR[y]['i']['general']['prov'].values() for q,x in p.items() if q!='BL'];o=100*t.get(k,0)/sum(t.values())
        if m in ser: pts.append((ser[m],o))
    if len(pts)>2:
        n=len(pts);mx=sum(p[0] for p in pts)/n;my=sum(p[1] for p in pts)/n
        b=sum((p[0]-mx)*(p[1]-my) for p in pts)/sum((p[0]-mx)**2 for p in pts);a=my-b*mx
        cur=ICG['serie'][-1];pred=a+b*cur['icg']*20
        fit={'a':a,'b':b,'pred':pred,'mes':cur['mes'],'n':n}
        lla=.7*T['LLA']+.3*pred/100
        rest=1-T['LLA'];T={k:(lla if k=='LLA' else v*(1-lla)/rest) for k,v in T.items()}
def project(level):
    bs,wt=base(level)
    nat={b:sum(bs[u][b]*wt[u] for u in bs)/sum(wt.values()) for b in B}
    f={b:(T[b]/nat[b] if nat[b]>0 else 1) for b in B}
    out={}
    for u,s in bs.items():
        x={b:s[b]*f[b] for b in B};t=sum(x.values());out[u]={b:round(100*x[b]/t,1) for b in B}
    return out,nat
def project_bal(level):
    if not BAL: return None
    a=BAL.get('Milei');c=next((BAL[k] for k in ['Kicillof','Peronismo','Massa'] if k in BAL),None)
    if not a or not c: return None
    tgt=a/(a+c)
    b23=PR['2023']['i']['balotaje'][level];d25=DIP['2025']['i']['general'][level]
    out={};wt={}
    for u,v in b23.items():
        s1=v.get('LLA',0)/max(1,v.get('LLA',0)+v.get('UXP',0))
        w=d25.get(u)
        if w:
            r=w.get('LLA',0)+w.get('PRO',0)+w.get('DER',0);p=w.get('PJ',0)
            s=.6*s1+.4*(r/max(1,r+p))
        else: s=s1
        s=min(.99,max(.01,s+reg_shift(u)))
        out[u]=s;wt[u]=v.get('LLA',0)+v.get('UXP',0)
    nat=sum(out[u]*wt[u] for u in out)/sum(wt.values())
    import math
    lg=lambda p:math.log(p/(1-p));sw=lg(tgt)-lg(nat)
    return {u:round(100/(1+math.exp(-(lg(min(.99,max(.01,s)))+sw))),1) for u,s in out.items()},tgt
res={'bloques':B,'colores':{'LLA':'#6C4C99','Peronismo':'#29B6F6','PRO_JxC':'#E8B800','Provincias Unidas':'#00897B','Izquierda':'#E2434B','Otros':'#9AA7B2'},
 'objetivo':{k:round(100*v,1) for k,v in (T or {}).items()},'encuestas':{'fuerzas':[nF,lastF],'candidatos':[nC,lastC],'balotaje':[nB,lastB]},'icg':fit,'ajuste_regional':ICGD and {r:round(100*ICGD['region']['k']*v['relativo']/100,1) for r,v in ICGD['region']['datos'].items()},
 'senado2027':['10','26','14','18','42','50','82','90'],'gob2027':['06','10','14','22','26','30','34','38','42','46','50','54','58','62','66','70','74','78','82','90','94','02']}
if T:
    res['general']={'prov':project('prov')[0],'dep':project('dep')[0]}
bp=project_bal('prov');bd=project_bal('dep')
if bp: res['balotaje']={'prov':bp[0],'dep':bd[0],'objetivo':round(100*bp[1],1)}
open(D+'proyeccion.js','w',encoding='utf-8').write('const PROY='+json.dumps(res,ensure_ascii=False,separators=(',',':')))
print('objetivo',res['objetivo'],'icg',fit and {k:round(v,2) if isinstance(v,float) else v for k,v in fit.items()},'bal',res.get('balotaje',{}).get('objetivo'))
