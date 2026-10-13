#!/usr/bin/env python3
"""27 illustrative PVT cases; hand-defined model variants, not foundry corners."""
import itertools,json,re,shutil,os
from regression import ROOT,run
exe=os.environ.get('NGSPICE') or shutil.which('ngspice')
if not exe: raise SystemExit('Install ngspice; no analog metrics generated.')
template=(ROOT/'analog/ring_oscillator.cir.in').read_text()
corners={'slow':(.8,.55),'typical':(1.,.5),'fast':(1.2,.45)}; rows=[]
for (corner,(speed,vto)),voltage,temp in itertools.product(corners.items(),[1.62,1.8,1.98],[-40,25,125]):
 name=f'{corner}_{voltage}_{temp}'; d=ROOT/'build/analog';d.mkdir(parents=True,exist_ok=True)
 s=template
 for key,value in dict(VDD=voltage,TEMP=temp,VTO=vto,KPN=200e-6*speed,KPP=100e-6*speed).items(): s=s.replace('@'+key+'@',str(value))
 p=d/f'{name}.cir';p.write_text(s)
 out=run([exe,'-b',str(p)],ROOT/f'reports/analog_{name}.log')
 def metric(key):
  match=re.search(r'^'+key+r'\s*=\s*([\deE+.-]+)',out,re.M)
  if not match: raise RuntimeError(f'missing {key}: {name}')
  return float(match[1])
 period=metric('period'); current=metric('avg_supply_current'); assert period>0
 rows.append(dict(corner=corner,voltage_V=voltage,temperature_C=temp,frequency_Hz=1/period,power_W=-voltage*current))
 print(name,round(1/period/1e9,3),'GHz',flush=True)
(ROOT/'reports/analog.json').write_text(json.dumps(dict(model='Illustrative LEVEL=1 CMOS; hand-varied KP/VTO, not PDK process corners',cases=rows),indent=2))
