# Synthesis and physical implementation status

Run `python3 scripts/synthesis.py` from the repository. Install the optional `requirements-synthesis.txt` to reproduce the recorded YoWASP build. Generated .ys files specialize N and PIPE via a generated source copy because this YoWASP version raised an internal error with chparam/hierarchy parameter override. The original RTL is not edited. Six flattened generic syntheses pass `check -assert`.

The flow explicitly disables ABC mapping (`-noabc`). It produces generic Boolean gates and register bits, not foundry cells. Metadata `$scopeinfo` objects are excluded from counts. Counts depend on tool version and optimization settings.

No route/STA/PPA results exist yet. To finish that stage, select an available platform in an OpenROAD-based flow, provide its standard-cell Liberty/LEF and RC data, constrain input/output timing and the clock, synthesize/map both pipeline variants, run floorplan/place/CTS/route, then extract setup/hold WNS, area, power, congestion and DRC from actual reports. Keep voltage, temperature, output load and timing constraints identical for before/after comparisons. Sweep at least three sizes and three target clock periods. A fixed utilization target is not evidence of routed utilization or congestion onset.

This directory does not contain an untested pretend physical-flow wrapper.
