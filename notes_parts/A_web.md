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
