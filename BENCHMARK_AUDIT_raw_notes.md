# Jev benchmark audit — raw notes (2026-09-29)

Parts: A = web-sourced (SimpleQA Verified, WritingBench, PlanningBench, research_analysis alternatives), B = HF datasets (LiveBench math/reasoning, MATH-500, LiveCodeBench, LongBench v2), C = local (AutomationBench, DeepSWE, Terminal-Bench 4.0/2.0). capability_need is NOT defined by any benchmark; difficulty fields below are native labels only. Note: LiveCodeBench local per-version counts (LOCAL_COUNTS_PLACEHOLDER) were still being computed by a streaming job when merged — UNVERIFIED locally; official counts from README are given.

# Part A — SimpleQA Verified / WritingBench / PlanningBench (+design gap) / research_analysis alternatives

Scripts: `/root/bench/jev_eval/scripts/inspect_writingbench_simpleqa.py` (counts + WritingBench analysis-flag heuristic).
Raw downloads: `/root/bench/jev_eval/raw/{simpleqa_verified,writingbench,planningbench,natural_plan,loong,financebench,tablebench,dabstep}/`.

---

## SimpleQA Verified → general_qa

1. **Measures**: short-form factuality / parametric knowledge, no tools. 1,000 prompts filtered from OpenAI SimpleQA (4,326) by Google DeepMind + Google Research; fixes noisy labels, topic bias, redundancy, fewer date answers. Graded by GPT-4.1 autorater (prompt in Kaggle starter notebook).
2. **Format**: official host = HF `google/simpleqa-verified` (Google org) — single file `simpleqa_verified.csv` (349 KB), config `simpleqa_verified`, split `eval`, **1,000 rows** (verified locally). Fields: `original_index, problem, answer, topic, answer_type, multi_step, requires_reasoning, urls`. Also mirrored officially by DeepMind on Kaggle (dataset + leaderboard).
3. **Native categories** (verified counts): `topic` = Politics 176, Science and technology 160, Art 145, Sports 117, Geography 111, Music 102, Other 102, History 52, TV shows 20, Video games 15. `answer_type` = Other 249, Date 222, Person 198, Number 185, Place 146.
4. **Difficulty**: no difficulty label. Proxy flags only: `multi_step` True 73 / False 927; `requires_reasoning` True 37 / False 963 (cross: F/F 903, T/F 60, F/T 24, T/T 13).
5. **Mode**: direct (card explicitly: meant to be used without search/retrieval tools).
6. **Purity**: very high for general_qa — one-line factual questions with short gold answers.
7. **Other-type contamination**: essentially none. The 37 `requires_reasoning=True` items (some involve small arithmetic/date reasoning) are borderline general_qa vs reasoning; still knowledge-dominant. Note: these are hard long-tail facts (frontier models score low) — good for task_type, but do NOT read them as "standard" capability items.
8. **Recommendation**: **SAMPLE** (stratified by `topic`×`answer_type`; e.g. 100–200). Optionally exclude or separately tag `requires_reasoning=True`. Full 1,000 is unnecessary for a router classifier.
9. **License**: MIT (HF card). Not gated. ~349 KB.
10. **Sources**: https://huggingface.co/datasets/google/simpleqa-verified · https://www.kaggle.com/benchmarks/deepmind/simpleqa-verified · https://www.kaggle.com/datasets/deepmind/simpleqa-verified · https://arxiv.org/abs/2509.07968 · starter code https://www.kaggle.com/code/nanliao7/simpleqa-verified-benchmark-starter-code

---

## WritingBench → writing_language

1. **Measures**: generative writing across real-world scenarios; query-dependent rubric (LLM generates 5 instance-specific criteria, each 1–10), judged by LLM (Claude-3.7-Sonnet recommended) or their Qwen-7B critic model.
2. **Format**: GitHub `X-PLUG/WritingBench`, file `benchmark_query/benchmark_all.jsonl` (14.7 MB), **1,000 rows** (verified). Fields: `index, domain1, domain2, lang, query, checklist`. `lang`: en 555 / zh 445. Also `benchmark_query/requirement/` subsets for style/format/length. Query length (chars): median 3,857, p90 10,211, max 31,135; **332 items >5,000 chars** (heavy pasted reference material).
3. **Native categories**: 6 `domain1` (Finance & Business 210, Politics & Law 201, Literature & Arts 183, Academic & Engineering 167, Advertising & Marketing 128, Education 111) × **100 `domain2` subdomains** (full list with counts printed by the script; e.g. Paper Outline 12, Investment Analysis 17, Financial Reports 20, Slogans 17, Lesson Plan 13, Contract 13…).
4. **Difficulty**: none native. (Requirement subsets style/format/length are constraint dimensions, not difficulty.)
5. **Mode**: direct.
6. **Purity**: medium. Output is always text, but many prompts are "write a report/analysis based on the following material/data" → semantically closer to research_analysis; some are plan/design documents → planning_design.
7. **Items that belong to other task_types** (manual spot-check + heuristic; heuristic output at `raw/writingbench/flagged_analysis_candidates.jsonl`, 242 items with analysis keywords in first 400 chars AND query >3,000 chars — this is a candidate list, NOT a clean label):
   - **research_analysis-like** (analyze provided data/documents, conclusions are the point): Finance & Business → Investment Analysis (17; e.g. "Based on Moutai 2019–2023 financials… analyze"), Market Analysis (12), Market Research (8), Financial Reports (20; e.g. "Tencent Q1 2024 business analysis briefing from these figures"), Sales Report (7), User Research (10), Risk Management (12); Politics & Law → Regulatory Analysis (10; full statute pasted, 10–16K chars), Case Study (9), Legal Opinion (12, partly), Policy Interpretation (13); Academic & Engineering → Literature Review (12), Test Report (10), Engineering Report (8); Education → Educational Report (8), Assignment Grading (6; evaluate pasted student essays).
   - **planning_design-like**: Finance & Business → Event Planning (10), Strategic Planning (6), Product Proposal (11), Requirements Specification (8), Bid Proposal (11); Education → Curriculum Design (14), Lesson Plan (13), Class Activity (8); Literature & Arts → Game Design (9), Novel Outline (7), Character Design (5); Academic → Research Proposal (8), Paper Outline (12).
   - Cleanest writing_language: Advertising & Marketing (Slogans, Promotional Copy, Product Description, Brand Story, Social Media, Voiceover, Sales Letter, Personal Blog, Multimedia Script), Literature & Arts creative (Poetry, Prose, Lyric, Fan Fiction, Novel Manuscript, Screenplay, Video/Podcast Script, Greeting Message, Host Script), Academic section-writing (Abstract, Introduction, Conclusion, Acknowledgements, Contributions, Limitations), Politics & Law (Government Speech, Official Document, Legal Awareness Campaign, Party Membership Application), Business Correspondence, Meeting Minutes/Summary (summarization — counts as writing_language per definition).
8. **Recommendation**: **FILTERED SUBSET** — take items from the "cleanest" subdomain list above, and exclude/relabel any item with >5K-char provided material whose instruction is "analyze/evaluate". Keep a separately-labeled pool of the flagged analysis/plan subdomains as hard negatives or cross-label candidates (needs human review; do not auto-label them research_analysis).
9. **License**: Apache-2.0 (GitHub). Not gated. 14.7 MB.
10. **Sources**: https://github.com/X-PLUG/WritingBench · https://raw.githubusercontent.com/X-PLUG/WritingBench/main/benchmark_query/benchmark_all.jsonl · https://arxiv.org/abs/2503.05244

---

## "PlanningBench" → planning_design

### Which project is "PlanningBench"?
Candidates found (official sources):
- **(A) PlanningBench (Tencent Hunyuan + Renmin Univ. of China), arXiv 2605.20873, May 2026** — the only project literally named "PlanningBench". HF dataset `tencent/PlanningBench`. **This is almost certainly the intended one.**
- (B) **PlanBench** (Valmeekam et al., NeurIPS 2023 D&B, arXiv 2206.10498; GitHub karthikv792/LLMs-Planning, MIT) — often confused by name; PDDL/Blocksworld-style classical planning (plan generation, cost-optimal, verification, replanning…). Symbolic puzzle-like → closer to our `reasoning` than to real-world planning_design.
- (C) Related but differently named: **NATURAL PLAN** (Google DeepMind, arXiv 2406.04520, GitHub google-deepmind/natural-plan, Apache-2.0 code / CC-BY-4.0 data): trip planning, meeting planning, calendar scheduling; **TravelPlanner** (OSU, GitHub OSU-NLP-Group/TravelPlanner, MIT; agentic tool-use + sole-planning modes).

### (A) Tencent PlanningBench — 10 fields
1. **Measures**: text-based planning under coupled constraints (goals, resources, time windows, dependencies, priorities, objectives) → executable, verifiable plan. Synthetic, constraint-driven generation (Generator/Responder/Critic loop) + human QC.
2. **Format**: HF `tencent/PlanningBench`, file `data/PlanningBench-eval.jsonl` (3.8 MB), **467 rows** (verified), eval-only. Fields: `idx, messages` (always 1 user turn, no system), `checklist` (string: reference plan + verification points). **All 467 prompts are Chinese** (verified). Prompt length 990–6,027 chars (median 2,367).
3. **Native categories**: README defines 6 families (Scheduling & Timetabling; Project & Production Operations; Routing & Travel; Emergency Response & Public Service; Allocation & Matching; Shift & Workforce Scheduling) and 30+ task types — **but the released jsonl carries NO per-item category field**. Keyword proxy only (分配 154, 应急 93, 路线 90, 调度 81, 项目 77, 排班 50, 会议 50 …; overlapping).
4. **Difficulty**: no per-item label (difficulty is a generation-time control, not released).
5. **Mode**: direct (self-contained; all info in prompt).
6. **Purity**: high for the *planning* half of planning_design; some items are very close to constraint-satisfaction puzzles (optimal dispatch with unique answer) → overlap with `reasoning`.
7. **Other types**: no clear foreign-type subsets; the boundary risk is reasoning (tight-constraint scheduling with a determinate optimum).
8. **Recommendation**: **SAMPLE** (e.g. 100–150; all zh — pair with English planning source such as NATURAL PLAN / TravelPlanner sole-planning for language balance).
9. **License**: CC-BY-4.0 (LICENSE.txt, Tencent). Not gated. 3.8 MB data (~4.7 MB assets).
10. **Sources**: https://huggingface.co/datasets/tencent/PlanningBench · https://arxiv.org/abs/2605.20873 · https://huggingface.co/papers/2605.20873

### Candidate (C) NATURAL PLAN (English supplement)
- Files `data/{trip_planning,meeting_planning,calendar_scheduling}.json` in google-deepmind/natural-plan (19 MB / 24 MB / 6.7 MB). Counts (verified): trip_planning **1,600** (fields `num_cities, cities, durations, prompt_0shot, prompt_5shot, golden_plan, pred_5shot_pro`), meeting_planning **1,000** (`num_people, constraints, dist_matrix, …`), calendar_scheduling **1,000** (`num_people, num_days, duration, …`). No explicit difficulty label, but `num_cities` / `num_people` / `num_days` are native complexity knobs. English only. Borderline with `reasoning` (constraint satisfaction with a unique golden plan). Direct mode (the prompts include the tool outputs as context). Few-shot prompts built in (`prompt_5shot`/`prompt_0shot`). License Apache-2.0 (code) / CC-BY-4.0 (data). Recommendation: SAMPLE. Source: https://github.com/google-deepmind/natural-plan · https://arxiv.org/abs/2406.04520

### Coverage statement
**PlanningBench (Tencent) covers only operational planning/scheduling/allocation. It does NOT cover system/software architecture design, product/solution design, or open-ended design-under-constraints.** Same for PlanBench, NATURAL PLAN, TravelPlanner. → **Coverage gap: the "design" half of planning_design.**

Candidate design benchmarks (none verified as clean, reproducible fits; all UNVERIFIED for data format/size):
- **ArchBench** (arXiv 2603.17833, ICSA 2026 showcase) — platform/CLI for software-architecture tasks; paper says tool & platform openly available; repo URL / task format UNVERIFIED.
- **SAKE** (arXiv 2606.29520) — 2,154 multiple-choice software-architecture *knowledge* questions, 8 categories, CC-BY-4.0 — this is knowledge QA (general_qa-like), not design production; poor fit.
- **QuArch** (arXiv 2510.22087) — computer-architecture QA; knowledge/reasoning, not design; poor fit.
- WritingBench subdomains Requirements Specification (8), Product Proposal (11), Game Design (9), Curriculum Design (14), Technical Documentation (10) can serve as weak design proxies (need human review).
- Suggest: build a small in-house design set (system design interview-style prompts with rubric) — no public benchmark found with clear inputs + reference answers for architecture design.

---

## research_analysis — alternatives beyond LongBench v2

| Candidate | What | Data / size | Labels | Mode | Fit | License | Source |
|---|---|---|---|---|---|---|---|
| **Loong** (EMNLP 2024) | Extended multi-doc QA over financial reports, legal cases, papers; avg ~11 docs/instance | `data/loong.jsonl` on GitHub (3.5 MB, **1,600 rows**, verified) + docs zip `doc.zip` 33.9 MB from Alibaba OSS (link in official README) | `type` financial 700 / legal 500 / paper 400; `level` 1 Spotlight Locating 250 / 2 Comparison 300 / 3 Clustering 641 / 4 Chain of Reasoning 409; `set` 1–4 = length buckets 10K–50K 323 / 50K–100K 564 / 100K–200K 481 / >200K 232; `language` zh 905 / en 695 | direct | **Good** (multi-doc synthesis). Level 1 (spotlight locating) is closer to retrieval/extraction — prefer levels 2–4. Paper-type items (citation-chain/relations) are more structural than analytical. | Apache-2.0 | https://github.com/MozerWang/Loong · https://arxiv.org/abs/2406.17419 |
| **FinanceBench** (Patronus AI) | QA over SEC filings (10-K/10-Q/8-K/earnings) | HF `PatronusAI/financebench`, `financebench_merged.jsonl` 0.96 MB, **150 rows** (open-source subset; verified). Fields incl. `question, answer, justification, evidence[evidence_text,…], doc_name, doc_link, question_type, question_reasoning, gics_sector, doc_type` | `question_type` metrics-generated / domain-relevant / novel-generated (50 each); `question_reasoning` Numerical reasoning 43, Information extraction 31, Logical reasoning…, None 50 | direct (if evidence pages given) / needs PDFs for full-doc setting | Medium: single-document; many are extraction/number lookups. Use `question_reasoning` containing "Logical"/"Numerical" subset. | CC-BY-NC-4.0 (non-commercial!) | https://huggingface.co/datasets/PatronusAI/financebench · https://github.com/patronus-ai/financebench · https://arxiv.org/abs/2311.11944 |
| **TableBench** (AAAI 2025) | Table QA: fact checking, numerical reasoning, data analysis, visualization | HF `Multilingual-Multimodal-NLP/TableBench`, `TableBench.jsonl` 1.4 MB, **886 rows** (verified); fields `id, qtype, qsubtype, table, question, answer` | `qtype` NumericalReasoning 397 / DataAnalysis 343 / FactChecking 96 / Visualization 50; 18 `qsubtype` (DescriptiveAnalysis, ImpactAnalysis, CorrelationAnalysis, TrendForecasting, StatisticalAnalysis, AnomalyDetection, CausalAnalysis, …) | direct | **Good for "structured data" analysis** — use `qtype=DataAnalysis` (343). NumericalReasoning → mostly math/arithmetics; Visualization (ChartGeneration) → coding. | Apache-2.0 (HF card) | https://huggingface.co/datasets/Multilingual-Multimodal-NLP/TableBench · https://arxiv.org/abs/2408.09174 |
| **DABstep** (Adyen) | Multi-step data-analysis over payments CSV/JSON/manual | HF `adyen/DABstep`, tasks `data/tasks/all.jsonl` **450** (easy 72 / hard 378, verified); context files ~24 MB (payments.csv 23.6 MB) | `level` easy/hard | **agentic** (needs code execution over files) | Good as agentic research_analysis; answers for the 450 test tasks are hidden (all.jsonl `answer` empty — verified); only `dev` split has answers. | CC-BY-4.0 | https://huggingface.co/datasets/adyen/DABstep |
| DocFinQA (Kensho) | Long financial-document QA (full 10-K context) | HF `kensho/DocFinQA`: test.json 581 MB, dev 496 MB, train 3.6 GB — too heavy, **not downloaded** | UNVERIFIED | direct | Mostly numerical program-style QA → math-leaning; low priority | MIT (HF card) | https://huggingface.co/datasets/kensho/DocFinQA |
| FRAMES (Google) | Multi-hop factual QA needing Wikipedia retrieval | HF `google/frames-benchmark` test.tsv 0.49 MB | reasoning_types field (UNVERIFIED values) | needs retrieval → agentic/RAG | Poor fit (retrieval-heavy, not "provided materials") | Apache-2.0 | https://huggingface.co/datasets/google/frames-benchmark |

Recommendation for research_analysis beyond LongBench v2: **Loong levels 2–4 (SAMPLE, stratified by type×level×set; note >100K-token contexts)** + **TableBench DataAnalysis (FILTERED SUBSET)** as the structured-data counterpart; FinanceBench only if non-commercial use is acceptable; DABstep as agentic research_analysis examples (dev split for labels).

---

## Coverage gaps (Part A)
- **planning_design → design half missing**: no public benchmark with clear inputs + references for system/software architecture or product design. ArchBench/SAKE/QuArch are either platform-only (format UNVERIFIED) or knowledge MCQ.
- **PlanningBench is Chinese-only** (467/467) and has no per-item category/difficulty field in the release → need English planning supplement (NATURAL PLAN / TravelPlanner) and our own category tagging.
- **WritingBench** mixes writing with analysis/planning; needs subdomain filtering + human review before use as clean writing_language positives.
- **SimpleQA Verified** has no difficulty field; items are long-tail hard facts, so no "easy general_qa" coverage — capability_need must not be inferred from it.

---

# Part B — HF-hosted benchmarks (LiveBench math/reasoning, MATH-500, LiveCodeBench, LongBench v2)

All counts below were verified locally from files downloaded from official huggingface.co repos on 2026-09-29
(scripts in `/root/bench/jev_eval/scripts/`: `hf_repo_info.py`, `inspect_small.py`, `inspect_longbench_v2.py`,
`longbench_v2_metadata_only.py`, `lcb_metadata_stream.py`). Raw data in `/root/bench/jev_eval/raw/<name>/`.

---

## B1. LiveBench — Mathematics (`livebench/math`) → task_type = math

1. **Measures**: contamination-limited math with objective ground truth (no LLM judge). Three tasks: competition math (AMC/AIME/SMC), olympiad proof-completion (fill masked formulae in IMO/USAMO proofs), AMPS_Hard (synthetic hard calculus/algebra computation).
2. **Format**: HF `livebench/math`, single parquet `data/test-00000-of-00001.parquet` (185,605 B), split `test`, **368 rows**. Fields: `question_id, category, task, subtask, year, turns (list[str], all single-turn), ground_truth, hardness (float, olympiad only), expressions, livebench_release_date, livebench_removal_date, release_date`.
3. **Native categories**: `task` ∈ {AMPS_Hard 150, math_comp 146, olympiad 72}. `subtask`: amps_hard_{characteristic_polynomial 20, complete_square 10, derivatives 10, determinant 10, factor_polynomials 10, gcd 20, geometric_mean 20, integral 10, std 20, variance 20}; math_comp: aime_i_2024 14, aime_ii_2024 15, amc_12a_2023 25, amc_12b_2023 25, smc 17, updated_amc_12a_2023 25, updated_amc_12b_2023 25; olympiad: imo 29, usamo 43.
4. **Difficulty**: no general difficulty label. `hardness` float (0.1–1.0) present only on the 72 olympiad rows (null on 296). Not a usable standard/strong/frontier label.
5. **Mode**: direct (single-turn, answer in `\boxed{}` / fixed format).
6. **Purity for math**: very high — every row is mathematics. Caveat: olympiad items are a structured "match masked formula ids" format (answer = list of expression ids), still math-core but atypical prompt shape. AMPS_Hard `std/variance/geometric_mean` are statistics computation — still math.
7. **Items belonging to another task_type**: none.
   Release/removal breakdown (task | release | removal): AMPS_Hard 06-24|2024-08-31:50, 06-24|none:50, 08-31|none:50; math_comp 06-24|08-31:50, 06-24|none:46, 08-31|2025-04-02:50; olympiad 06-24|08-31:36, 08-31|none:36. Rows with `livebench_removal_date==""` (182) = still-active as of the HF snapshot.
8. **Recommendation**: **FULL** (368 is small), or SAMPLE stratified by `task` if balancing against other types. Note HF snapshot is stale: repo lastModified 2025-04-07; the LiveBench changelog lists later math changes (2025-11-25 refreshed math_comp/olympiad; 2026-01-08 new task "Integrals with Game") that are **not** in this HF repo; GitHub README: "not all questions for this release are public on Huggingface" (recommends `--livebench-release-option 2024-11-25`).
9. **License / gating / size**: not gated; HF card has no `license` field; LiveBench DATASHEET: "distributed under the Apache License 2.0". Download 186 KB.
10. **Sources**: https://huggingface.co/datasets/livebench/math ; https://github.com/LiveBench/LiveBench (README, changelog.md, docs/DATASHEET.md) ; https://arxiv.org/abs/2406.19314
   - Note: HF card body (math and reasoning) wrongly says "This is the instruction_following category of livebench" — copy-paste boilerplate, ignore.

---

## B2. MATH-500 (`HuggingFaceH4/MATH-500`) → task_type = math

1. **Measures**: 500-problem subset of the MATH competition dataset (Hendrycks et al.), the test split OpenAI used in "Let's Verify Step by Step" (PRM800K).
2. **Format**: `test.jsonl` (446,564 B), split `test`, **500 rows**. Fields: `problem, solution, answer, subject, level, unique_id` (unique_id = original MATH path, e.g. `test/precalculus/807.json`).
3. **Native categories** (`subject`): Algebra 124, Intermediate Algebra 97, Prealgebra 82, Number Theory 62, Precalculus 56, Geometry 41, Counting & Probability 38.
4. **Difficulty** (`level`, int 1–5): L1 43, L2 90, L3 105, L4 128, L5 134. This is MATH's native difficulty (AoPS-derived), NOT our capability_need; do not map it to standard/strong/frontier without a separate calibration.
5. **Mode**: direct.
6. **Purity for math**: essentially 100%.
7. **Other task_type**: none.
8. **Recommendation**: **SAMPLE** stratified by level×subject (e.g. 100–150), since heavily contaminated/saturated; keep level as metadata. FULL is also cheap if wanted.
9. **License / gating / size**: not gated; HF card has no license field. Source repo openai/prm800k LICENSE = MIT (Copyright 2023 OpenAI); original MATH dataset (hendrycks/math) MIT — UNVERIFIED on the HF card itself. 447 KB.
10. **Sources**: https://huggingface.co/datasets/HuggingFaceH4/MATH-500 ; https://github.com/openai/prm800k (MATH splits section) ; https://github.com/hendrycks/math

---

## B3. LiveBench — Reasoning (`livebench/reasoning`) → task_type = reasoning

1. **Measures**: non-math logical reasoning with objective answers.
2. **Format**: parquet `data/test-00000-of-00001.parquet` (88,219 B), split `test`, **200 rows**. Fields: `question_id, category, ground_truth, turns, task, livebench_release_date, livebench_removal_date, level`.
3. **Native categories — task names in HF public data (only 3)**:
   - `zebra_puzzle` 100 (Einstein-style constraint satisfaction; 50 released 2024-06-24 removed 2024-11-25; 50 released 2024-11-25, active)
   - `web_of_lies_v2` 50 (truth-teller/liar deduction; released 2024-06-24, removed 2025-04-02)
   - `spatial` 50 (2D/3D geometric shape cutting/arrangement reasoning; released 2024-07-26, active)
   - Tasks named in the LiveBench changelog but **NOT in HF public data**: `web_of_lies_v3`, `theory_of_mind` (2025-11-25, replaced web_of_lies_v3), "Logic with Navigation" (2025-12-23). Removed earlier: house_traversal.
4. **Difficulty**: `level` only on zebra_puzzle (50 of 100 rows non-null; values 8–20 = puzzle size/level, counts 8:3, 9:3, 12:3, 13:5, 14:4, 15:4, 16:10, 17:5, 18:3, 19:4, 20:6). Otherwise none.
5. **Mode**: direct.
6. **Purity for reasoning**: high. `spatial` borders on math (geometry of solids/cuts, counting pieces) — it is geometric/spatial reasoning with no calculation-heavy math; our taxonomy lists "spatial" under reasoning, so keep, but flag as the most math-adjacent. zebra & web_of_lies are pure constraint/deduction.
7. **Other task_type**: none clearly; `spatial` is a mild math/reasoning boundary case.
8. **Recommendation**: **FULL** (200). Only 3 task families → low diversity; supplement from elsewhere if possible (causal / planning-free deduction). Prompts are templated and highly recognizable (risk of router overfitting to template surface).
9. **License / gating / size**: not gated; Apache-2.0 per LiveBench DATASHEET; 88 KB.
10. **Sources**: https://huggingface.co/datasets/livebench/reasoning ; https://github.com/LiveBench/LiveBench/blob/main/changelog.md

---

## B4. LiveCodeBench code generation (`livecodebench/code_generation_lite`) → task_type = coding

1. **Measures**: competitive-programming code generation (LeetCode, AtCoder, Codeforces), date-tagged for contamination control; graded by hidden tests.
2. **Format**: loading-script dataset (`code_generation_lite.py`, `version_tag=` arg). Files: `test.jsonl` 1,252,609,773 B; `test2.jsonl` 713,377,060; `test3.jsonl` 623,360,766; `test4.jsonl` 1,204,644,685; `test5.jsonl` 557,699,297; `test6.jsonl` 134,303,240 → **total ≈ 4.49 GB**. Fields: `question_title, question_content, platform, question_id, contest_id, contest_date, starter_code, difficulty, public_test_cases, private_test_cases, metadata` (private_test_cases is the bulk of the size).
   Versions (script `ALLOWED_FILES`): release_v1=test; v2=+test2; v3=+test3; v4=+test4; v5=+test5; v6/release_latest=+test6. Also delta tags `v1..v6` (single file) and ranges like `v4_v5`.
   Official counts/date ranges (README/GitHub): v1 400 (May 2023–Mar 2024), v2 511 (–May 2024), v3 612 (–Jul 2024), v4 713 (–Sep 2024), v5 880 (–Jan 2025), v6 1055 (–Apr 2025; GitHub README only, HF card stops at v5).
   LOCAL_COUNTS_PLACEHOLDER
3. **Native categories**: `platform` (leetcode/atcoder/codeforces); no topic labels. `starter_code` non-empty ≈ LeetCode function-signature style vs stdin/stdout style.
4. **Difficulty**: `difficulty` ∈ {easy, medium, hard} (platform-derived). Not our capability_need.
5. **Mode**: direct (single-shot generation; self-repair scenario is multi-turn but separate).
6. **Purity for coding**: ~100% coding, but narrow (algorithmic competitive programming only — no software engineering, debugging, repo work). Many problems are math-flavored (number theory/combinatorics) — core is still writing code, so label coding.
7. **Other task_type**: none; boundary: math-heavy problems could confuse a router between math and coding — useful hard negatives.
8. **Recommendation**: **SAMPLE** stratified by difficulty × platform, preferably from the newest window (v5/v6 deltas: test5+test6) for less contamination. Only metadata fields needed.
9. **License / gating / size**: not gated. HF card `license: cc` (unspecified variant); loading script `license="MIT License"`; GitHub repo LICENSE MIT (Copyright 2024 LiveCodeBench). Underlying problems come from LeetCode/AtCoder/Codeforces — their ToS apply (UNVERIFIED). Full download 4.49 GB (exceeds 1.5 GB cap → not stored).
   **Fetching only question/metadata**: HF datasets-server does NOT support this repo ("runs arbitrary Python code"; no auto-parquet), so no column projection. Per-version files can be fetched individually (e.g. only `test6.jsonl`, 134 MB). Our approach: `scripts/lcb_metadata_stream.py` streams each jsonl over HTTP and writes only the metadata fields (drops test cases) to `raw/livecodebench/metadata_no_tests.jsonl` — disk stays small but bandwidth is the full ≈4.5 GB (slow: ~1–2 MB/s here).
10. **Sources**: https://huggingface.co/datasets/livecodebench/code_generation_lite ; https://github.com/LiveCodeBench/LiveCodeBench ; https://livecodebench.github.io/ ; https://arxiv.org/abs/2403.07974

---

## B5. LongBench v2 (`THUDM/LongBench-v2`, now redirects to `zai-org/LongBench-v2`) → candidate for research_analysis

1. **Measures**: deep understanding/reasoning over realistic long contexts (8k–2M words), 503 four-choice MCQs, human experts 53.7% under 15-min limit.
2. **Format**: single `data.json` (465,490,535 B), split `train`, **503 rows**. Fields: `_id, domain, sub_domain, difficulty, length, question, choice_A..D, answer (A–D), context`. Context char length: short mean ≈123k chars, medium ≈500k, long ≈2.86M (max 16.2M chars). All questions English (1 CJK in New language translation).
   Official prompt (GitHub `prompts/0shot.txt`): "Please read the following text and answer the question below.\n\n<text>\n$DOC$\n</text>\n\nWhat is the correct answer to this question: $Q$\nChoices:\n(A) $C_A$ ... Format your response as follows: \"The correct answer is (insert answer here)\"."
3. **Native categories (domain / sub_domain, counts)**:
   - Single-Document QA 175: Academic 44, Detective 22, Event ordering 20, Financial 22, Governmental 18, Legal 19, Literary 30
   - Multi-Document QA 125: Academic 50, Financial 15, Governmental 23, Legal 14, Multi-news 23
   - Long In-context Learning 81: Many-shot learning 21, New language translation 20, User guide QA 40
   - Long-dialogue History Understanding 39: Agent history QA 20, Dialogue history QA 19
   - Code Repository Understanding 50: Code repo QA 50
   - Long Structured Data Understanding 33: Knowledge graph reasoning 15, Table QA 18
4. **Difficulty**: `difficulty` ∈ {easy 192, hard 311}; hard = "at least two out of three models do not answer correctly in automated review and the human reviewer is unable to solve it within 10 minutes" (paper). `length` ∈ {short 180 (<32k words), medium 215 (32k–128k), long 108 (>128k)}.
   Per domain easy/hard: MDQA 34/91; LSDU 20/13. Length MDQA short 58/medium 44/long 23; LSDU 4/23/6.
5. **Mode**: direct (single request, huge context). Not agentic.
6. **Purity for research_analysis** (synthesize provided materials into analytical conclusion):
   - **Multi-news (23)**: high — cross-article synthesis, timelines, "which conclusion is most reliable". Some are shallow lookup ("Which one is noted in all the five passages?").
   - **Governmental (23)**: high — cross-report comparisons/inferences (e.g., NSW Health 2020-21 vs 2022-23).
   - **Financial (15)**: high — multi-report analysis incl. numeric computation (e.g. PUMA H2 EBIT % increase), some scenario-analysis items.
   - **Academic (50)**: medium-high — synthesis across papers, but some are generic "Which statement is correct?"; content is scholarly, fine.
   - **Legal (14)**: medium — mix of case-comparison synthesis and some items that are legal-knowledge application/hypothetical-case reasoning (may lean reasoning/general_qa).
   - **Table QA (18)**: medium-high — multi-cell/multi-table integration; data-analysis flavored.
   - **Knowledge graph reasoning (15)**: LOW — Wikidata-style triple lookups ("inception time of award received by Q181659 in 1995", "Ireland counties with plate code DL") → structured retrieval/logic, closer to general_qa/reasoning than analytical synthesis. Exclude or tag as boundary.
   - Other domains are NOT candidates: Code repo QA → coding; Many-shot learning/New language translation → writing_language/reasoning-ish ICL; User guide QA, Single-Doc QA → borderline (single long doc); Dialogue/Agent history QA → memory retrieval.
   - Format caveat: every item is 4-choice MCQ over a pasted mega-context; for a router, the *prompt as sent* (context+question+choices) is the realistic input. If we only store question text without context, the item loses its "provided materials" signal → classifier would see only a short question. Router input should include (truncated) context.
7. **Other task_type items**: see above (Code Repository → coding; KG reasoning → reasoning/general_qa; New language translation → writing_language; Many-shot learning → reasoning).
8. **Recommendation**: **FILTERED SUBSET** = Multi-Document QA (all 5 sub_domains, 125; optionally drop Legal knowledge-application items after manual review) + Table QA (18) → ~143 items; exclude Knowledge graph reasoning. Consider Single-Doc Financial/Governmental (40) as secondary candidates. Count is modest; supplement with other research-analysis benchmarks (handled by another part).
9. **License / gating / size**: not gated. HF card `license: apache-2.0`; GitHub repo THUDM/LongBench LICENSE = MIT (Copyright 2023 THU-KEG & Zhipu AI) — card vs repo differ; data license per card = Apache-2.0. Size: data.json 465 MB (downloaded, under cap). HF auto-converted parquet (`refs/convert/parquet`, default/train/0000.parquet) = 161.5 MB, single row group.
   **Metadata-only fetch — works**: `scripts/longbench_v2_metadata_only.py` uses `HfFileSystem` + pyarrow column projection on the auto-parquet, reading all columns except `context`: 503 rows in ~3 s, ~0.3 MB transferred. datasets-server `/first-rows` fails ("row groups are too big", 384 MiB > 286 MiB), so `/rows` API is not usable; column projection on parquet is. Saved: `raw/longbench_v2/metadata_no_context.jsonl`.
10. **Sources**: https://huggingface.co/datasets/THUDM/LongBench-v2 (→ https://huggingface.co/datasets/zai-org/LongBench-v2) ; https://github.com/THUDM/LongBench ; https://longbench2.github.io ; https://arxiv.org/abs/2412.15204

---

## workflow_operation: AutomationBench (local v1.0.6)

1. **What it measures**: Agents executing realistic business workflows in a simulated environment of 47 SaaS tools (CRM, Gmail, Slack, Calendar, Sheets, ticketing, accounting, HRIS...). Each task = trigger prompt + pre-populated world state; graded by assertions on the FINAL world state (e.g. `salesforce_field_equals`, `gmail_message_sent_to_with_body_contains`, `slack_message_not_in_channel`). Metrics: `partial_credit` and strict `task_completed_correctly` (official pass rate = mean of strict over the 600 non-simple tasks). Official leaderboard uses a held-out private set; the repo is the public set.
2. **Data format**: Tasks are Python dicts in `automationbench/domains/<domain>/tasks.py` (huge files, e.g. sales/tasks.py ~32k lines), assembled into a HF `datasets.Dataset` by `get_<domain>_dataset()`. Row fields: `example_id`, `prompt` (list of messages: exactly `[system, user]` for all 800 tasks), `answer` (""), `info` = {`zapier_tools` (per-task tool name list), `initial_state` (world state JSON), `assertions`, `task_name` (moved from `task` at dataset build time, e.g. `sales.multi_hop_lookup`, `simple.email_sf_contact_phone_update`)}. `apply_noise()` injects deterministic distractor records into initial_state (seed = example_id); it does not change the prompt.
   - Counts (verified by loading all loaders locally): simple 200, sales 100, marketing 100, operations 100, support 100, finance 100, hr 100 → 800 total (600 scored). sales/tasks.py has 106 `"task":` literals but only 100 are included in the dataset list.
   - User prompt length (chars, median/max): simple 185/368, sales 282/714, marketing 437/744, operations 729/1254, support 434/1168, finance 463/744, hr 406/745. Median `zapier_tools` per task: simple 2, domains 8–12.
3. **Native category labels**: domain (7 values above) and `task_name` (`<domain>.<slug>`, unique per task). No finer taxonomy field.
4. **Native difficulty labels**: none per task. Only implicit: `simple` domain = "foundational single- and two-step tasks", excluded from score (README). Private set is "purposely harder" (not released).
5. **Direct vs agentic**: agentic (multi-turn tool use, default `--max-steps 50`; system prompt mentions ~50 tool-using turns).
6. **Purity for workflow_operation**: HIGH. All tasks are graded on external state changes (emails sent, CRM fields updated, sheet rows written, Slack posts). Checked assertion types: only 3/800 tasks have exclusively negative ("not sent / not exists") assertions (1 sales, 2 simple) — i.e. the correct action is to NOT act (policy trap). Many domain tasks embed reasoning sub-steps (FX conversion, weighted scoring, policy lookups in emails/sheets), but the output is always an operation, so they remain workflow_operation positives.
7. **Items belonging to another task_type**: none cleanly. Caveat: some tasks are "report/recap" style (e.g. `sales.historical_win_loss_recap`, finance reporting) where the substance is data synthesis, but the deliverable is still posting/sending via tools → keep as workflow_operation; optionally tag as secondary research_analysis.
8. **Recommendation**: **FULL** 600 public domain tasks (stratified by domain if sampling), plus `simple` 200 as a separate easy/"standard"-candidate slice (not a benchmark-defined capability label — do not map to capability_need automatically).
9. **License / gating / size**: MIT (Copyright 2026 Zapier, Inc.). Not gated. Local repo; reconstructed first-request dumps: api 1.2 MB, limited_zapier 8.7 MB, zapier 1.2 MB.
10. **Sources**: https://github.com/zapier/AutomationBench ; paper https://arxiv.org/abs/2604.18934 ; https://zapier.com/benchmarks ; local /root/bench/AutomationBench (pyproject version 1.0.6).

**How the first request is built (verified in code, no model run)**:
- `scripts/eval.py` → `get_combined_dataset(domains)` → `AutomationBenchEnv(dataset, rubric, max_turns, toolset, search_top_k)` (verifiers `StatefulToolEnv`). CLI default `--toolset api` (note: the Python function default is "zapier", but argparse default is "api").
- messages = task `prompt` as-is: `system` = one shared `SYSTEM_PROMPT` (identical across all 800 tasks: "You are a workflow automation agent. Execute the requested tasks using the available tools. Do not ask clarifying questions ... budget of ~50 tool-using turns ... list only items you acted on ..."), `user` = the task text. No initial state is shown in the prompt — the agent must discover it via tools.
- tools depend on toolset (`runner.py` `__init__` + `setup_state`):
  - `api` (default): 3 generic tools for every task: `api_search(query, top_k)`, `api_fetch(method, url, params, body)`, `base64_encode(text)` → tools reveal nothing about the task domain.
  - `limited_zapier`: only the task's `info.zapier_tools` (from a registry of 549 Zapier-style tools, e.g. `salesforce_find_records`, `gmail_send_email`).
  - `zapier`: 2 meta-tools `search_tools` / `execute_tool`.
- Script: `/root/bench/jev_eval/scripts/automationbench_first_request.py [api|limited_zapier|zapier]` (run with `/root/bench/AutomationBench/.venv/bin/python`) → `/root/bench/jev_eval/raw/automationbench/first_requests_<toolset>.jsonl` (domain, example_id, messages, tools, zapier_tools_listed). Note `task` field is None in the dumps because the task name lives in `info.task_name`; add it if needed.

---

## Agentic sources (execution_mode only)

### DeepSWE (local /root/bench/deep-swe)
1. **Measures**: frontier coding agents on original, long-horizon SWE tasks (feature implementation in real OSS repos), program-based verifiers in a separate pristine container.
2. **Format**: Harbor task format. `tasks/` has 117 entries = **113 task dirs** + `dataset.toml`, `manifest.json`, `manifest.schema.json`, `README.md` (so "117 dirs" is actually 113 tasks + 4 files). Each task: `task.toml` (metadata: task_id, display_title, display_description, category, language, repository_url, base_commit_hash; docker_image; agent timeout 10800 s, no-network), `instruction.md` (= the prompt the agent sees; 571–5,484 chars, median ~2.2k), `environment/`, `tests/`, `solution/`. Dataset name `datacurve/deep-swe-1-1` (v1.1).
3. **Categories**: `category`: feature_request 106, enhancement 3, bugfix 4. `language`: go 34, python 34, typescript 35, javascript 5, rust 5.
4. **Difficulty**: none.
5. **agentic** (mini-swe-agent in sandbox, hours-long).
6. **Purity**: 100% coding (for task_type), 100% agentic.
7. Other task_types: none.
8. **Recommendation**: FULL (113) as agentic+coding positives.
9. License: Apache-2.0 for Datacurve contributions; upstream repos under their own permissive licenses (PROVENANCE.md). Docker images on public.ecr.aws (not needed for classification).
10. Sources: https://github.com/datacurve-ai/deep-swe ; https://deepswe.datacurve.ai/ ; Pier https://github.com/datacurve-ai/pier

**First request (mini-swe-agent via Pier)** — verified in local Pier 0.3.1 source (`pier/agents/installed/mini_swe_agent.py`): command is `mini-swe-agent --yolo --model=<m> --task=<instruction.md text> --output=... -c mini.yaml [-c agent.cost_limit=0] [...] --exit-immediately`. So the config is mini-swe-agent's built-in **`mini.yaml`** (tool-calling mode), `--yolo` (no confirm), Pier default cost_limit=0 (no limit). The task text passes through `render_instruction` (only changes it if a prompt_template_path is configured; none by default) and MCP info is appended only if MCP servers are configured.
- `mini.yaml` (local mini-swe-agent 2.4.6; matches official https://github.com/SWE-agent/mini-swe-agent/blob/main/src/minisweagent/config/mini.yaml — checked system_template + head of instance_template, step_limit 0, cost_limit 3., mode confirm):
  - system: `You are a helpful assistant that can interact with a computer.`
  - user (instance_template): `Please solve this issue: {{task}}` + "You can execute bash commands and edit files..." + Recommended Workflow (6 steps, submit with `echo COMPLETE_TASK_AND_SUBMIT_FINAL_OUTPUT`) + Command Execution Rules + `<system_information>{{system}} {{release}} {{version}} {{machine}}</system_information>` + useful command examples.
  - tools: single `bash` tool `{"command": string}` (`minisweagent/models/utils/actions_toolcall.py` BASH_TOOL).
  - The older text-based `default.yaml` (```mswea_bash_command``` blocks, no tools) is NOT what Pier uses.
- DeepSWE README only says "All leaderboard scores were produced with Pier running mini-swe-agent on Modal"; exact mini-swe-agent version / cost limit / step limit for the leaderboard is **UNVERIFIED** (not documented).
- Script: `/root/bench/jev_eval/scripts/miniswe_first_request.py` (run with `/root/bench/.msa/bin/python`) → `/root/bench/jev_eval/raw/agentic_first_requests/{deepswe,tb4,tb2}_miniswe_first_requests.jsonl` (113 / 66 / 89 rows). uname fields are placeholders (they come from the task container at runtime).

### Terminal-Bench 4.0 (local /root/bench/tb4/terminal-bench-4.0.0)
1. **Measures**: agents completing hard, realistic tasks in a terminal (continuous benchmark, tagged releases).
2. **Format**: Harbor format, `tasks/<id>/{task.toml, instruction.md, environment/, tests/, solution/}`; 66 task dirs + `dataset.toml` (header comment says "terminal-bench/terminal-bench-3", dataset name `terminal-bench/terminal-bench`). `archive/` holds 2 removed tasks (erp-procurement-planning, gpt2-codegolf). Instruction = `instruction.md` (starts with a harbor-canary HTML comment); median ~1.6k chars, max 6.5k.
3. **Categories**: `category`: Software 18, Science 14, ML 11, Operations 9, Hardware 5, Security 5, Media 4; plus `subcategory` (29 values, e.g. Systems, Inference, Frontend, Chemistry, CAD, Claims, Biology, Algorithms, Logistics, Math, Finance, Compliance, Marketing...) and `tags`, `expert_time_estimate_hours`.
4. **Difficulty**: no discrete difficulty field; 6 tasks have free-text `difficulty_explanation`; `expert_time_estimate_hours` numeric.
5. agentic.
6. **Purity**: execution_mode agentic 100%. task_type is mixed — most are coding/terminal engineering, but some are domain workflows/analysis (e.g. Claims auditing, freight dispatch planning, utility billing via legacy GUI, genomics variant cataloguing, Math subcategory). Use only as agentic signal, or label task_type per item manually.
7. Other task_types: Science/*, Operations/Claims/Logistics/Compliance/Finance/Marketing, Math subcategory → research_analysis / planning_design / workflow_operation / math candidates (needs per-item review).
8. **Recommendation**: FULL for execution_mode=agentic; FILTERED (manual per-item task_type) if used for task_type.
9. License Apache-2.0 (GitHub API). Releases: v3.0.0 2026-07-23, v4.0.0 2026-08-26 (GitHub API); v4.0.0 = 74 v3 tasks − 8 removed = 66 (release notes, via fetch).
10. Sources: https://github.com/harbor-framework/terminal-bench ; https://github.com/harbor-framework/terminal-bench/releases ; https://hub.harborframework.com/datasets/terminal-bench/terminal-bench ; https://www.tbench.ai/

### Terminal-Bench 2.0 (local /root/bench/tb2/terminal-bench)
1. Measures: same family, 2.0 release.
2. Format: 89 task dirs directly under the folder (no tasks/ subdir), each `task.toml` + `instruction.md` + environment/tests/solution. Official repo harbor-framework/terminal-bench-2 (laude-institute/terminal-bench-2 redirects) has 89 task dirs (GitHub API) — matches local.
3. Categories (`category`): software-engineering 26, system-administration 9, security 8, scientific-computing 8, data-science 8, file-operations 5, debugging 5, model-training 4, mathematics 4, data-processing 4, machine-learning 3, video-processing, personal-assistant, optimization, games, data-querying (1 each). Plus tags, expert/junior time estimates.
4. **Difficulty**: `difficulty` = easy 4 / medium 55 / hard 30.
5. agentic. 6–7. Mostly coding/sysadmin; `mathematics` (4), `data-science`/`scientific-computing` partly research_analysis/math; `personal-assistant` (1) workflow-like.
8. Recommendation: FULL for execution_mode=agentic; filtered per item for task_type.
9. Apache-2.0 (per repo page). 10. https://github.com/harbor-framework/terminal-bench-2 ; run: `harbor run --dataset terminal-bench@2.0`.

**First request for TB**: depends on agent. With mini-swe-agent via Harbor (`harbor/agents/installed/mini_swe_agent.py`: `mini-swe-agent --yolo ... --task=<instruction> -c mini ...`) it is the same mini.yaml system/instance template + bash tool as above, `{{task}}` = instruction.md. The TB reference agent Terminus-2 instead uses its own template (`harbor/agents/terminus_2/templates/terminus-json-plain.txt`: "You are an AI assistant tasked with solving command-line tasks in a Linux environment..." with JSON analysis/plan/commands, no native tools).

---

## Coverage gaps (overall)
- planning_design: no public benchmark with clear inputs/answers covers system/software/architecture design; PlanningBench/NATURAL PLAN/PlanBench cover planning/scheduling only. WritingBench planning/design-like subdomains (~13) are a partial, unverified-answer stopgap.
- research_analysis: LongBench v2 filtered subset is only ~143 items; supplement with Loong (levels 2-4), TableBench DataAnalysis; FinanceBench is CC-BY-NC.
- reasoning: LiveBench reasoning has only 3 templated task families (low diversity).
- coding (direct): LiveCodeBench is competitive programming only; no direct-mode software-engineering source. Agentic coding covered by DeepSWE/TB.
- capability_need (standard/strong/frontier): no benchmark defines it; must be labelled separately.
- LiveBench HF snapshots are stale vs the live leaderboard (later tasks not public).
