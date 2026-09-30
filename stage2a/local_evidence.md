# Stage 2a: comparability audit of local evidence

| Item | Value |
|---|---|
| Written | 2026-09-30 |
| Scope | Model-quality, cost, latency and capacity evidence that already exists on this Tokyo machine. This audit made no model or Jev API calls and did not ssh anywhere. Existing files were not modified. |
| Machine-readable | `local_evidence.jsonl`: 50 rows, one per result set x model. Result-set ids S01–S20. |
| Recomputation | The 9/23 numbers were recomputed from the raw `log.jsonl` and EvalPlus `*_eval_results.json` files, using a scratch script that re-implements `exp_report.py` / `exp_math.py summarise()`. Every recomputed number matches the REPORT.md files. |
| Price check | I recomputed `charged_micro` from the usage tokens at the Table 2 prices below. It matches (±1.5 micro) on 98% of 9/23 rows: kimi 957/975, deepseek 1,137/1,138, glm 407/413. Pricing was therefore unchanged from 9/13 to 9/23. |

Evidence levels used in this audit:

- **A**: exact model on Engy, exact benchmark, same or comparable harness and window, clear parameters, clear scorer, traceable raw data.
- **B**: candidate screening only.
- **C**: reference only.
- **INVALID**: not usable, with the reason stated.

Strict rule applied: a partial sample, a binding self-set output cap, or infra contamination disqualifies a result from A.

**Rule conflict to settle.** `EXISTING_RESULTS_INVENTORY.md` (R12–R17) applies the user's 9/29 rule ("all benchmark results before 2026-09-29 are invalid") to the 9/23 experiment and to the TrajectoryRL doc as well. This audit follows the caller's instruction to judge both on their own merits. The one A below is therefore **provisional until the user confirms that the 9/29 rule covers only the Jev benchmark runs of 9/27–9/28.**

---

## Prices (USD per 1M tokens)

| Model | Input | Output | Cache read | Source |
|---|---|---|---|---|
| deepseek-v4.1-flash | 0.040 | 0.080 | 0.008 | FUSION Table 2; `run_ab.sh`; matches 9/23 and 9/30 `charged_micro` |
| deepseek-v4-flash-0731 | 0.045 | 0.090 | 0.009 (not verified) | No local doc records this price. Input and output rates were **verified from the 9/30 probe charges**: 828,311 prompt tokens → 37,275 micro (0.045/M); 826,950 prompt + 49 output → 37,217 micro (implies 0.09/M output). The cache rate is unverified. |
| qwen3.8-27b | 0.045 | 0.320 | 0.015 | FUSION Table 2 |
| glm-5.3-flash | 0.135 | 0.450 | 0.027 | FUSION Table 2; `run_ab.sh`; 9/30 probe (222,395 prompt tokens → 30,027 micro) |
| glm-5.2 | 0.680 | 1.500 | 0.180 | FUSION Table 2 |
| glm-5.3 | 0.980 | 3.080 | 0.180 | FUSION Table 2; `run_ab.sh`; 9/30 probe (281,535 prompt tokens → 275,929 micro; cached reads at 0.18) |
| kimi-k3 | 1.950 | 9.750 | 0.195 | FUSION Table 2; `run_ab.sh`; 9/23 rows match exactly |
| qwen3.6-35b-a3b | — | — | — | No local price and no local results |

---

## S01–S12: 9/23 auto-routing experiment (`/root/h3_work/auto/`)

**Common protocol**, confirmed from `exp_run.py`, `exp_math.py`, `exp_report.py` and the logs:

- Calls go directly to `api.engy.ai/v1/chat/completions`, non-streaming.
- Each request carries a system prompt plus a single user turn. There are no tools.
- `temperature` is 0.
- `reasoning_effort` is **not sent**, so each model runs at its provider default:
  - deepseek-v4.1-flash returns 0 reasoning tokens on every row, i.e. it runs in direct mode.
  - kimi-k3 runs with reasoning on (average 250–370 reasoning tokens).
  - glm-5.3-flash runs with thinking on.
- Output caps:
  - Code tasks: `max_tokens` 2048 (`EXP_MAX_TOKENS`, default 2048).
  - The code3-tier auto rerun (code4) allowed glm up to 6000. This is inferred from the maximum observed completion of 6000; the exact setting is UNVERIFIED.
  - Math tasks: `max_tokens` 6000.
- Client timeouts are 600 s (code) and 900 s (math), with up to 4 attempts.
- One rollout per task per arm.
- Cost is the gateway `charged_micro`, plus Jev at $0.042/M for the auto arm.
- Latency is non-stream wall time.

**Scorers:**

- Code: EvalPlus 0.3.1 run locally (HumanEvalPlus v0.1.10, MbppPlus v0.2.0), `plus_status`.
- Math: custom exact match on the last `\boxed{}` (falling back to the last number), with normalisation. This is not math-verify or the official scorer.

**Lineage** (checked by md5 and cmp):

| Final directory | Built from |
|---|---|
| `final/` | kimi = `run1/`, auto = `run2/` |
| `code_final/` | kimi = `code3/`, auto = `code4/` |
| `code_all/` | `code_final/` + ds = `code_ds/` |
| `math_all/` | kimi + auto = `math3/`, ds = `math_ds/` |

**Windows** (from log mtimes, all on 2026-09-23 CST; kimi arm first, deepseek arm later):

| Surface | kimi arm ended | deepseek arm ran | Gap |
|---|---|---|---|
| Code | 18:54 (code3) | about 19:40–19:53 (code_ds) | about 1 h |
| Math | 18:40 (math3) | ended 20:04 (math_ds) | about 1.4 h |

The kimi and deepseek arms were **not interleaved.** The experiment doc itself says "deepseek 组在单独补跑" (the deepseek arm was run separately to fill in). Auto and kimi were interleaved only within code3/math1/math3/run1; in the published 3-tier code result the auto arm (code4) came from a later rerun.

### S01 — code, deepseek-v4.1-flash only (code_ds) → **A (on its own merits, provisional)**

| Field | Value |
|---|---|
| n | 542, the full sets (HumanEval+ 164, MBPP+ 378) |
| Score | plus **83.9%** (455/542); base 94.1%; HumanEval+ 91.5%, MBPP+ 80.7% |
| Cost | **$0.0000095 per task** |
| Latency | average 1.46 s, p50 1.12 s, p95 3.19 s |
| Truncation | 0 `finish=length`. The largest completion was 911 tokens, so the 2048 cap never bound. |
| Failures | 0; 2 tasks were retried once |
| Raw data | `code_ds/log.jsonl`, `code_all/deepseek_*_eval_results.json` |

The same number (83.9%) was reported independently by TrajectoryRL on 9/13–18.

Caveats:

- It is a single rollout.
- It was not run in the kimi arm's window.
- It is subject to the rule conflict above.

Bucket: **coding + direct**.

### S02 — code, kimi-k3 only (code3) → **B**

| Field | Value |
|---|---|
| Score | plus 86.3% (468/542); base 96.5%; HumanEval+ 93.9%, MBPP+ 83.1% |
| Cost | $0.00392 per task |
| Latency | average 3.39 s, p95 11.4 s |

Why B:

- The self-set 2048 cap **bound on 12 of 542 tasks, and all 12 failed.**
- A replicate with the same configuration (S03, run1, 17:32) scored 84.1%, a run-to-run spread of 2.2 points.
- It was not run in the same window as S01.

The DS-vs-kimi gap of 2.4 points is therefore B-level only.

### S03 — code, kimi-k3 replicate (run1 = final/) → **C**

84.1% plus, $0.00379 per task, 10 truncations. Use it only as a variance reference.

### S04 — code, 3-tier auto rerun (code4): per-model subsets → **C**

Each model saw only the Jev-routed subset, not a random sample:

| Model | Tasks | Plus accuracy | Cost per task | Average latency | Notes |
|---|---|---|---|---|---|
| deepseek | 130 | 93.1% | — | — | |
| glm-5.3-flash | 409 | 83.9% | $0.00060 | 25.9 s | thinking on; 21 runs still hit 6000 tokens |
| kimi | 3 | 3/3 | — | — | |

The auto arm total was 86.2% at $0.00054 per task.

### S05 — code, 2-tier auto rerun (run2): per-model subsets → **C**

| Model | Tasks | Plus accuracy |
|---|---|---|
| deepseek | 513 | 85.0% |
| kimi | 29 | 72.4% (4 truncations) |

On the 513 tasks routed "simple", deepseek and kimi scored the same, 85.0% each. That comparison is reference only.

### S06 — first 3-tier auto (code3 auto) → **INVALID**

glm-5.3-flash hit the 2048 cap on 63 of 412 tasks. The experimenters voided this run themselves.

### S07 — run1 auto arm → **INVALID**

Jev fell back on 361 of 542 tasks, so routing was contaminated. Superseded by run2.

### S08 — smoke/, trial2/, math_smoke/ → **INVALID**

Partial or smoke runs only: 6 tasks, 8 tasks, and trial2 with no result files.

### S09 — math, deepseek-v4.1-flash only (math_ds) → **B**

| Field | Value |
|---|---|
| Score | **94.3%** (283/300); GSM8K 97.3%; MATH-500 91.3% (L1 100, L2 100, L3 94.4, L4 89.1, L5 78.6) |
| Cost | $0.0000375 per task |
| Latency | average 6.27 s, p95 21.3 s |
| Truncation | 2 at the 6000 cap, both wrong |

Why B:

- It uses a sampled subset (GSM8K 150 of 1319, MATH-500 150 of 500, seed 0).
- The scorer is a non-official exact-match scorer.
- The self-set cap bound on 2 tasks.
- Separate window from kimi.

Bucket: math + direct.

### S10 — math, kimi-k3 only (math3) → **B**

| Field | Value |
|---|---|
| Score | 94.7% (284/300); GSM8K 97.3%; MATH-500 92.0% (L5 71.4) |
| Cost | $0.00507 per task |
| Latency | average 4.84 s, p95 19.5 s |
| Truncation | 4 at 6000, all wrong |

A replicate 20 minutes earlier (math1, S11) scored 92.3%. **DS ≈ kimi on math is within noise.**

### S11 — math, kimi replicate (math1) → **C**

92.3% (GSM8K 94.7%, MATH-500 90.0%), 7 truncations. The log was regraded once; the pre-regrade copy is kept.

### S12 — math, auto arms: per-model subsets → **C**

| Arm | Model | Tasks | Accuracy |
|---|---|---|---|
| math3 (3-tier) | deepseek | 166 | 97.6% |
| math3 (3-tier) | kimi | 130 | 92.3% |
| math3 (3-tier) | glm-5.3-flash | 4 | 3/4 |
| math1 (2-tier) | deepseek | 166 | 95.8% |
| math1 (2-tier) | kimi | 134 | 91.8% |

---

## S13–S14: TrajectoryRL doc (`/root/FUSION_METHODS_AND_DATA.md`, 9/13–9/18) → **C, raw data not available locally**

The scripts the doc names are not on this machine (`route_proxy.py`, `council_sn11_run.py`, `council_cross.py`, `eval_pack.py`, `sandbox_harness.py`). What follows is only what the doc states.

### S13 — code surfaces (Table 4)

542 pooled HumanEval+/MBPP+ tasks, hidden EvalPlus plus suites, one sample each. The doc does not state temperature, max_tokens or reasoning settings, except for the reasoning on/off split on deepseek and qwen.

| Model | Accuracy | Cost per task | Latency per task | Output tokens |
|---|---|---|---|---|
| deepseek-v4.1-flash, no reasoning | 83.9% | $0.00001 | 3.9 s | 107 |
| deepseek-v4.1-flash, reasoning | 85.8% | $0.00007 | 20.8 s | 763 |
| qwen3.8-27b, no reasoning | 80.4% | $0.00007 | 3.5 s | 192 |
| qwen3.8-27b, reasoning | 83.9% | $0.00059 | 22.8 s | 1,828 |
| glm-5.3-flash | 86.5% | $0.00066 | 23.8 s | 1,434 |
| glm-5.2 | 83.0% | $0.00346 | 24.8 s | 2,254 |
| glm-5.3 | 85.6% | $0.00693 | 41.3 s | 2,214 |
| kimi-k3 | 86.2% | $0.00562 | 6.3 s | 539 |

Other code-surface figures in the doc:

- Oracle (cheapest correct per task): 92.8% at $0.00024.
- Best cascade, deepseek then kimi: 87.5% at $0.00099.

### S14 — agentic surfaces

Setup stated by the doc: sandbox-agent 4.0.23, Hermes 0.20.5, 600 s per episode, hidden shell verifiers.

| Model | Agentic-14 (two trials) | Agentic-35, pinned | Agentic-26 |
|---|---|---|---|
| deepseek-v4.1-flash | 10.68 / 11.55 | — | — |
| qwen3.8-27b | 11.30 / 11.30 | — | — |
| glm-5.3-flash | 11.50 / 11.30 | 28.68 (mean 24.96 over 6 council runs) | 22.60 |
| kimi-k3 | 11.65 / 11.35 ($6.48 / $7.13 per run) | 29.95 / 26.91 / 29.34 ($12–14 per run) | 22.84 |
| glm-5.3 | — | 24.44 | — |

The doc's own measured noise floor is 3.04 points on Agentic-35. The agentic harness and verifiers are not public, so this is not reproducible here.

**No local quality evidence exists for deepseek-v4-flash-0731, qwen3.6-35b-a3b or kimi-k3 in direct (non-reasoning) mode.** glm-5.3, glm-5.2 and qwen3.8-27b appear only in this doc, at Level C.

---

## S15–S18: this project's Jev benchmark runs (9/27–9/28) → **INVALID**

The user's 9/29 rule applies, and each run also has its own defect. Full details are in `EXISTING_RESULTS_INVENTORY.md` R01–R11.

| Run | Model | Defect |
|---|---|---|
| HLE R03 | deepseek-v4.1-flash | self-set 16K cap (19 of 48 hit it); 5 predictions missing; effort inconsistent; non-official judge |
| HLE R04 | kimi-k3 | 16K cap (29 of 100 hit it); 12 missing |
| HLE R06 | kimi-k3 | interrupted, 0 judged |
| HLE R07 | deepseek-v4.1-flash | aborted |
| HLE R05 | — | judge test only |
| AB R01 | kimi-k3 | 3 tasks |
| AB R08 | deepseek-v4.1-flash | 30 tasks, public set; 3 aborted tasks counted; 400/429 errors |
| AB R09, R10 | — | stopped or crashed |
| DeepSWE R02 | kimi-k3 | n=2; 4 GB memory; sampling parameters set |
| DeepSWE R11 | deepseek-v4.1-flash | n=1; Shenyang production; capacity 400 |

**S18, server-only results (not audited):** DeepSWE Auto b0/b0r/b0v2/b0v3/b0v4/bredo, the GLM full run, the server bandit rerun, the TB2 smoke, and the server proxy logs under `~/bench/{jobs,proxy/log}`. These are known only from `WORK_SUMMARY_2026-09-29.md` and `STATUS_2026-09-28.md`.

---

## S19–S20: serving capacity (capacity evidence, not quality)

Source: `stage1_5/context_capacity_probes.jsonl`, 9/30 13:36 CST. The gateway checks the prompt plus `max_tokens` against these caps. I derived the caps from the rejection texts.

| Model | Effective input cap | Output cap | Largest successful prompt | Live window | Notes |
|---|---|---|---|---|---|
| deepseek-v4.1-flash | **262,144** | 65,536 | 235,631 (29.7 s) | 1,048,576 | 263,404 + 65,536 was rejected. On 9/29, `ctx_test` still **accepted** 280,621 (105.8 s), so the cap was tightened afterwards. |
| deepseek-v4-flash-0731 | **920,576** | 128,000 | 828,311 (38.5 s) | 1,048,576 | 1,046,226 was rejected on 9/30. On 9/29 it **accepted** 1,042,101 (77.4 s) and rejected about 1.06M. The cap changed between the two probes. |
| glm-5.3-flash | **229,376** | 32,768 | 222,395 | 1,048,576 | `max_tokens` 65,536 was accepted rather than rejected, so the output cap is apparently clamped. |
| glm-5.3 | **294,912** | 32,768 | 281,535 | 1,048,575 | `max_tokens` 65,536 accepted (clamped). |
| kimi-k3 | about 1.05M total (input + output, upstream window 1,048,576) | — | no success in the probe set | — | Rejected at 1,056,206 + 8 and at 985,105 + 65,536. `/v1/models` on 9/29 listed 1,113,088; the gateway-limits doc cites 1,047,552 input. |

## Latency and throughput observations

These are completion tokens divided by non-stream wall time, for rows with more than 200 output tokens. Prefill time is included.

| Model | Condition | Median tok/s | Source |
|---|---|---|---|
| deepseek-v4.1-flash | 9/28, effort max, under HLE/AB load | 19.7–24.9 (p10 about 11–15) | `proxy/log/{hle,ab}-*-ds.jsonl` |
| deepseek-v4.1-flash | 9/28, concurrency-30 AB run (aborted) | 18.2 | same |
| deepseek-v4.1-flash | 9/23, default (direct), concurrency 8 | 84 | 9/23 logs |
| kimi-k3 | 9/28, effort max | 104–110 (p90 about 150–160) | `proxy/log/hle-*-k3`, `ab-pinned-k3` |
| kimi-k3 | 9/23 | 117–128 | 9/23 logs |
| glm-5.3-flash | 9/23 | about 51 | 9/23 logs |

- `STATUS_2026-09-28.md` separately records "DS at max effort about 13 tok/s".
- The "97 tok/s single request on 9/29" figure is **not recorded in any local file**, so it is unverified here.
- Per-request latency at 9/28 effort max was about 90–124 s median for kimi HLE, 251 s for DS HLE sample, and 1,063 s for DS HLE pinned.

---

## Summary table

| ID | Result set | Model | Bench / n | Score | Cost per task | Latency (avg) | Level |
|---|---|---|---|---|---|---|---|
| S01 | 9/23 code_ds | deepseek-v4.1-flash (direct) | HE+/MBPP+ 542 | 83.9% plus | $0.0000095 | 1.46 s | **A (provisional)** |
| S02 | 9/23 code3 kimi | kimi-k3 (reasoning, default) | HE+/MBPP+ 542 | 86.3% plus | $0.00392 | 3.39 s | B (12 capped) |
| S03 | 9/23 run1 kimi | kimi-k3 | HE+/MBPP+ 542 | 84.1% | $0.00379 | 3.61 s | C |
| S04 | 9/23 code4 auto subsets | ds / glm-5.3-flash / kimi | 130 / 409 / 3 routed | 93.1 / 83.9 / 100% | — | — | C |
| S05 | 9/23 run2 auto subsets | ds / kimi | 513 / 29 routed | 85.0 / 72.4% | — | — | C |
| S06 | 9/23 code3 auto | glm-5.3-flash | 412 routed | 76.0% | — | — | INVALID |
| S07 | 9/23 run1 auto | ds / kimi | 542 | 83.2% | — | — | INVALID |
| S08 | smoke/trial2/math_smoke | — | 6 / 0 / 8 | — | — | — | INVALID |
| S09 | 9/23 math_ds | deepseek-v4.1-flash (direct) | GSM8K 150 + MATH-500 150 | 94.3% | $0.0000375 | 6.27 s | B |
| S10 | 9/23 math3 kimi | kimi-k3 | same 300 | 94.7% | $0.00507 | 4.84 s | B |
| S11 | 9/23 math1 kimi | kimi-k3 | same 300 | 92.3% | $0.00542 | 4.41 s | C |
| S12 | 9/23 math auto subsets | ds / kimi / glm-5.3-flash | routed | see above | — | — | C |
| S13 | TrajectoryRL Table 4 | ds (both modes), qwen3.8-27b (both modes), glm-5.3-flash, glm-5.2, glm-5.3, kimi-k3 | HE+/MBPP+ 542 | 80.4–86.5% | $0.00001–0.00693 | 3.5–41.3 s | C (no raw) |
| S14 | TrajectoryRL agentic | ds, qwen3.8-27b, glm-5.3-flash, glm-5.3, kimi-k3 | Agentic-14/26/35 | see above | per run | — | C (no raw) |
| S15 | HLE R03–R07 | ds / kimi | partial | — | — | — | INVALID |
| S16 | AB R01, R08–R10 | ds / kimi | partial | — | — | — | INVALID |
| S17 | DeepSWE R02, R11 | kimi / ds | 2 / 1 | — | — | — | INVALID |
| S18 | Server-only DeepSWE/TB2 | various | — | — | — | — | INVALID, not audited |
| S19 | 9/30 capacity probes | ds 4.1, 0731, glm-5.3-flash, glm-5.3, kimi | 5 probes each | caps above | — | — | C (capacity only) |
| S20 | 9/29 ctx_test | 0731, ds 4.1 | 7 probes | caps above | — | — | C (capacity only) |

**Candidate coverage by bucket**:

| Bucket | Evidence |
|---|---|
| coding + direct | deepseek-v4.1-flash **A (provisional)**; qwen3.8-27b C |
| coding + reasoning | kimi-k3 B; glm-5.3-flash, glm-5.3 and glm-5.2 C only |
| math + direct | deepseek-v4.1-flash B |
| math + reasoning | kimi-k3 B |
| agentic | C only (TrajectoryRL) |
| long context | capacity only |
| deepseek-v4-flash-0731, qwen3.6-35b-a3b, glm-5.3 on Engy in this project | none |
