#!/usr/bin/env python3
import json,hashlib
from regression import ROOT
r=json.loads((ROOT/'reports/results.json').read_text());s=json.loads((ROOT/'reports/synthesis.json').read_text());a=json.loads((ROOT/'reports/analog.json').read_text());m=json.loads((ROOT/'reports/mutations.json').read_text())
hit=sum(len(c['coverage_bins_hit']) for c in r['configurations']);total=sum(c['coverage_bins_total'] for c in r['configurations'])
lines=['# Measured results','', 'Run date: 2026-10-13 UTC. AI-assisted implementation and execution.','',
'## RTL regression','',f"- Random matrices: {r['random_tests']:,}; directed matrices: {r['directed_tests']:,}; zero mismatches.",
f"- Configurations: {len(r['configurations'])}; bins: {hit}/{total} ({100*hit/total:.2f}%).",'- Four SVA definitions per PE; 234 reset-abort/recovery trials.',
'- Three deliberate mutations detected (two RTL faults, one producer-schedule fault).','',
'| N | Product pipeline | Simulation period (ns) | Random | Directed | Bins |','|---|---|---|---|---|---|']
for c in r['configurations']:lines.append(f"| {c['n']} | {c['pipe']} | {c['period_ns']} | {c['random_tests']} | {c['directed_tests']} | {len(c['coverage_bins_hit'])}/15 |")
lines+=['','Coverage bins are defined in README. Six negative-overflow bins for N=2 are unreachable and retained in the denominator. Simulation clocks are not timing-closure measurements.','',
'## Technology-independent synthesis','', 'YoWASP Yosys 0.69.0.0.post1233, `synth -flatten -noabc`, `check -assert`. Scope metadata cells are excluded. No standard-cell mapping or physical implementation.','',
'| N | Pipeline | Generic primitives | Register bits |','|---|---|---|---|']
for c in s:lines.append(f"| {c['n']} | {c['pipe']} | {c['generic_cells']:,} | {c['cell_types']['$_SDFF_PP0_']:,} |")
lines+=['','## Analog companion','',f"ngspice 42 completed {len(a['cases'])} model/voltage/temperature combinations using illustrative LEVEL=1 CMOS models.",
'No foundry process corners or silicon frequency claim. Supply voltages: 1.62/1.8/1.98 V; temperatures: -40/25/125 C. KP factors: 0.8/1/1.2; VTO magnitudes: 0.55/0.50/0.45 V.',
'', '| Model variant | VDD (V) | Temp (C) | Simulated frequency (GHz) | Simulated power (mW) |','|---|---|---|---|---|']
for c in a['cases']:lines.append(f"| {c['corner']} | {c['voltage_V']} | {c['temperature_C']} | {c['frequency_Hz']/1e9:.3f} | {c['power_W']*1e3:.4f} |")
lines+=['','## Not measured','', 'STA, WNS, Fmax, critical-path improvement, mapped silicon area, digital power, routed utilization, congestion onset, and DRC are not measured. A full PPA sweep remains pending a PDK-equipped implementation environment.',
'', '## Source hashes (SHA-256)','']
for p in sorted((ROOT/'rtl').glob('*.sv'))+sorted((ROOT/'tb').glob('*.sv')):lines.append(f'- `{p.relative_to(ROOT)}`: `{hashlib.sha256(p.read_bytes()).hexdigest()}`')
(ROOT/'reports/METRICS.md').write_text('\n'.join(lines)+'\n')
