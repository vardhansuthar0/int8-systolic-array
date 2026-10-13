#!/usr/bin/env python3
"""Deliberately planted faults, never reported as bugs discovered in original RTL."""
import json,pathlib,shutil,subprocess
from regression import ROOT,run
v=shutil.which('verilator') or shutil.which('verilator-cli') or str(pathlib.Path.home()/'.local/bin/verilator-cli')
pe=(ROOT/'rtl/mac_pe.sv').read_text(); tb=(ROOT/'tb/tb.sv').read_text()
mutants={
 'unsigned_product':(pe.replace('a_in * b_in','$unsigned(a_in) * $unsigned(b_in)'),tb,0),
 'missing_acc_clear':(pe.replace('acc<=0;', 'acc<=acc;'),tb,0),
 'missing_pipeline_drain':(pe,tb.replace("3*N-2+int'(PIPE)",'3*N-2'),1)
}
records=[]
for name,(mut_pe,mut_tb,pipe) in mutants.items():
 d=ROOT/'build'/name; d.mkdir(parents=True,exist_ok=True)
 (d/'mac_pe.sv').write_text(mut_pe); (d/'tb.sv').write_text(mut_tb)
 run([v,'--binary','--timing','--assert','--no-sched-zero-delay','--top-module','tb','-GN=4',f'-GPIPE={pipe}',
 '--Mdir',str(d/'obj'),'-j','2',str(d/'mac_pe.sv'),'rtl/systolic_array.sv',str(d/'tb.sv')],ROOT/f'reports/mutant_{name}_build.log')
 p=subprocess.run([str(d/'obj/Vtb'),f'+VECTORS={ROOT}/vectors/n4_p{pipe}_h2.txt','+HALF=2'],cwd=ROOT,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
 (ROOT/f'reports/mutant_{name}.log').write_text(p.stdout)
 detected=p.returncode!=0 and ('MISMATCH' in p.stdout or 'Assertion failed' in p.stdout)
 records.append(dict(mutation=name,detected=detected,returncode=p.returncode,diagnostic=p.stdout.splitlines()[:3]))
 print(name,'DETECTED' if detected else 'MISSED',flush=True)
(ROOT/'reports/mutations.json').write_text(json.dumps(records,indent=2))
assert all(x['detected'] for x in records)
