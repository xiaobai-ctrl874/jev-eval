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
   Local verification (streamed, metadata only): `test.jsonl` = 400 rows (v1 ✓), contest_date 2023-05-07..2024-03-02, easy 142 / medium 168 / hard 90, atcoder 210 / leetcode 181 / codeforces 9. `test6.jsonl` = 175 rows (= 1055−880 ✓), contest_date 2025-01-04..2025-04-06, easy 43 / medium 52 / hard 80, atcoder 112 / leetcode 63. Stream completed: all 6 files → **1055 unique question_ids** in `raw/livecodebench/metadata_no_tests.jsonl` (≈ release_v6 ✓).
   Per file (easy/medium/hard; atcoder/leetcode/codeforces; contest_date range):
   - test (v1): 400 = 142/168/90; 210/181/9; 2023-05-07..2024-03-02
   - test2 (v2 delta): 111 = 40/38/33; 57/54/0; 2024-03-09..2024-05-25
   - test3 (v3 delta): 101 = 34/39/28; 53/48/0; 2024-06-01..2024-08-10
   - test4 (v4 delta): 101 = 22/34/45; 65/36/0; 2023-08-26..2024-10-05 (min date predates v3 — some older problems added late)
   - test5 (v5 delta): 167 = 41/52/74; 105/62/0; 2024-09-22..2025-01-04
   - test6 (v6 delta): 175 = 43/52/80; 112/63/0; 2025-01-04..2025-04-06
   - Total: easy 322 / medium 383 / hard 350.
   Streaming took ~70 min total for ~4.5 GB of bandwidth (disk use: metadata file only).
   `starter_code` is non-empty for 100% of LeetCode rows and 0% of AtCoder/Codeforces rows.
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
