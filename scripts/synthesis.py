#!/usr/bin/env python3
"""Technology-independent synthesis only. Cell counts are not silicon area."""
import pathlib,shutil,json,re,os
from regression import ROOT,run
yosys=os.environ.get('YOSYS') or shutil.which('yosys') or shutil.which('yowasp-yosys') or '/root/.local/bin/yowasp-yosys'
summary=[]
for n in [2,4,8]:
 for pipe in [0,1]:
  name=f'n{n}_p{pipe}'
  # Specialize source defaults to avoid a parameter-elaboration regression in YoWASP 0.69.
  source=(ROOT/'rtl/systolic_array.sv').read_text().replace('parameter int N=4',f'parameter int N={n}').replace('parameter bit PIPE=0',f'parameter bit PIPE={pipe}')
  (ROOT/f'build/array_{name}.sv').write_text(source)
  script=f'read_verilog -sv -DSYNTHESIS rtl/mac_pe.sv build/array_{name}.sv; synth -top systolic_array -flatten -noabc; check -assert; stat; write_json reports/synth_{name}.json'
  (ROOT/f'physical/synth_{name}.ys').write_text(script+'\n')
  run([yosys,'-Q','-T','-p',script],ROOT/f'reports/synth_{name}.log')
  net=json.loads((ROOT/f'reports/synth_{name}.json').read_text())
  cells=net['modules']['systolic_array']['cells']; counts={}
  for c in cells.values():
   if c['type']=='$scopeinfo': continue # metadata, not a logic primitive
   counts[c['type']]=counts.get(c['type'],0)+1
  summary.append(dict(n=n,pipe=pipe,generic_cells=sum(counts.values()),cell_types=counts))
  print(name,sum(counts.values()),'generic cells',flush=True)
(ROOT/'reports/synthesis.json').write_text(json.dumps(summary,indent=2))
