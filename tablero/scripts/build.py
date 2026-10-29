import openpyxl,datetime,json,collections,sys
U=sys.argv[1]; SH=sys.argv[2]; META=sys.argv[3]
def dt(v):
  if isinstance(v,(datetime.date,datetime.datetime)): return v.strftime("%Y-%m-%d")
  return str(v)[:10] if v else ""
WB={c:openpyxl.load_workbook(f"{SH}/{c}.xlsx",read_only=True,data_only=True) for c in ["brooklyn","begbarker","ayoba","granite"]}
rows=lambda c,t: list(WB[c][t].iter_rows(values_only=True))
def agg(c,tab,a="2026-10-01",b=U):
  out=collections.defaultdict(lambda:[0,0,0,0,0])
  for r in rows(c,tab)[1:]:
    if a<=dt(r[0])<=b:
      for i in range(5): out[r[1]][i]+=r[2+i] if isinstance(r[2+i],(int,float)) else 0
  return out
old=json.load(open("datos/campanas.json"))
def findold(cl,canal,name):
  for o in old:
    if o['cliente']==cl and o['canal']==canal and o['campana']==name: return o
  return {}
meta=json.load(open(META))
ST={"ACTIVE":"Activa","PAUSED":"Pausada","COMPLETED":"Finalizada 18-oct (programada)"}
special={"Beg_FlashSale":"Finalizada 25-oct","Ayoba_FlashSale":"Finalizada 25-oct (programada)","Brooklyn_FlashSale":"Finalizada 18-oct (programada)"}
B={"brooklyn":"Brooklyn Biltong","begbarker":"Beg & Barker","ayoba":"Ayoba","granite":"Granite"}
d1=int(U[-2:]); lab=f"1–{d1} oct"
out=[]
def mk(cl,canal,name,est,inv,imp,clk,conv,val,fuente,hoja=None):
  o=findold(cl,canal,name)
  r={"cliente":cl,"canal":canal,"campana":name,"estado":est or o.get("estado","Activa"),"objetivo":o.get("objetivo","Ventas" if canal=="Meta" else ""),
     "inversion":round(inv,2),"impresiones":int(imp),"clics":int(clk),"conversiones":round(conv,2),"valor":round(val,2),"fuente":fuente}
  if hoja is not None:
    r["inversion_hoja"]=round(hoja,2); r["dif_pct"]=round(abs(inv-hoja)/inv*100,2) if inv else 0
    r["verificacion"]="Cuadra" if r["dif_pct"]<1 else "Revisar"
  else: r["verificacion"]="Solo hoja (sin MCC)" if canal=="Google" else "Solo hoja (sin acceso a Meta)"
  r["ctr"]=round(clk/imp,4) if imp else None; r["cpc"]=round(inv/clk,2) if clk else None
  r["cpa"]=round(inv/conv,2) if conv else None; r["roas"]=round(val/inv,2) if inv else None
  r["id"]=cl[:2]+"|"+canal+"|"+name; out.append(r)
for c,cl in B.items():
  for k,v in agg(c,"Hist Google").items():
    if v[0]>0: mk(cl,"Google",k,findold(cl,"Google",k).get("estado","Activa"),*v,f"Hoja (Hist Google), {lab}")
  hm=agg(c,"Hist Meta")
  if c=="granite":
    for k,v in hm.items():
      if v[0]>0: mk(cl,"Meta",k,None,*v,f"Hoja (Hist Meta), {lab}")
  else:
    for name,st,inv,imp,clk,conv,val in meta[cl]:
      mk(cl,"Meta",name,special.get(name,ST[st]),inv,imp,clk,conv,val,f"API Meta + hoja, {lab}",hm[name][0] if name in hm else None)
lb=findold("Beg & Barker","Meta","Beg_LaborDay")
if lb: lb=dict(lb); lb["estado"]="Pausada"; out.append(lb)
assert len({r['id'] for r in out})==len(out)
print("revisar:",[(r['campana'],r['inversion'],r.get('inversion_hoja')) for r in out if r['verificacion']=="Revisar"])
json.dump(out,open("datos/campanas.json","w"),ensure_ascii=False)
def ch(c,tab,a,b):
  r2=collections.defaultdict(lambda:[0,0]); R=rows(c,tab); h=R[0]
  for r in R[1:]:
    if a<=dt(r[0])<=b: r2[r[1]][0]+=r[h.index('total_sales')] or 0; r2[r[1]][1]+=r[h.index('orders')] or 0
  return r2
T=[];tot={}
SU="2026-09-"+U[-2:]
for c,cl,tab in [("brooklyn","Brooklyn Biltong","Shopify Diario"),("granite","Granite","Shopify Diario"),("ayoba","Ayoba","Shopify Diario"),("begbarker","Beg & Barker","Tienda Diario")]:
  o=ch(c,tab,"2026-10-01",U); s=ch(c,tab,"2026-09-01",SU)
  for k in set(o)|set(s): T.append({"cliente":cl,"canal_venta":k,"ventas_oct":round(o[k][0],2),"pedidos_oct":o[k][1],"ventas_sep":round(s[k][0],2),"pedidos_sep":s[k][1]})
  vo=sum(v[0] for v in o.values()); vs=sum(v[0] for v in s.values()); tot[cl]=(round(vo),sum(v[1] for v in o.values()),round(vs),round((vo/vs-1)*100,1))
  oo=o.get("Online Store",[0,0]); so=s.get("Online Store",[0,0]); print(cl,"online",round(oo[0]),round(so[0]),round((oo[0]/so[0]-1)*100,1))
print("TOT",tot)
json.dump(T,open("datos/tienda.json","w"),ensure_ascii=False)
dd=ch("brooklyn","Shopify Diario","2026-10-01",U)
R=rows("brooklyn","Shopify Diario"); h=R[0]; dd=collections.defaultdict(lambda:[0,0])
for r in R[1:]:
  d=dt(r[0])
  if "2026-10-01"<=d<=U: dd[d][0]+=r[h.index('total_sales')] or 0; dd[d][1]+=r[h.index('orders')] or 0
promo={d:"Fast Sale" for d in ["2026-10-15","2026-10-16","2026-10-17","2026-10-18"]}
json.dump([{"dia":d,"ventas":round(v[0],2),"pedidos":v[1],"promo":promo.get(d,""),"fuente":"Shopify (hoja, verificado con API)"} for d,v in sorted(dd.items())],open("datos/bk_diario.json","w"),ensure_ascii=False)
P=[]
for c,cl,tab in [("begbarker","Beg & Barker","Tienda Diario"),("ayoba","Ayoba","Shopify Diario")]:
  R=rows(c,tab); h=R[0]; d2=collections.defaultdict(lambda:[0,0,0])
  for r in R[1:]:
    d=dt(r[0])
    if "2026-10-01"<=d<=U: x=d2[d]; x[0]+=r[h.index('total_sales')] or 0; x[1]+=r[h.index('orders')] or 0; x[2]+=r[h.index('discounts')] or 0
  for d,v in sorted(d2.items()): P.append({"id":cl[:3]+"|"+d,"marca":cl,"dia":d,"ventas":round(v[0],2),"pedidos":v[1],"descuentos":round(-v[2],2),"promo":"Promo" if "2026-10-21"<=d<="2026-10-25" else ""})
json.dump(P,open("datos/promo_diario.json","w"),ensure_ascii=False)
for c in B:
  g=collections.defaultdict(float)
  for r in rows(c,"Hist Google")[1:]:
    if "2026-10-20"<=dt(r[0])<=U: g[dt(r[0])]+=r[2] if isinstance(r[2],(int,float)) else 0
  print(c,"google diario",{k[5:]:round(v) for k,v in sorted(g.items())})
sm=agg("brooklyn","Hist Google","2026-10-26",U); print("smile 26-27",round(sm["Brooklyn_PmaxExcludedW10SmileProgram"][0],2))
