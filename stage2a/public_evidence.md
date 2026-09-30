# Stage 2a — Public benchmark evidence for routing candidates (collected 2026-09-30)

Scope: only public pages and existing local files. No model API was called and no ssh was used. Machine-readable rows are in `public_evidence.jsonl` (265 rows, one per model × benchmark × source). Each row has version, n_tasks, harness, tools, reasoning, temperature, max output, timeout, rollouts, judge, cost, latency, date, URL and `source_type`. Unknown fields are marked `unknown`. Raw downloads (model-card READMEs, AA page data, LiveBench CSV, EQ-Bench data) are in `raw/`. The DeepSWE builder script lives in the session scratchpad and is not needed to read the results.

Candidates → vendor names:
- `deepseek-v4.1-flash` = DeepSeek-V4.1-Flash (HF `deepseek-ai/DeepSeek-V4.1-Flash`, AA "DeepSeek V4.1 Flash (Reasoning, Max Effort)", released 2026-09-10).
- `deepseek-v4-flash-0731` = **DeepSeek-V4-Flash-0731** (HF `deepseek-ai/DeepSeek-V4-Flash-0731`). This is the official, non-preview release of V4-Flash. On AA its slug is `deepseek-v4-flash`, named "DeepSeek V4 Flash 0731 (Reasoning, Max Effort)", released 2026-07-31. The "DS-V4-Flash" column on the V4.1 card matches the 0731 card exactly (TB2.1 82.7, DeepSWE 54.4, NL2Repo 54.2, ALE 25.2), so that column is 0731. The DeepSWE leaderboard id `deepseek-v4-flash` was run on the DeepSeek API on 2026-08-05/06, after the 0731 release. That makes it *probably* 0731, but the leaderboard does not say so.
- `kimi-k3` = Kimi K3 (max). `glm-5.3` = GLM-5.3 (max). `glm-5.3-flash` = GLM-5.3-Flash (AA "GLM 5.3 Flash").
- Reserve: Qwen3.6-35B-A3B and Qwen3.8-27B (AA `qwen3-8-27b` = "Qwen3.8 27B (xhigh)"). Qwen3.6-35B-A3B is not on LiveBench or EQ-Bench.

Legend: **V** = self-reported by the vendor. **C** = a competitor's number as printed on another vendor's card. **3P** = third party (Artificial Analysis, DeepSWE leaderboard, LiveBench, EQ-Bench). **V→AA** = a vendor card citing an older AA value. `*` = reserve model.

## Per-bucket tables

### general_qa

| Benchmark | Source | DS-V4.1-F | DS-V4-F-0731 | Kimi K3 | GLM-5.3 | GLM-5.3-F | Qwen3.6-35B* | Qwen3.8-27B* |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| SimpleQA-Verified (EM, 25-shot) | DS-V4.1 card | 42.3 (V) | — | — | — | — | — | — |
| AA-Omniscience accuracy | AA | 46.4 (3P) | 40.4 (3P) | 47.6 (3P) | 33.9 (3P) | 27.5 (3P) | 18.8 (3P) | 15.6 (3P) |
| AA-Omniscience hallucination rate (lower better) | AA | 96.5 (3P) | 91.7 (3P) | 53.2 (3P) | 29.6 (3P) | 27.6 (3P) | 50.5 (3P) | 30.3 (3P) |
| AA-Omniscience index (-100..100) | AA | -5.3 (3P) | -14.3 (3P) | 19.7 (3P) | 14.3 (3P) | 7.5 (3P) | -22.2 (3P) | -10.0 (3P) |

### writing_language

| Benchmark | Source | DS-V4.1-F | DS-V4-F-0731 | Kimi K3 | GLM-5.3 | GLM-5.3-F | Qwen3.6-35B* | Qwen3.8-27B* |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| IFBench | Qwen card | — | — | — | — | — | — | 79.5 (V) |
| IFBench (AA) | AA | — | — | — | — | — | 64.4 (3P) | — |
| LiveBench Language | LiveBench | 81.2 (3P) | 79.2 (3P) | 85.5 (3P) | 79.9 (3P) | 77.3 (3P) | — | 74.3 (3P) |
| LiveBench IF | LiveBench | 70.0 (3P) | 65.5 (3P) | 71.4 (3P) | 69.3 (3P) | 52.8 (3P) | — | 72.7 (3P) |
| EQ-Bench Creative Writing v3 Elo (raw) | EQ-Bench | 1540.1 (3P) | 1441.1 (3P) | 2082.3 (3P) | 2075.0 (3P) | — | — | 1671.3 (3P) |
| EQ-Bench Creative Writing v3 rubric (raw) | EQ-Bench | 16.08 (3P) | 15.98 (3P) | 16.85 (3P) | 17.04 (3P) | — | — | 15.5 (3P) |

### math

| Benchmark | Source | DS-V4.1-F | DS-V4-F-0731 | Kimi K3 | GLM-5.3 | GLM-5.3-F | Qwen3.6-35B* | Qwen3.8-27B* |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| MathArena Apex | DS-V4.1 card | 65.6 (V) | 58.6 (C) | 65.6 (C) | — | — | — | — |
| MATH (EM, 4-shot) | DS-V4.1 card | 61.1 (V) | — | — | — | — | — | — |
| HMMT Feb 26 | Qwen card | — | — | — | — | — | 83.6 (V) | — |
| AIME26 | Qwen card | — | — | — | — | — | 92.7 (V) | — |
| IMOAnswerBench | Qwen card | — | — | — | — | — | 78.9 (V) | — |
| LiveBench Mathematics | LiveBench | 93.3 (3P) | 86.8 (3P) | 84.4 (3P) | 87.9 (3P) | 81.2 (3P) | — | 86.2 (3P) |

### reasoning_planning

| Benchmark | Source | DS-V4.1-F | DS-V4-F-0731 | Kimi K3 | GLM-5.3 | GLM-5.3-F | Qwen3.6-35B* | Qwen3.8-27B* |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| GPQA Diamond | DS-V4.1 card | 90.9 (V) | 89.9 (C) | 92.9 (C) | 88.1 (C) | — | — | — |
| HLE (full, no tools) | DS-V4.1 card | 36.8 (V) | — | — | — | — | — | — |
| HLE text-only subset (no tools) | DS-V4.1 card | 39.1 (V) | — | — | — | — | — | — |
| HLE (DS card; K3 full set, GLM/DS-V4-Flash marked text-only) | DS-V4.1 card | — | 37.8 (C) | 43.5 (C) | 42.0 (C) | — | — | — |
| GPQA Diamond | Kimi card | — | — | 93.5 (V) | — | — | — | — |
| HLE-Full (no tools) | Kimi card | — | — | 43.5 (V) | — | — | — | — |
| GPQA | Qwen card | — | — | — | — | — | 86.0 (V) | — |
| HLE | Qwen card | — | — | — | — | — | 21.4 (V) | 30.8 (V) |
| GPQA Diamond | Qwen card | — | — | — | — | — | — | 89.2 (V) |
| HLE (AA) | AA | 39.2 (3P) | 38.6 (3P) | 46.9 (3P) | 42.3 (3P) | 39.9 (3P) | 22.2 (3P) | 33.9 (3P) |
| CritPt (AA) | AA | 14.3 (3P) | 16.6 (3P) | 23.4 (3P) | 19.1 (3P) | 15.4 (3P) | 0.3 (3P) | 5.4 (3P) |
| GPQA Diamond (AA) | AA | — | 90.8 (3P) | 93.5 (3P) | 91.7 (3P) | 91.2 (3P) | 84.1 (3P) | 90.5 (3P) |
| LiveBench Reasoning | LiveBench | 86.7 (3P) | 86.6 (3P) | 90.7 (3P) | 85.8 (3P) | 77.6 (3P) | — | 80.0 (3P) |

### coding_direct

| Benchmark | Source | DS-V4.1-F | DS-V4-F-0731 | Kimi K3 | GLM-5.3 | GLM-5.3-F | Qwen3.6-35B* | Qwen3.8-27B* |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| Codeforces | DS-V4.1 card | 3471 (V) | 3289 (C) | — | — | — | — | — |
| HumanEval (Pass@1, 0-shot) | DS-V4.1 card | 79.4 (V) | — | — | — | — | — | — |
| SciCode | Kimi card | — | — | 58.7 (V→AA) | — | — | — | — |
| LiveCodeBench v6 | Qwen card | — | — | — | — | — | 80.4 (V) | 90.3 (V) |
| SciCode (AA) | AA | 51.9 (3P) | 50.3 (3P) | 59.5 (3P) | 59.0 (3P) | 51.6 (3P) | 36.6 (3P) | 46.6 (3P) |
| LiveBench Coding | LiveBench | 80.0 (3P) | 75.0 (3P) | 81.4 (3P) | 79.0 (3P) | 79.0 (3P) | — | 75.7 (3P) |

### research_analysis

| Benchmark | Source | DS-V4.1-F | DS-V4-F-0731 | Kimi K3 | GLM-5.3 | GLM-5.3-F | Qwen3.6-35B* | Qwen3.8-27B* |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| HLE w/ tools | DS-V4.1 card | 63.9 (V) | 51.5 (C) | 59.8 (C) | 62.5 (C) | — | — | — |
| HLE-Full (with general tools) | Kimi card | — | — | 56.0 (V) | — | — | — | — |
| BrowseComp | Kimi card | — | — | 91.2 (V) | — | — | — | — |
| HLE w/ tools | GLM card | — | — | 59.8 (C) | 62.5 (V) | — | — | — |
| HLE w/ tools (full set) | GLM-Flash card | — | — | — | — | 55.3 (V) | — | — |
| LiveBench Data Analysis | LiveBench | 79.3 (3P) | 79.3 (3P) | 78.7 (3P) | 70.2 (3P) | 76.4 (3P) | — | 76.6 (3P) |

### coding_agentic

| Benchmark | Source | DS-V4.1-F | DS-V4-F-0731 | Kimi K3 | GLM-5.3 | GLM-5.3-F | Qwen3.6-35B* | Qwen3.8-27B* |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| Terminal-Bench 2.1 | DS-V4.1 card | 90.6 (V) | 82.7 (C) | 88.3 (C) | 88.2 (C) | — | — | — |
| Terminal-Bench 3.0 | DS-V4.1 card | 30.0 (V) | 7.6 (C) | 17.7 (C) | 28.3 (C) | — | — | — |
| Terminal-Bench 4.0 | DS-V4.1 card | 31.2 (V) | 7.0 (C) | 12.6 (C) | 37.9 (C) | — | — | — |
| DeepSWE [mini-SWE harness (DS own run: N=8, 1M ctx, max_steps 500)] | DS-V4.1 card | 74.2 (V) | 54.4 (C) | 67.5 (C) | 66.9 (C) | — | — | — |
| NL2Repo-Bench | DS-V4.1 card | 64.0 (V) | 54.2 (C) | 58.0 (C) | 58.0 (C) | — | — | — |
| DeepSWE [Claude Code] | DS-V4.1 card | 69.8 (V) | — | — | — | — | — | — |
| DeepSWE [Codex] | DS-V4.1 card | 65.6 (V) | — | — | — | — | — | — |
| DeepSWE [OpenCode] | DS-V4.1 card | 65.5 (V) | — | — | — | — | — | — |
| DeepSWE [Pi] | DS-V4.1 card | 66.2 (V) | — | — | — | — | — | — |
| DeepSWE [mini-SWE] | DS-V4.1 card | 74.2 (V) | — | — | — | — | — | — |
| DeepSWE [DSH Minimal] | DS-V4.1 card | 72.6 (V) | — | — | — | — | — | — |
| DeepSWE [DSH Standard] | DS-V4.1 card | 70.5 (V) | — | — | — | — | — | — |
| DeepSWE [DSH PTC] | DS-V4.1 card | 67.6 (V) | — | — | — | — | — | — |
| Terminal-Bench 2.1 | DS-0731 card | — | 82.7 (V) | — | — | — | — | — |
| NL2Repo | DS-0731 card | — | 54.2 (V) | — | — | — | — | — |
| DeepSWE [DeepSeek Harness minimal mode (code agent tasks)] | DS-0731 card | — | 54.4 (V) | — | — | — | — | — |
| DeepSWE [Kimi Code harness] | Kimi card | — | — | 67.5 (V) | — | — | — | — |
| Terminal-Bench 2.1 | Kimi card | — | — | 88.3 (V) | — | — | — | — |
| FrontierSWE | Kimi card | — | — | 81.2 (V) | — | — | — | — |
| SWE-Marathon | Kimi card | — | — | 42.0 (V) | — | — | — | — |
| Terminal-Bench 2.1 | GLM card | — | — | 88.3 (C) | 88.2 (V) | — | — | — |
| Terminal-Bench 3.0 | GLM card | — | — | 17.4 (C) | 28.3 (V) | — | — | — |
| DeepSWE [mini-swe-agent] | GLM card | — | — | — | 66.9 (V) | — | — | — |
| DeepSWE [unknown] | GLM card | — | — | 67.5 (C) | — | — | — | — |
| NL2Repo | GLM card | — | — | 58.0 (C) | 58.0 (V) | — | — | — |
| FrontierSWE | GLM card | — | — | — | 78.1 (V) | — | — | — |
| SWE-Marathon | GLM card | — | — | 48.1 (C) | 42.5 (V) | — | — | — |
| Terminal-Bench 2.1 | GLM-Flash card | — | — | — | — | 84.3 (V) | — | — |
| DeepSWE [mini-swe-agent] | GLM-Flash card | — | — | — | — | 63.4 (V) | — | — |
| SWE-bench Verified | Qwen card | — | — | — | — | — | 73.4 (V) | — |
| SWE-bench Pro (Qwen-refined) | Qwen card | — | — | — | — | — | 49.5 (V) | 61.7 (V) |
| Terminal-Bench 2.0 | Qwen card | — | — | — | — | — | 51.5 (V) | — |
| Terminal-Bench 2.1 | Qwen card | — | — | — | — | — | — | 73.0 (V) |
| NL2Repo-Bench | Qwen card | — | — | — | — | — | — | 42.3 (V) |
| DeepSWE [Claude Code] | Qwen card | — | — | — | — | — | — | 42.2 (V) |
| Terminal-Bench 4.0 (AA) | AA | 26.8 (3P) | 12.1 (3P) | 12.6 (3P) | 41.9 (3P) | 32.8 (3P) | 0 (3P) | 5.6 (3P) |
| Terminal-Bench 2.1 (AA) | AA | — | 78.7 (3P) | 85.0 (3P) | 83.9 (3P) | 84.3 (3P) | 44.9 (3P) | 79.8 (3P) |
| DeepSWE leaderboard | DeepSWE-LB | — | 53.3 (3P) | 68.5 (3P) | 69.0 (3P) | 63.4 (3P) | — | — |
| LiveBench Agentic Coding | LiveBench | 77.3 (3P) | 46.8 (3P) | 62.2 (3P) | 60.9 (3P) | 56.8 (3P) | — | 61.4 (3P) |

### workflow_agentic

| Benchmark | Source | DS-V4.1-F | DS-V4-F-0731 | Kimi K3 | GLM-5.3 | GLM-5.3-F | Qwen3.6-35B* | Qwen3.8-27B* |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| AutomationBench | DS-V4.1 card | 54.8 (V) | 37.7 (C) | 46.7 (C) | 48.8 (C) | — | — | — |
| Toolathlon-Verified | DS-0731 card | — | 70.3 (V) | — | — | — | — | — |
| AutomationBench Public | DS-0731 card | — | 25.1 (V) | — | — | — | — | — |
| AutomationBench | Kimi card | — | — | 30.8 (V) | — | — | — | — |
| tau3-Banking | Kimi card | — | — | 33.4 (V→AA) | — | — | — | — |
| Toolathlon-Verified | Kimi card | — | — | 76.5 (V) | — | — | — | — |
| MCP-Atlas | Kimi card | — | — | 84.2 (V) | — | — | — | — |
| Toolathlon Verified | GLM card | — | — | 76.5 (C) | 73.0 (V) | — | — | — |
| AutomationBench | GLM card | — | — | 46.7 (C) | 48.2 (V) | — | — | — |
| AutomationBench | GLM-Flash card | — | — | — | — | 48.8 (V) | — | — |
| TAU3-Bench | Qwen card | — | — | — | — | — | 67.2 (V) | — |
| MCP-Atlas (public) | Qwen card | — | — | — | — | — | 62.8 (V) | — |
| AutomationBench-AA | AA | 68.9 (3P) | 54.0 (3P) | 58.3 (3P) | 62.2 (3P) | 60.4 (3P) | 5.2 (3P) | 48.2 (3P) |
| tau-Banking (AA field tauBanking) | AA | — | 39.4 (3P) | 46.0 (3P) | 50.3 (3P) | 47.2 (3P) | 9.3 (3P) | 48.0 (3P) |
| tau2-Bench Telecom (AA) | AA | — | — | — | — | — | 95.3 (3P) | — |

### long_context

| Benchmark | Source | DS-V4.1-F | DS-V4-F-0731 | Kimi K3 | GLM-5.3 | GLM-5.3-F | Qwen3.6-35B* | Qwen3.8-27B* |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| LongBench-V2 (EM, 1-shot) | DS-V4.1 card | 45.2 (V) | — | — | — | — | — | — |
| AA-LCR | Kimi card | — | — | 74.7 (V→AA) | — | — | — | — |
| AA-LCR | AA | 84.0 (3P) | 79.7 (3P) | 88.7 (3P) | 79.7 (3P) | 80.0 (3P) | 71.7 (3P) | 82.0 (3P) |

### meta

| Benchmark | Source | DS-V4.1-F | DS-V4-F-0731 | Kimi K3 | GLM-5.3 | GLM-5.3-F | Qwen3.6-35B* | Qwen3.8-27B* |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| AA price & speed | AA | input $0.3/M, output $1.2/M, cache hit $0.006/M; median output speed 277.7 tok/s; Intelligence Index time/task 319s | input $0.44/M, output $1.32/M, cache hit $0.014/M; speed not shown; Intelligence Index time/task 207s | input $3/M, output $15/M, cache hit $0.3/M; median output speed 42.3 tok/s; Intelligence Index time/task 1145s | input $1.4/M, output $4.4/M, cache hit $0.26/M; median output speed 109.3 tok/s; Intelligence Index time/task 651s | input $0.15/M, output $0.5/M, cache hit $0.026/M; median output speed 61.7 tok/s; Intelligence Index time/task 1113s | input $0.375/M, output $2.25/M, cache hit $None/M; speed not shown; Intelligence Index time/task 268s | input $0.5/M, output $3/M, cache hit $0.1/M; median output speed 53.8 tok/s; Intelligence Index time/task 1241s |
| LiveBench global average | LiveBench | 81.1 (3P) | 74.2 (3P) | 79.2 (3P) | 76.1 (3P) | 71.6 (3P) | — | 75.3 (3P) |
### AA cost / time per task (list price, AA harness) — used for cost-aware routing

| AA eval | DS-V4.1-F | DS-V4-F-0731 | Kimi K3 | GLM-5.3 | GLM-5.3-F | Qwen3.8-27B* |
|---|---|---|---|---|---|---|
| HLE (AA) | $0.042 / 125s | $0.043 / 108s | $0.394 / 618s | $0.233 / 483s | $0.022 / 700s | $0.133 / 820s |
| AA-LCR | $0.032 / 11s | $0.048 / 14s | $0.309 / 36s | $0.149 / 26s | $0.017 / 73s | $0.062 / 52s |
| SciCode (AA) | $0.012 / 35s | $0.042 / 105s | $0.060 / 83s | $0.082 / 160s | $0.014 / 438s | $0.065 / 387s |
| Terminal-Bench 4.0 (AA) | $1.16 / 1027s | $0.92 / 490s | $5.09 / 2905s | $8.06 / 1780s | $0.79 / 2935s | $3.94 / 2755s |
| AutomationBench-AA | $0.173 / 313s | $0.105 / 121s | $0.633 / 471s | $0.460 / 254s | $0.030 / 328s | $0.254 / 599s |

DeepSWE v1.1 leaderboard (local per-trial data; mini-swe-agent via Pier on Modal; 113 tasks × 4 runs; only `reasoning_effort` is passed and sampling uses provider defaults; agent timeout 3h):

| Model (LB id) | Provider | Effort | Pass@1 ± 95% CI | Pass@4 | Mean cost/task (LB) | Mean / median agent time | Runs (dates) |
|---|---|---|---|---|---|---|---|
| glm-5-3 | zai | max | 69.0 ± 3.0 | see jsonl | $3.99 | 35.3 / 30.7 min | 4 (2026-08-19..20) |
| kimi-k3 | moonshot | max | 68.5 ± 4.5 | see jsonl | $4.65 | 75.7 / 66.2 min | 4 (2026-07-16) |
| glm-5-3-flash | anthropic (Z.ai's Anthropic-compatible endpoint) | max | 63.4 ± 4.4 | see jsonl | $0.24 | 25.6 / 22.0 min | 4 (2026-08-26) |
| deepseek-v4-flash (≈0731) | deepseek | max | 53.3 ± 3.6 | see jsonl | $0.46 | 24.0 / 23.1 min | 4 (2026-08-05..06) |
| deepseek-v4.1-flash | — | — | **not on leaderboard** | | | | |

Cost caveat: the leaderboard's `mean_cost_usd` is recomputed at current pricing. The per-trial `cost_usd` fields in the trials file give different means: DS-V4-Flash $0.100, GLM-5.3-Flash $0.482; GLM-5.3 and K3 agree. Both values are in the jsonl notes.

## Comparability notes

1. **Harness differences dominate agentic numbers.** DeepSWE v1.1 for the same model:
   - DS-V4.1-Flash ranges from 65.5 to 74.2 across 8 scaffolds on its own card (N=8, 1M ctx, 500 steps).
   - K3 scores 67.5 on Kimi Code, 67.3 on mini-SWE (per its card) and 68.5 on the leaderboard today.
   - Qwen3.8-27B's 42.2 was measured with Claude Code.
   - Only the datacurve leaderboard runs all models under one protocol, and it lacks DS-V4.1-Flash.
   - Terminal-Bench 2.1 vendor numbers use Claude Code, Kimi Code or DSH. AA's TB2.1 uses its own harness and gives lower values (K3 85.0 vs 88.3; GLM-5.3 83.9 vs 88.2).
2. **Terminal-Bench 4.0 is the only frontier-agentic benchmark with a uniform third-party run (AA)** for all 5 candidates. Its ranking is GLM-5.3 41.9 > GLM-5.3-F 32.8 > DS-V4.1-F 26.8 >> K3 12.6 ≈ DS-0731 12.1. The DS V4.1 card's own TB4.0 numbers (K3 12.6, GLM-5.3 37.9, DS-V4.1 31.2) roughly agree.
3. **AutomationBench numbers are not interchangeable.** There are four different things:
   - AA's private 657-task held-out split, scored with partial credit and a guardrail zero. This gives the high numbers: DS-V4.1 68.9, GLM 62.2, GLM-F 60.4, K3 58.3.
   - Kimi's public-600 run: K3 30.8.
   - The DS-0731 card's "AutomationBench Public": 25.1.
   - The GLM cards (v1.0.6) and the DS-V4.1 card (version unstated): 46–55.
   
   The same model gets 30.8 (Kimi card) vs 46.7 (GLM and DS cards) vs 58.3 (AA). GLM-5.3 is 48.2 on its own card but 48.8 on the DS card, and 48.8 is exactly GLM-5.3-Flash's own number. The DS card may have copied the Flash figure. Unverified.
4. **HLE: with vs without tools are different benchmarks.**
   - No tools: AA text-only (2158 questions, uniform judge), Kimi HLE-Full, DS HLE.
   - With tools: GLM "HLE w/ tools", DS "HLE w/ tools", Kimi "HLE-Full with tools". These go in research_analysis.
   - AA without tools: K3 46.9 > GLM 42.3 > GLM-F 39.9 ≈ DS-V4.1 39.2 ≈ DS-0731 38.6.
   - With tools (vendor, different harnesses): DS-V4.1 63.9 > GLM 62.5 > K3 59.8 (56.0 on Kimi's own card) > GLM-F 55.3.
5. **Kimi card cites older AA values.** It gives AA-LCR 74.7 as of 2026-07-23, while AA now shows 88.7 (AA-LCR v1.1). AA's τ-Banking is also not the same figure as the card's "τ³-Banking 33.4". Use the current AA values.
6. **AA settings:** temperature 0.6 for reasoning models; max output as disclosed by the model creator; the endpoint is AA's choice (not stated per model). Scores come from API providers at full precision, not Engy's quantized self-hosted serving.
7. **LiveBench** is auto-scored with no LLM judge and one common protocol. Category scores are the mean of task columns from `table_2026_06_25.csv`, computed here. The recomputed global averages match the site (K3 79.2, GLM-5.3 76.1). The Agentic Coding category is small (3 task families).
8. **EQ-Bench Creative Writing v3** uses an LLM judge. Values are the raw Elo/rubric numbers from the page data file, and the site rescales them for display. GLM-5.3-Flash is absent. `*deepseek-v4.1-flash` carries an asterisk whose meaning was not verified.
9. **Base-model rows** (DS-V4.1-Flash-Base: SimpleQA-Verified 42.3, LongBench-V2 45.2, MATH 61.1, HumanEval 79.4) are pre-trained base checkpoints, not the served model. They are recorded only because nothing else exists.

## Bucket evidence summary

| Bucket | Evidence quality | What exists |
|---|---|---|
| general_qa | Weak–moderate | AA-Omniscience (uniform, all 7 models). No SimpleQA/SimpleQA-Verified for any instruct candidate. |
| writing_language | Moderate | LiveBench Language/IF (6 models), EQ-Bench CW v3 (5 models, no GLM-F). No WritingBench; IFBench only for Qwen. |
| math | Weak | LiveBench Mathematics (6 models); MathArena Apex only DS/K3. No AIME/HMMT for any main candidate (AA no longer reports AIME). |
| reasoning_planning | Good | AA HLE text-only, GPQA, CritPt (uniform); LiveBench Reasoning. No planning-specific benchmark. |
| coding_direct | Moderate | AA SciCode (uniform), LiveBench Coding. No LiveCodeBench for main candidates (AA field null; only Qwen self-reported). |
| research_analysis | Weak | HLE w/ tools (vendor-only, mixed harness), BrowseComp only K3, LiveBench Data Analysis. |
| coding_agentic | Good | AA TB4.0 (uniform), AA TB2.1 (4 of 5), DeepSWE leaderboard (4 of 5; missing DS-V4.1), many vendor numbers. |
| workflow_agentic | Moderate (inconsistent) | AA AutomationBench-AA + τ-Banking (uniform); vendor AutomationBench variants disagree; Toolathlon/MCP-Atlas vendor-only. No tau2 for main candidates. |
| long_context | Moderate | AA-LCR (uniform, all 7). No RULER; LongBench-V2 only base DS. |

## Could not find
- SimpleQA / SimpleQA-Verified leaderboard entries for any main candidate. The Kaggle page was not fetched and the search returned no scores.
- WritingBench scores for any candidate.
- LiveCodeBench (official leaderboard or AA), AIME, HMMT or MATH-500 for the 5 main candidates. Only Qwen reserve models self-report these.
- IFBench / IFEval for the 5 main candidates. The AA field is null; only Qwen reports it.
- τ²-Bench for the main candidates. AA has it only for Qwen3.6-35B-A3B.
- RULER; LongBench v2 for instruct models.
- A SWE-bench Verified or Pro number for any main candidate. Only Qwen's own refined-Pro and Verified numbers exist.
- GLM-5.3-Flash on EQ-Bench. GLM-5.3-Flash numbers exist only as a chart image on its card; the z.ai blog did not render.
- The official Zapier AutomationBench board. It was not fetched, and a third-party snippet only says GLM-5.3 is not on it.
- DS-V4.1-Flash on the DeepSWE leaderboard.
- AA methodology details for GPQA, TB2.1 and τ-Banking (version and n not shown in the page data).
