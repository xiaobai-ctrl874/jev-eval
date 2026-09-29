# Jev 分类评测集 v1：构建说明

Built 2026-09-29. No model, Jev API or remote host was called. Every label comes from a benchmark field, a fixed rule, or a hand-written entry marked `human_review_required`. All random choices use `random.Random(20260929)`, re-created fresh for each draw. Pools are sorted before shuffling, and output rows are sorted by `id`.

Rebuild and validate:

```
/root/bench/hle-venv/bin/python scripts/build_all.py          # writes datasets/ and splits/
/root/bench/hle-venv/bin/python scripts/validate_datasets.py  # includes the rebuild-hash check
```

Inputs: `raw/` (gitignored; recreated with the download scripts). Metadata for DeepSWE and Terminal-Bench comes from the local task repos `/root/bench/deep-swe/tasks`, `/root/bench/tb4/terminal-bench-4.0.0/tasks` and `/root/bench/tb2/terminal-bench` (`task.toml`).

## Files

| File | Rows | Content |
|---|---|---|
| `datasets/jev_classification_eval_v1.jsonl` | 240 | 30 high-purity items per task_type |
| `datasets/jev_boundary_eval_v1.jsonl` | 60 | 10 per ambiguous pair × 6 pairs, all `human_review_required` |
| `datasets/jev_execution_mode_eval_v1.jsonl` | 200 | 100 direct + 100 agentic |
| `datasets/jev_capability_eval_v1.jsonl` | 150 | 30 per source, only sources with an official difficulty (plus AutomationBench simple vs public) |
| `splits/calibration_ids.txt` / `splits/holdout_ids.txt` | 354 / 152 | 70/30 over the 506 distinct ids |

Scripts:
- `scripts/jev_common.py`: loaders, prompt reconstruction, samplers and the row builder.
- `scripts/boundary_picks.py`: the frozen boundary items.
- `scripts/build_{classification,boundary,execution_mode,capability,splits,all}.py`: the builders.
- `scripts/validate_datasets.py`: the validator.
- `scripts/longbench_v2_0shot.txt`: a verbatim copy of the official LongBench `prompts/0shot.txt`.

`scripts/lcb_metadata_stream.py` gained one change: an optional `LCB_OUT` env var that names the output file. Its default behaviour is unchanged.

### Row schema

The required fields are `id, benchmark, source_id, prompt, system_prompt, tools, gold_task_type, gold_execution_mode, gold_capability_need (always null), official_category, official_difficulty, label_source, label_confidence, notes`.

- **`id`** is `<bench_key>:<source_id>`. The same item gets the same id in every file. The validator checks that shared ids have identical prompt, labels, category and difficulty across files.
- **`label_source` / `label_confidence`** describe the file's primary label:
  - task_type in the classification, boundary and capability files;
  - execution_mode in the execution-mode file.
- **Per-dimension provenance** is always present: `task_type_label_source`, `task_type_confidence`, `execution_mode_label_source`, `execution_mode_confidence`.
- **`official_difficulty`** is the benchmark's own field value, copied verbatim, or null. `official_difficulty_field` names the source field:
  - LiveCodeBench `difficulty`
  - MATH-500 `level`
  - LongBench v2 `difficulty`
  - Terminal-Bench 2.0 `difficulty`
  - LiveBench math `hardness` (olympiad items only)
  - LiveBench reasoning `level` (zebra items only)
- **Agentic rows** keep their first request:
  - `prompt` is the user message.
  - `system_prompt` is kept.
  - `tools` holds tool names only, which is what `autoroute.build_state` exposes.
  - AutomationBench rows use the official CLI default toolset `api` (`api_search`, `api_fetch`, `base64_encode`). The task's Zapier tool list is kept in `zapier_tools_listed`.
  - DeepSWE and Terminal-Bench rows use the mini-swe-agent `mini.yaml` first request (single `bash` tool), taken from `raw/agentic_first_requests`.
- **LiveCodeBench** prompts are rebuilt with the official OpenAIChat template: `SYSTEM_MESSAGE_GENERIC` plus `get_generic_question_template_answer`, from `lcb_runner/prompts/code_generation.py` on GitHub main.
- **LongBench v2 rows:**
  - `prompt` holds the question and choices block of the official 0shot template.
  - `prompt_as_sent` holds the full filled template (context + question), truncated in the middle to 20,000 chars: the first 10,000 plus the last 10,000, mirroring pred.py's head+tail truncation.
  - Also stored: `prompt_as_sent_truncated`, `prompt_as_sent_full_chars` and `context_ref` (HF dataset, file, `_id`, local path, context chars).
  - The context was available locally for every item, and all 62 distinct LongBench items are truncated.
  - Note that production `build_state` clips the first user message to 1,500 chars and the current one to 4,000 chars, keeping only the head. Production Jev would therefore see the instruction line and the start of the context, but not the question.

## 1. Classification set (240)

| task_type | Source and rule | label_source | Sampling |
|---|---|---|---|
| general_qa (30) | SimpleQA Verified, `requires_reasoning=False` | rule_mapping, high | 3 per topic (10 topics), round-robin over answer_type → Place 9 / Date 6 / Number 5 / Person 5 / Other 5 |
| writing_language (30) | WritingBench. `domain2` is in the audit's 32 "cleanest" subdomains (see `WB_CLEAN`). Excluded: (a) the 242 heuristic-flagged analysis candidates; (b) queries over 5,000 chars whose first or last 600 chars match analyze/evaluate keywords (en and zh regex) | rule_mapping; high if ≤5K chars, else medium (25/5) | Round-robin over domain2, so 30 distinct subdomains; zh 18 / en 12 |
| math (30) | 15 LiveBench math (native `category=math`) + 15 MATH-500 | benchmark_native (LiveBench) / rule_mapping (MATH-500), high | LiveBench: 5 per task (AMPS_Hard / math_comp / olympiad), round-robin over subtask. MATH-500: 3 per level 1–5, round-robin over subject. The `updated_amc` twins of two boundary items are excluded. |
| reasoning (30) | LiveBench reasoning (native `category=reasoning`) | benchmark_native, high | 10 each of zebra_puzzle / web_of_lies_v2 / spatial, round-robin over release date |
| coding (30) | LiveCodeBench **test6.jsonl only** (release_v6 delta, 175 rows, all used) | rule_mapping, high | 10 easy / 10 medium / 10 hard, round-robin over platform. test6 has only leetcode and atcoder, so the result is 15 + 15. |
| research_analysis (30) | LongBench v2. Multi-Document QA {Academic, Financial, Governmental, Multi-news} + Table QA. Legal is dropped (audited as mixed). A manual purity filter then removes 26 lookup / extraction / arithmetic items (`LB_EXCLUDE_PREFIX`, with a reason for each). Pool after filtering: 103. | rule_mapping, **medium** | 6 per sub_domain, round-robin over difficulty×length → easy 12 / hard 18; short 8 / medium 14 / long 8 |
| planning_design (30) | tencent PlanningBench (all zh) | rule_mapping, high | Seeded `sample(30)`. Extra `sub_category` is marked `human_review_required`. |
| workflow_operation (30) | AutomationBench | rule_mapping, high | 5 per public domain (sales, marketing, operations, support, finance, hr) |

- No shortfall: every task_type has 30 items. research_analysis filled 30 from a clean pool of 103.
- The PlanningBench `sub_category` is "planning" for all 30. I read every sampled prompt: all are operational scheduling, allocation, dispatch, rostering, evacuation or production plans. None is a design task.

## 2. Boundary set (60)

These are real items picked by hand. They are listed with a reason in `scripts/boundary_picks.py`. Every row has `label_source=human_review_required`, and `gold_task_type = recommended_gold`, which is my recommendation, not verified gold. Extra fields: `pair, candidate_labels, why_ambiguous, recommended_gold, confidence`. Confidence splits into 31 low / 29 medium.

| Pair | Items (source) | Recommended gold |
|---|---|---|
| math vs reasoning | 5 LiveBench math puzzle-style items (liar puzzle, token game, guessing game, tournament, class Venn) + 5 LiveBench reasoning spatial counting/geometry items | math 5 / reasoning 5 |
| general_qa vs research_analysis | 8 LongBench items removed by the purity filter (single-document lookups within Multi-Document QA and Table QA) + 2 Knowledge-graph-reasoning items | general_qa 9 / research_analysis 1 |
| planning_design vs workflow_operation | 7 AutomationBench planning-flavoured tasks (content calendars, capacity, headcount plan, break schedules, move scheduling) + TB4 production-planning, TB4 ctr-optimization, TB2 constraints-scheduling | workflow_operation 8 / planning_design 2 |
| writing_language vs research_analysis | 10 WritingBench items from Investment Analysis, Market Analysis, Financial Reports, Sales Report, User Research, Literature Review and Regulatory Analysis | research_analysis 8 / writing_language 2 |
| reasoning vs planning_design | 5 PlanningBench items whose prompt contains 唯一 (a unique solution). Rule: seeded `sample(5)` from those 200; resulting ids frozen. Plus 5 NATURAL PLAN items (2 calendar, 2 meeting, 1 trip; seeded `sample` per file; prompt = `prompt_5shot`). | planning_design 7 / reasoning 3 |
| coding vs planning_design | 7 Terminal-Bench tasks (waveguide routing, dispatch CLI, Spark dedup, DB cutover, batching scheduler, flight-dispatch fix, WDM device design) + 3 WritingBench Technical Documentation items (DB optimisation plan, recommender architecture doc, ViT training doc) | coding 7 / planning_design 3 |

- Boundary ids are excluded from every other file.
- Split: 43 direct / 17 agentic.
- Weakness: the coding vs planning_design pair has no clean direct "software design" item, because no benchmark provides one. The pair is built from agentic Terminal-Bench tasks and WritingBench docs. It is real but only weakly ambiguous on the design side.

## 3. Execution-mode set (200)

All execution_mode labels are rule_mapping and high confidence, derived from benchmark structure: single-turn benchmarks are direct; sandbox or tool-environment benchmarks are agentic.

- **Direct (100):** SimpleQA 13, WritingBench 13, LiveBench math 11, MATH-500 11, LiveBench reasoning 13, LiveCodeBench 13, LongBench v2 13, PlanningBench 13. Each is drawn from the same clean pool as the classification set, round-robin over topic / domain2 / task / level / task / difficulty / sub_domain respectively; PlanningBench uses `sample`.
- **Agentic (100):**
  - DeepSWE 25 (round-robin over language)
  - Terminal-Bench 4.0: 20 (round-robin over category)
  - Terminal-Bench 2.0: 25 (round-robin over category)
  - AutomationBench 30: 4 per public domain + 6 from `simple`
- **task_type on agentic rows:**
  - DeepSWE → coding (rule_mapping).
  - AutomationBench → workflow_operation (rule_mapping).
  - Terminal-Bench:
    - Rows whose category is TB2 software-engineering / debugging or TB4 Software are recommended **coding**.
    - Exception: `prove-plus-comm` is a Coq proof, so it stays null.
    - Every other Terminal-Bench row is **null**.
    - Both groups are marked `human_review_required`: 7 coding + 38 null in this file.

## 4. Capability set (150)

`gold_capability_need = null` on every row.

| Source | official_difficulty | Sampling |
|---|---|---|
| LiveCodeBench (test6) | easy/medium/hard | 10/10/10, round-robin over platform. These are the **same 30 items** as the classification coding set: same pool, quota and seed. |
| MATH-500 | level 1–5 | 6 per level, round-robin over subject |
| LongBench v2 (research_analysis pool) | easy/hard; `length` kept | 15/15, round-robin over length |
| Terminal-Bench 2.0 | easy/medium/hard | All 4 easy + 13 medium + 13 hard, round-robin over category; task_type as in §3 (6 coding, 24 null, human review) |
| AutomationBench | **null** (simple vs public is not an official label) | 15 simple + 15 public, round-robin over domain. The domain is in `official_category`, plus an `ab_slice` field. |

## 5. Splits

- **Universe:** the 506 distinct ids across files 1–4. Overlaps: classification∩execution 68, classification∩capability 56, execution∩capability 26.
- **Stratum:** (`gold_task_type` or "null", `gold_execution_mode`, `official_difficulty` or "-"). This gives 40 fine strata.
- **Assignment:**
  1. Shuffle the ids with the seed.
  2. Stable-sort them by stratum.
  3. Send position i to calibration iff ⌊0.7(i+1)⌋ > ⌊0.7i⌋.
- **Result:** 354 / 152, which is exactly 0.700. Every fine stratum is within 0.7 items of 70%, and task_type shares range from 0.686 to 0.719.
- An id appears in exactly one split, so an item shared by several datasets always lands on the same side.

## Items needing human review

- **Boundary set:** 60 of 60 task_type labels.
- **Terminal-Bench task_type:** 62 distinct non-boundary ids are `human_review_required`, 50 of them null. Across all files that is 45 rows in the execution-mode set and 30 in the capability set, with 13 ids shared.
- **Across the union:** 122 distinct ids have a `human_review_required` task_type.
- **PlanningBench `sub_category`:** 30 tags, all recommended "planning".
- **Recommended for a spot check although rule-mapped:**
  - The 30 LongBench research_analysis items: the purity filter and the subdomain→label mapping are my own judgement, so these are marked medium.
  - The 5 WritingBench rows longer than 5K chars (medium).

## Shortfalls / coverage gaps

- **planning_design:** the "design" half is not covered at all. All 30 items are operational planning, because no public benchmark gives clean design items.
- **coding:** only competitive programming (leetcode and atcoder; test6 has no codeforces). test5 was **not used**: its metadata stream was still at 18/167 rows, so I stopped it and deleted the partial file. The newest file, test6, was complete (175 rows, matching the official v6 delta count 1055−880).
- **reasoning:** only 3 templated LiveBench families.
- **LiveBench HF snapshot is stale** (2025-04). The live leaderboard's newer tasks are not included.
- **Boundary pairs:** general_qa vs research_analysis is single-source (all 10 items from LongBench v2). coding vs planning_design is weak on direct design items (see §2).
- **Language:** PlanningBench is zh only; WritingBench is 18 zh / 12 en.

## UNVERIFIED

- **LiveCodeBench prompt template:** taken from GitHub `main` on 2026-09-29, not pinned to the commit used by any leaderboard run.
- **MATH-500:** has no single official chat template; the prompt is the bare problem.
- **SimpleQA Verified and WritingBench:** the prompt is the bare question or query, per their generation setups.
- **Agentic first requests:** AutomationBench uses toolset `api` (the CLI default). The DeepSWE and Terminal-Bench requests assume the mini-swe-agent `mini.yaml` harness. The DeepSWE leaderboard's exact mini-swe-agent configuration is undocumented, and Terminal-Bench's reference agent is Terminus-2. Production traffic may differ.
- **NATURAL PLAN:** `prompt_5shot` is assumed to be the official evaluation prompt. `prompt_0shot` is kept as well.
- **LongBench `prompt_as_sent`:** the 20K-char middle truncation is our own excerpt budget. The official code truncates tokens at the model's max length (e.g. 128K).
- **Terminal-Bench 4.0** has no discrete difficulty field, so it is not in the capability set.
- **Remote HF files:** the LiveCodeBench `test6.jsonl` metadata was streamed from the official HF repo. Row count 175 was verified; content hashes against a later HF revision were not checked.

## Validation output (`scripts/validate_datasets.py`)

```
union ids: 506  calibration: 354 (0.700)  holdout: 152 (0.300)
stratum proportions by gold_task_type (calibration share):
  coding               n=  83 cal=  58 share=0.699
  general_qa           n=  51 cal=  35 share=0.686
  math                 n=  72 cal=  51 share=0.708
  null                 n=  50 cal=  35 share=0.700
  planning_design      n=  42 cal=  29 share=0.690
  reasoning            n=  47 cal=  33 share=0.702
  research_analysis    n=  61 cal=  43 share=0.705
  workflow_operation   n=  68 cal=  47 share=0.691
  writing_language     n=  32 cal=  23 share=0.719
  execution_mode=agentic  n= 164 share=0.695
  execution_mode=direct   n= 342 share=0.702
  fine strata (task_type x execution_mode x official_difficulty): 40; max |cal - 0.7n| = 0.70 items
rebuild hash compare:
  datasets/jev_classification_eval_v1.jsonl     69698fe840b2329a == 69698fe840b2329a
  datasets/jev_boundary_eval_v1.jsonl           c6c66207be8825d4 == c6c66207be8825d4
  datasets/jev_execution_mode_eval_v1.jsonl     db89282b70c94e6e == db89282b70c94e6e
  datasets/jev_capability_eval_v1.jsonl         43e36f3b117e689e == 43e36f3b117e689e
  splits/calibration_ids.txt                    3314f6dfc3b3ca94 == 3314f6dfc3b3ca94
  splits/holdout_ids.txt                        cccedb073872be56 == cccedb073872be56
ALL CHECKS PASSED
```

The validator also checks:
- required fields and label vocabularies;
- ids unique per file;
- every `source_id` exists in the raw data, and its prompt / system prompt / tools match the raw item exactly;
- the boundary fields, and that recommended_gold is one of candidate_labels;
- the 100/100 execution-mode split;
- that boundary ids stay out of the other files;
- that AutomationBench `official_difficulty` is null;
- cross-file consistency;
- that the HF token does not appear in any output.
