# Parameterized INT8 systolic array

An SystemVerilog implementation with executable RTL regression, a NumPy reference, simulation assertions, mutation testing, and an illustrative CMOS ring oscillator.

## Architecture

`rtl/systolic_array.sv` instantiates N × N `mac_pe` cells. Each cell forwards signed 8-bit A to the right and B downward, multiplying in 16 bits and accumulating in signed 32 bits. `PIPE=1` inserts a product register before the accumulator. This is product pipelining, not an experimentally demonstrated retiming or timing-closure improvement.

The interface is deliberately a streaming core: the producer supplies skewed edges, issues `clear`, and counts cycles. It does not contain a DMA, matrix buffer, ready/valid protocol, or autonomous scheduler. The testbench implements the producer.

### Cycle contract

1. Assert synchronous active-high `rst` or `clear` for one rising edge; all PE state clears.
2. At edge index t starting at zero, row i receives `A[i,t-i]` and column j receives `B[t-j,j]`, substituting zero for out-of-range indices.
3. Sample results after **3N − 2 + PIPE** rising edges (excluding clear). Result `(i,j)` occupies `result[(i*N+j)*32 +: 32]`.
4. Feed zero during idle cycles. Clear before the next matrix. Reset may abort an operation.

Tested sizes: 2, 4, 8. The generator parameter is not an assertion that every N has been tested. With N≤8, complete INT8 dot products fit comfortably in 32 bits. Accumulation wraps modulo 2^32 if the producer streams a longer workload that overflows.

## Reproduce

Linux, Python 3.10+, NumPy, GNU C++, make, and a recent Verilator with timing and SVA support:

```sh
python3 -m pip install -r requirements.txt
python3 scripts/regression.py
python3 scripts/mutation_test.py
python3 -m pip install -r requirements-synthesis.txt
python3 scripts/synthesis.py   # Native Yosys or YoWASP fallback
python3 scripts/analog_sweep.py # Requires ngspice or NGSPICE=/absolute/path/ngspice
```

`verilator` or `verilator-cli` must be on PATH. For a pip user install, add `$HOME/.local/bin` to PATH. The full regression performs 1,200 newly seeded random matrix pairs and seven directed pairs per configuration. Each pair is one test of all N² result entries. Seeds and per-configuration results are recorded in `reports/results.json`. Generated vectors and compiled objects are reproducible and excluded from git.

## Verified digital results

- 21,600 constrained-random matrix tests and 126 directed tests, all matching NumPy integer matrix multiplication.
- 18 simulation configurations: N={2,4,8} × PIPE={0,1} × period={4,6,10} ns.
- Four SVA property definitions per PE: reset/clear, A forwarding, B forwarding, and accumulator update; up to 256 instantiated assertions in the 8×8 array. These are simulation checks, not formal proofs.
- 234 reset-abort/recovery trials, included in the regression.
- All three deliberate mutations detected: unsigned product, omitted accumulator clear, and a testbench schedule missing the pipelined drain edge. The third is a driver/protocol mutation, not an RTL mutation. No claim of three organically discovered RTL bugs is made.
- 264/270 defined functional bins hit, **97.78% raw bin coverage**. This is a small project-specific functional coverage plan, not line, toggle, FSM, or commercial verification signoff coverage.

### Coverage definition

15 bins per configuration: ten input families (zero, identity, min×min, max×max, min×max, alternating, sparse diagonal, uniform random, boundary-biased random, random sparse); three output signs; output below −32768 and above 32767. Bins receive credit only if every corresponding RTL scoreboard run succeeds. There are 270 configuration-crossed bins total.

The six unhit bins are `result < -32768` for the six N=2 configurations. They are unreachable: two INT8 products cannot sum below −32512. We retain them in the raw denominator rather than silently excluding them. Every reachable bin is exercised. This limited plan does not cover every operand combination or microarchitectural event.

Six technology-independent synthesis runs completed successfully. The 8x8 baseline/pipelined variants contain 46,209/47,233 generic primitives (metadata excluded). These are not standard-cell area measurements.

## Implementation status and limitations

Simulation clock periods do **not** demonstrate achievable frequency. No foundry library, parasitic extraction, routed design, signoff DRC, STA WNS, congestion onset, silicon area, or power result has been established for this array. Therefore no 200–400 MHz, positive WNS, 15–30% path improvement, 55–70% routed utilization, or zero-DRC claim is supported.

`physical/` contains reproducible technology-independent synthesis scripts. Generic primitive counts must not be called silicon area. A real PPA sweep still requires an installed physical implementation flow and a licensed/available PDK with LEF, Liberty, RC, and routing rules. The 18-run matrix is a **functional regression sweep**, not a PPA sweep.

## Analog companion

`analog/ring_oscillator.cir.in` is a five-stage CMOS ring oscillator. `scripts/analog_sweep.py` sweeps 3 hand-defined transistor model variants × 3 voltages × 3 temperatures. LEVEL=1 models are illustrative; slow/typical/fast vary KP and VTO manually. They are not foundry-characterized process corners, and their frequencies must not be presented as node-qualified silicon performance. See `reports/analog.json` if the run completed.

## Evidence

`reports/results.json`, run logs, `mutations.json`, synthesis summaries, and analog logs retain evidence. `reports/METRICS.md` consolidates completed runs and limitations. Commands fail on scoreboard errors or missing measurements. Code was generated with AI assistance and tested in the accompanying environment; review the design and reproduce the runs before describing personal design experience in an interview.
