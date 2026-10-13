# Measured results

Run date: 2026-10-13 UTC. AI-assisted implementation and execution.

## RTL regression

- Random matrices: 21,600; directed matrices: 126; zero mismatches.
- Configurations: 18; bins: 264/270 (97.78%).
- Four SVA definitions per PE; 234 reset-abort/recovery trials.
- Three deliberate mutations detected (two RTL faults, one producer-schedule fault).

| N | Product pipeline | Simulation period (ns) | Random | Directed | Bins |
|---|---|---|---|---|---|
| 2 | 0 | 4 | 1200 | 7 | 14/15 |
| 2 | 0 | 6 | 1200 | 7 | 14/15 |
| 2 | 0 | 10 | 1200 | 7 | 14/15 |
| 2 | 1 | 4 | 1200 | 7 | 14/15 |
| 2 | 1 | 6 | 1200 | 7 | 14/15 |
| 2 | 1 | 10 | 1200 | 7 | 14/15 |
| 4 | 0 | 4 | 1200 | 7 | 15/15 |
| 4 | 0 | 6 | 1200 | 7 | 15/15 |
| 4 | 0 | 10 | 1200 | 7 | 15/15 |
| 4 | 1 | 4 | 1200 | 7 | 15/15 |
| 4 | 1 | 6 | 1200 | 7 | 15/15 |
| 4 | 1 | 10 | 1200 | 7 | 15/15 |
| 8 | 0 | 4 | 1200 | 7 | 15/15 |
| 8 | 0 | 6 | 1200 | 7 | 15/15 |
| 8 | 0 | 10 | 1200 | 7 | 15/15 |
| 8 | 1 | 4 | 1200 | 7 | 15/15 |
| 8 | 1 | 6 | 1200 | 7 | 15/15 |
| 8 | 1 | 10 | 1200 | 7 | 15/15 |

Coverage bins are defined in README. Six negative-overflow bins for N=2 are unreachable and retained in the denominator. Simulation clocks are not timing-closure measurements.

## Technology-independent synthesis

YoWASP Yosys 0.69.0.0.post1233, `synth -flatten -noabc`, `check -assert`. Scope metadata cells are excluded. No standard-cell mapping or physical implementation.

| N | Pipeline | Generic primitives | Register bits |
|---|---|---|---|
| 2 | 0 | 2,865 | 160 |
| 2 | 1 | 2,929 | 224 |
| 4 | 0 | 11,521 | 704 |
| 4 | 1 | 11,777 | 960 |
| 8 | 0 | 46,209 | 2,944 |
| 8 | 1 | 47,233 | 3,968 |

## Analog companion

ngspice 42 completed 27 model/voltage/temperature combinations using illustrative LEVEL=1 CMOS models.
No foundry process corners or silicon frequency claim. Supply voltages: 1.62/1.8/1.98 V; temperatures: -40/25/125 C. KP factors: 0.8/1/1.2; VTO magnitudes: 0.55/0.50/0.45 V.

| Model variant | VDD (V) | Temp (C) | Simulated frequency (GHz) | Simulated power (mW) |
|---|---|---|---|---|
| slow | 1.62 | -40 | 4.047 | 0.5313 |
| slow | 1.62 | 25 | 3.352 | 0.4406 |
| slow | 1.62 | 125 | 2.872 | 0.3803 |
| slow | 1.8 | -40 | 5.155 | 0.8363 |
| slow | 1.8 | 25 | 4.161 | 0.6763 |
| slow | 1.8 | 125 | 3.435 | 0.5642 |
| slow | 1.98 | -40 | 6.312 | 1.2404 |
| slow | 1.98 | 25 | 4.998 | 0.9852 |
| slow | 1.98 | 125 | 4.011 | 0.7996 |
| typical | 1.62 | -40 | 5.615 | 0.7373 |
| typical | 1.62 | 25 | 4.617 | 0.6075 |
| typical | 1.62 | 125 | 3.913 | 0.5211 |
| typical | 1.8 | -40 | 7.044 | 1.1437 |
| typical | 1.8 | 25 | 5.656 | 0.9213 |
| typical | 1.8 | 125 | 4.631 | 0.7644 |
| typical | 1.98 | -40 | 8.528 | 1.6781 |
| typical | 1.98 | 25 | 6.725 | 1.3297 |
| typical | 1.98 | 125 | 5.360 | 1.0756 |
| fast | 1.62 | -40 | 7.445 | 0.9790 |
| fast | 1.62 | 25 | 6.081 | 0.8025 |
| fast | 1.62 | 125 | 5.102 | 0.6836 |
| fast | 1.8 | -40 | 9.211 | 1.4976 |
| fast | 1.8 | 25 | 7.358 | 1.2027 |
| fast | 1.8 | 125 | 5.976 | 0.9937 |
| fast | 1.98 | -40 | 11.034 | 2.1772 |
| fast | 1.98 | 25 | 8.666 | 1.7201 |
| fast | 1.98 | 125 | 6.862 | 1.3873 |

## Not measured

STA, WNS, Fmax, critical-path improvement, mapped silicon area, digital power, routed utilization, congestion onset, and DRC are not measured. A full PPA sweep remains pending a PDK-equipped implementation environment.

## Source hashes (SHA-256)

- `rtl/mac_pe.sv`: `9274029d104dbb1044efa08948b15e85b59eac6c3bd3428423ba80aaf5c4ab4b`
- `rtl/systolic_array.sv`: `3c131879c7f418fdae78347ed211115e46f2ec6c85bb44abf934927ba3910f6b`
- `tb/tb.sv`: `bb03239353e2f532e0557ec5503d339a87dc8c492a94bde1f885b15fc379580a`
