#!/usr/bin/env python3
"""Actual RTL regression: independent NumPy matrix multiply, subprocess Verilator."""
import argparse, json, subprocess, pathlib, shutil, time
import numpy as np
ROOT=pathlib.Path(__file__).resolve().parents[1]
for directory in ['reports','build','vectors','physical']: (ROOT/directory).mkdir(exist_ok=True)
def run(cmd,log):
 p=subprocess.run(cmd,cwd=ROOT,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
 log.write_text(p.stdout)
 if p.returncode: raise RuntimeError(f'{cmd[0]} failed; see {log}')
 return p.stdout

def vectors(n,seed,random_count,path):
 rng=np.random.default_rng(seed); cases=[]
 z=np.zeros((n,n),dtype=np.int64); eye=np.eye(n,dtype=np.int64)
 cases += [('zero',z,z),('identity',eye,rng.integers(-128,128,(n,n))),
           ('min_min',np.full((n,n),-128),np.full((n,n),-128)),
           ('max_max',np.full((n,n),127),np.full((n,n),127)),
           ('min_max',np.full((n,n),-128),np.full((n,n),127)),
           ('alternating',np.fromfunction(lambda i,j:np.where((i+j)%2,127,-128),(n,n),dtype=int),np.full((n,n),127)),
           ('sparse',eye*-128,eye*127)]
 for k in range(random_count):
  if k%3==0:
   a=rng.integers(-128,128,(n,n)); b=rng.integers(-128,128,(n,n)); tag='uniform'
  elif k%3==1:
   a=rng.choice([-128,-1,0,1,127],(n,n)); b=rng.choice([-128,-1,0,1,127],(n,n)); tag='boundary'
  else:
   a=rng.integers(-128,128,(n,n))*(rng.random((n,n))<.2)
   b=rng.integers(-128,128,(n,n))*(rng.random((n,n))<.2); tag='random_sparse'
  cases.append((tag,a,b))
 seen=set(); lines=[]
 for tag,a,b in cases:
  c=a.astype(np.int64)@b.astype(np.int64)
  seen.add('class:'+tag)
  for label,mask in [('negative',c<0),('zero',c==0),('positive',c>0)]:
   if mask.any(): seen.add('result:'+label)
  for label,mask in [('below_int16',c<-32768),('above_int16',c>32767)]:
   if mask.any(): seen.add('range:'+label)
  lines.append(' '.join(map(str,np.concatenate([a.ravel(),b.ravel(),c.ravel()]))))
 path.write_text('\n'.join(lines)+'\n')
 return len(cases),seen

def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--random',type=int,default=1200); args=ap.parse_args()
 verilator=shutil.which('verilator') or shutil.which('verilator-cli') or str(pathlib.Path.home()/'.local/bin/verilator-cli')
 results=[]; start=time.time()
 for n in [2,4,8]:
  for pipe in [0,1]:
   build=ROOT/f'build/n{n}_p{pipe}'; build.mkdir(parents=True,exist_ok=True)
   run([verilator,'--binary','--timing','--assert','--no-sched-zero-delay','--top-module','tb',f'-GN={n}',f'-GPIPE={pipe}',
       '--Mdir',str(build),'-j','2','rtl/mac_pe.sv','rtl/systolic_array.sv','tb/tb.sv'],ROOT/f'reports/build_n{n}_p{pipe}.log')
   for half in [2,3,5]:
    seed=530000+n*1000+pipe*100+half
    name=f'n{n}_p{pipe}_h{half}'; vf=ROOT/f'vectors/{name}.txt'
    count,bins=vectors(n,seed,args.random,vf)
    out=run([str(build/'Vtb'),f'+VECTORS={vf}',f'+HALF={half}'],ROOT/f'reports/{name}.log')
    assert f'TESTS={count}' in out and 'PASS' in out
    results.append(dict(n=n,pipe=pipe,period_ns=half*2,seed=seed,random_tests=args.random,directed_tests=7,
                        pass_tests=count,coverage_bins_hit=sorted(bins),coverage_bins_total=15))
    print(name,'PASS',count,'coverage',len(bins),'/15',flush=True)
 (ROOT/'reports/results.json').write_text(json.dumps(dict(configurations=results,elapsed_seconds=time.time()-start,
   random_tests=sum(r['random_tests'] for r in results),directed_tests=sum(r['directed_tests'] for r in results),
   coverage_note='15 predeclared bins per configuration: 10 input families, 3 output signs, 2 signed-16-bit overflow ranges. Credited only after RTL scoreboard passes. Not code/toggle/industrial coverage.',
   timing_note='Simulation clock periods only; no STA, PPA or timing closure measured.'),indent=2))
if __name__=='__main__': main()
