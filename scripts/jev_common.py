"""Shared loaders / helpers for the Jev classification evaluation datasets.

Everything here is deterministic: every random choice uses a fresh
random.Random(SEED) (SEED = 20260929) and every input collection is sorted
before it is shuffled, so re-running the build scripts yields byte-identical
files.  No model or Jev API is called anywhere; gold labels come only from
benchmark-native fields, fixed rule mappings, or explicit hand-written entries
marked human_review_required.
"""
from __future__ import annotations

import json
import os
import random
import tomllib
from collections import defaultdict
from functools import lru_cache

import pandas as pd

SEED = 20260929
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(REPO, "raw")

DEEPSWE_ROOT = "/root/bench/deep-swe/tasks"
TB4_ROOT = "/root/bench/tb4/terminal-bench-4.0.0/tasks"
TB2_ROOT = "/root/bench/tb2/terminal-bench"

TASK_TYPES = ["general_qa", "writing_language", "math", "reasoning", "coding",
              "research_analysis", "planning_design", "workflow_operation"]
EXEC_MODES = ["direct", "agentic"]
CAPABILITY = ["standard", "strong", "frontier"]
LABEL_SOURCES = ["benchmark_native", "rule_mapping", "human_review_required"]
CONFIDENCES = ["high", "medium", "low"]

REQUIRED_FIELDS = ["id", "benchmark", "source_id", "prompt", "system_prompt", "tools",
                   "gold_task_type", "gold_execution_mode", "gold_capability_need",
                   "official_category", "official_difficulty", "label_source",
                   "label_confidence", "notes"]

# LongBench v2 excerpt budget for prompt_as_sent (chars).
LB_MAX_CHARS = 20000

# ---------------------------------------------------------------- utilities


def make_id(bench_key: str, source_id) -> str:
    return f"{bench_key}:{source_id}"


def rng() -> random.Random:
    """Fresh generator with the fixed seed for every random choice."""
    return random.Random(SEED)


def _skey(v):
    return "" if v is None else str(v)


def sample_quota(items, quotas, top_key, sub_key=None, sort_key=None):
    """Stratified sample.  quotas: {top_value: n}.  Within a top stratum, items are
    drawn round-robin over sub_key strata (sub strata visited in a seeded random
    order, items within each sub stratum seeded-shuffled).  Raises if a quota
    cannot be met (callers pass quotas that fit)."""
    r = rng()
    sort_key = sort_key or (lambda x: str(x["_sid"]))
    out = []
    for top in sorted(quotas, key=_skey):
        n = quotas[top]
        pool = sorted([x for x in items if top_key(x) == top], key=sort_key)
        groups = defaultdict(list)
        for x in pool:
            groups[_skey(sub_key(x)) if sub_key else ""].append(x)
        order = sorted(groups)
        r.shuffle(order)
        for g in order:
            r.shuffle(groups[g])
        picked = []
        while len(picked) < n and any(groups[g] for g in order):
            for g in order:
                if groups[g] and len(picked) < n:
                    picked.append(groups[g].pop())
        if len(picked) < n:
            raise ValueError(f"quota {n} for stratum {top!r} not met ({len(picked)})")
        out.extend(picked)
    return out


def sample_round_robin(items, n, key, sort_key=None):
    """Round-robin over strata of `key` (strata order seeded-random), n items."""
    return sample_quota(items, {"__all__": n}, lambda x: "__all__", key, sort_key)


def weakest(*sources):
    order = {s: i for i, s in enumerate(LABEL_SOURCES)}
    s = [x for x in sources if x]
    return max(s, key=lambda x: order[x]) if s else None


def write_jsonl(path, records):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    records = sorted(records, key=lambda r: r["id"])
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        for rec in records:
            f.write(json.dumps(rec, ensure_ascii=False, sort_keys=False) + "\n")


def out_dir_arg(argv):
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default=REPO)
    return ap.parse_args(argv).out_dir


def record(*, bench_key, benchmark, source_id, prompt, system_prompt=None, tools=None,
           gold_task_type, task_type_label_source, task_type_confidence,
           gold_execution_mode, execution_mode_label_source="rule_mapping",
           execution_mode_confidence="high", official_category=None,
           official_difficulty=None, notes="", primary="task_type", **extra):
    """Build one dataset row.  label_source / label_confidence describe the
    dataset's primary label (task_type for classification/boundary/capability
    files, execution_mode for the execution-mode file); the per-dimension
    sources are always kept in task_type_label_source / execution_mode_label_source."""
    if primary == "task_type":
        ls, lc = task_type_label_source, task_type_confidence
    else:
        ls, lc = execution_mode_label_source, execution_mode_confidence
    rec = {
        "id": make_id(bench_key, source_id),
        "benchmark": benchmark,
        "source_id": str(source_id),
        "prompt": prompt,
        "system_prompt": system_prompt,
        "tools": tools,
        "gold_task_type": gold_task_type,
        "gold_execution_mode": gold_execution_mode,
        "gold_capability_need": None,
        "official_category": official_category,
        "official_difficulty": official_difficulty,
        "label_source": ls,
        "label_confidence": lc,
        "notes": notes,
        "task_type_label_source": task_type_label_source,
        "task_type_confidence": task_type_confidence,
        "execution_mode_label_source": execution_mode_label_source,
        "execution_mode_confidence": execution_mode_confidence,
    }
    rec.update(extra)
    return rec


# ---------------------------------------------------------------- SimpleQA Verified


@lru_cache(None)
def load_simpleqa():
    df = pd.read_csv(os.path.join(RAW, "simpleqa_verified", "simpleqa_verified.csv"))
    rows = []
    for r in df.to_dict("records"):
        r["_sid"] = int(r["original_index"])
        rows.append(r)
    return rows


def simpleqa_record(r, notes_extra="", **kw):
    base = dict(
        bench_key="simpleqa_verified", benchmark="SimpleQA Verified", source_id=r["_sid"],
        prompt=r["problem"], gold_task_type="general_qa",
        task_type_label_source="rule_mapping", task_type_confidence="high",
        gold_execution_mode="direct",
        official_category=f"topic={r['topic']}|answer_type={r['answer_type']}",
        official_difficulty=None,
        notes=("Benchmark-level rule: SimpleQA Verified short-form factual QA -> general_qa; "
               "no-tools benchmark -> direct. No native difficulty field. " + notes_extra).strip(),
        multi_step=bool(r["multi_step"]), requires_reasoning=bool(r["requires_reasoning"]),
        prompt_format="question text as-is (official autorater setup sends the bare question)",
    )
    base.update(kw)
    return record(**base)


def simpleqa_pool():
    return [r for r in load_simpleqa() if not r["requires_reasoning"]]


# ---------------------------------------------------------------- WritingBench

WB_CLEAN = {
    # Advertising & Marketing
    "Slogans", "Promotional Copy", "Product Description", "Brand Story", "Social Media Content",
    "Promotional Voiceover", "Sales Letter", "Personal Blog", "Multimedia Script",
    # Literature & Arts (creative)
    "Poetry", "Prose", "Lyric Writing", "Fan Fiction", "Novel Manuscript", "Screenplay",
    "Video Script", "Podcast Script", "Greeting Message", "Host Script",
    # Academic section writing
    "Abstract", "Introduction", "Conclusion", "Acknowledgements", "Contributions", "Limitations",
    # Politics & Law
    "Government Speech", "Official Document", "Legal Awareness Campaign",
    "Party Membership Application",
    # correspondence / summarisation
    "Business Correspondence", "Meeting Minutes", "Meeting Summary",
}

import re as _re
_WB_ANALYZE = _re.compile(r"analy[sz]|evaluat|assess|critique|分析|评估|评价|点评|评析|研判", _re.I)


@lru_cache(None)
def load_writingbench():
    rows = []
    with open(os.path.join(RAW, "writingbench", "benchmark_all.jsonl"), encoding="utf-8") as f:
        for line in f:
            r = json.loads(line)
            r["_sid"] = int(r["index"])
            rows.append(r)
    return rows


@lru_cache(None)
def wb_flagged():
    with open(os.path.join(RAW, "writingbench", "flagged_analysis_candidates.jsonl"), encoding="utf-8") as f:
        return frozenset(int(json.loads(l)["index"]) for l in f)


def wb_long_analyze(r):
    """>5,000-char query whose instruction (first or last 600 chars) asks to analyze/evaluate."""
    q = r["query"]
    return len(q) > 5000 and bool(_WB_ANALYZE.search(q[:600]) or _WB_ANALYZE.search(q[-600:]))


def writingbench_pool():
    return [r for r in load_writingbench()
            if r["domain2"] in WB_CLEAN and not wb_long_analyze(r) and r["_sid"] not in wb_flagged()]


def wb_record(r, *, gold_task_type="writing_language", tt_source="rule_mapping", tt_conf=None,
              notes=None, **kw):
    conf = tt_conf or ("high" if len(r["query"]) <= 5000 else "medium")
    base = dict(
        bench_key="writingbench", benchmark="WritingBench", source_id=r["_sid"], prompt=r["query"],
        gold_task_type=gold_task_type, task_type_label_source=tt_source, task_type_confidence=conf,
        gold_execution_mode="direct",
        official_category=f"{r['domain1']}/{r['domain2']}", official_difficulty=None,
        notes=notes if notes is not None else (
            "Subdomain rule: domain2 in audited 'cleanest writing_language' list -> writing_language; "
            "excluded: heuristic-flagged analysis candidates and >5K-char queries with analyze/evaluate instructions."),
        lang=r["lang"], query_chars=len(r["query"]),
        prompt_format="query as-is (WritingBench generation sends the query as the user message)",
    )
    base.update(kw)
    return record(**base)


# ---------------------------------------------------------------- LiveBench


@lru_cache(None)
def load_livebench(cat):
    df = pd.read_parquet(os.path.join(RAW, f"livebench_{cat}", "test.parquet"))
    rows = []
    for r in df.to_dict("records"):
        r["turns"] = [str(t) for t in list(r["turns"])]
        r["_sid"] = r["question_id"]
        rows.append(r)
    return rows


# LiveBench math contains 'updated_amc_*' near-duplicates of 'amc_*' items; the twins of
# boundary items are kept out of the clean pools so the same problem is not labelled twice.
LB_MATH_TWIN_EXCLUDE = {"a981ef2141": "twin of boundary item c93744a0f4 (tournament)",
                        "417aea0ce4": "twin of boundary item 1e7ae0275d (covered-square game)"}


def lb_math_twin_excluded(r):
    return any(r["question_id"].startswith(p) for p in LB_MATH_TWIN_EXCLUDE)


def lb_difficulty(r, cat):
    if cat == "math":
        v = r.get("hardness")
        field = "hardness"
    else:
        v = r.get("level")
        field = "level"
    if v is None or (isinstance(v, float) and v != v) or str(v) in ("", "nan", "None"):
        return None, None
    return v, field


def livebench_record(r, cat, *, gold_task_type=None, tt_source="benchmark_native", tt_conf="high",
                     notes=None, **kw):
    diff, dfield = lb_difficulty(r, cat)
    oc = f"{r['category']}/{r['task']}" + (f"/{r['subtask']}" if cat == "math" and r.get("subtask") else "")
    base = dict(
        bench_key=f"livebench_{cat}", benchmark=f"LiveBench {cat}", source_id=r["_sid"],
        prompt=r["turns"][0], gold_task_type=gold_task_type or cat,
        task_type_label_source=tt_source, task_type_confidence=tt_conf,
        gold_execution_mode="direct", official_category=oc,
        official_difficulty=diff,
        notes=notes if notes is not None else (
            f"LiveBench native field category='{r['category']}' maps 1:1 to task_type={cat}; single-turn -> direct."),
        official_difficulty_field=dfield,
        livebench_release_date=str(r["livebench_release_date"]),
        livebench_removal_date=str(r["livebench_removal_date"]),
        prompt_format="turns[0] as-is (single-turn LiveBench question incl. its answer-format instructions)",
    )
    base.update(kw)
    return record(**base)


# ---------------------------------------------------------------- MATH-500


@lru_cache(None)
def load_math500():
    rows = []
    with open(os.path.join(RAW, "math500", "test.jsonl"), encoding="utf-8") as f:
        for line in f:
            r = json.loads(line)
            r["_sid"] = r["unique_id"]
            rows.append(r)
    return rows


def math500_record(r, **kw):
    base = dict(
        bench_key="math500", benchmark="MATH-500", source_id=r["_sid"], prompt=r["problem"],
        gold_task_type="math", task_type_label_source="rule_mapping", task_type_confidence="high",
        gold_execution_mode="direct", official_category=r["subject"], official_difficulty=r["level"],
        notes="Benchmark-level rule: MATH competition problems -> math; direct. official_difficulty = MATH native level (1-5), not capability_need.",
        official_difficulty_field="level",
        prompt_format="problem text as-is (MATH-500 has no single official chat template; harnesses differ)",
    )
    base.update(kw)
    return record(**base)


# ---------------------------------------------------------------- LiveCodeBench

LCB_SYSTEM = ("You are an expert Python programmer. You will be given a question (problem specification) "
              "and will generate a correct Python program that matches the specification and passes all tests.")
LCB_FMT_STARTER = ("You will use the following starter code to write the solution to the problem and "
                   "enclose your code within delimiters.")
LCB_FMT_STDIN = ("Read the inputs from stdin solve the problem and write the answer to stdout (do not directly "
                 "test on the sample inputs). Enclose your code within delimiters as follows. Ensure that when "
                 "the python program runs, it reads the inputs, runs the algorithm and writes output to STDOUT.")

# Newest release file only (v6 delta, test6.jsonl = problems added in release_v6, 175 rows, official
# count 1055-880).  Metadata streamed by scripts/lcb_metadata_stream.py with LCB_OUT set to this file.
# test5 was not used (its stream had not finished); pinning the list keeps rebuilds byte-identical.
LCB_FILES = [("test6.jsonl", "metadata_test6_no_tests.jsonl", 175)]


def lcb_prompt(r):
    """lcb_runner/prompts/code_generation.py get_generic_question_template_answer (OpenAIChat style)."""
    p = f"### Question:\n{r['question_content']}\n\n"
    if r.get("starter_code"):
        p += f"### Format: {LCB_FMT_STARTER}\n```python\n{r['starter_code']}\n```\n\n"
    else:
        p += f"### Format: {LCB_FMT_STDIN}\n```python\n# YOUR CODE HERE\n```\n\n"
    p += "### Answer: (use the provided format with backticks)\n\n"
    return p


@lru_cache(None)
def load_lcb():
    """Rows from the newest release files whose metadata is complete locally."""
    rows, used = [], []
    for src, fn, expected in LCB_FILES:
        path = os.path.join(RAW, "livecodebench", fn)
        with open(path, encoding="utf-8") as f:
            part = [json.loads(l) for l in f if l.strip()]
        if len(part) != expected:
            raise RuntimeError(f"{fn}: {len(part)} rows, expected {expected} (incomplete stream)")
        for r in part:
            r["_sid"] = r["question_id"]
            r["_file"] = src
        rows.extend(part)
        used.append(src)
    return rows, tuple(used)


def lcb_record(r, **kw):
    base = dict(
        bench_key="livecodebench", benchmark="LiveCodeBench code_generation_lite", source_id=r["_sid"],
        prompt=lcb_prompt(r), system_prompt=LCB_SYSTEM,
        gold_task_type="coding", task_type_label_source="rule_mapping", task_type_confidence="high",
        gold_execution_mode="direct", official_category=r["platform"],
        official_difficulty=r["difficulty"],
        notes=("Benchmark-level rule: code generation scenario -> coding; single-shot generation -> direct. "
               f"From release file {r['_file']}. Prompt rebuilt with the official OpenAIChat template."),
        official_difficulty_field="difficulty", release_file=r["_file"],
        contest_date=r.get("contest_date"), question_title=r.get("question_title"),
        prompt_format="lcb_runner get_generic_question_template_answer + SYSTEM_MESSAGE_GENERIC",
    )
    base.update(kw)
    return record(**base)


# ---------------------------------------------------------------- LongBench v2

# verbatim copy of https://github.com/THUDM/LongBench/blob/main/prompts/0shot.txt (fetched 2026-09-29)
LB_TEMPLATE = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "longbench_v2_0shot.txt"),
                   encoding="utf-8").read()

# research_analysis pool = Multi-Document QA (minus Legal, audited as mixed) + Table QA, minus the
# items below which read as single-document lookup / extraction / pure arithmetic rather than
# research-style synthesis (manual purity filter; several are reused as boundary items).
LB_RA_SUBDOMAINS = {("Multi-Document QA", "Academic"), ("Multi-Document QA", "Financial"),
                    ("Multi-Document QA", "Governmental"), ("Multi-Document QA", "Multi-news"),
                    ("Long Structured Data Understanding", "Table QA")}
LB_EXCLUDE_PREFIX = {
    # Multi-news: single-press-release extraction / single fact / counting
    "66f6b623": "single-fact lookup (cause of death per initial investigation)",
    "66fa6867": "single press release indication lookup",
    "66fd4f54": "single press release indication lookup",
    "66fbe00f": "single press release indication lookup",
    "66fbab85": "which item is noted in all passages (lookup across passages)",
    "66fab4bf": "count products in Phase 3 (extraction/counting)",
    # Governmental / Financial: single-document or lookup or arithmetic
    "66f50109": "lookup/inference of a meeting time",
    "66f6bcf3": "single-document 'not part of plan' lookup",
    "66f4ce9e": "single-act statement check",
    "66f61d7d": "pure percentage computation (math-leaning)",
    "66f3f947": "single annual report statement check",
    "66f26c5f": "single-company fact",
    # Academic: single-paper detail lookups
    "66ed4274": "which step of one paper (lookup)",
    "66f2ad89": "count models in two systems (lookup)",
    "66ee8bab": "single fact (role of glacier mouse)",
    "66f590fa": "single-paper feature lookup",
    "66f120a9": "explain one passage of a single document",
    "66ebee0a": "single-paper formula detail",
    # Table QA: lookups / arithmetic / counting
    "66f2a414": "table lookup",
    "66f659a8": "table lookup",
    "66fa8ccd": "arithmetic word problem over a table (math-leaning)",
    "66f2a46d": "string counting over table rows",
    "66f95e11": "frequency counting",
    "66ec088c": "definition lookup ('What is MAIC?')",
    "66f2abc5": "gene id lookup",
    "66f2a59d": "row filter lookup",
}


@lru_cache(None)
def load_longbench_meta():
    rows = []
    with open(os.path.join(RAW, "longbench_v2", "metadata_no_context.jsonl"), encoding="utf-8") as f:
        for line in f:
            r = json.loads(line)
            r["_sid"] = r["_id"]
            rows.append(r)
    return rows


def lb_excluded(r):
    return any(r["_id"].startswith(p) for p in LB_EXCLUDE_PREFIX)


def longbench_ra_pool():
    return [r for r in load_longbench_meta()
            if (r["domain"], r["sub_domain"]) in LB_RA_SUBDOMAINS and not lb_excluded(r)]


_LB_CTX_CACHE = {}


def longbench_contexts(ids):
    """Return {_id: context} for the requested ids from the local data.json (loaded once)."""
    need = set(ids) - set(_LB_CTX_CACHE)
    if need:
        path = os.path.join(RAW, "longbench_v2", "data.json")
        if os.path.exists(path):
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
            for d in data:
                if d["_id"] in need:
                    _LB_CTX_CACHE[d["_id"]] = d["context"]
            del data
    return {i: _LB_CTX_CACHE.get(i) for i in ids}


def lb_question_block(r):
    return (f"What is the correct answer to this question: {r['question'].strip()}\nChoices:\n"
            f"(A) {r['choice_A'].strip()}\n(B) {r['choice_B'].strip()}\n(C) {r['choice_C'].strip()}\n"
            f"(D) {r['choice_D'].strip()}\n\n"
            "Format your response as follows: \"The correct answer is (insert answer here)\".")


def lb_full_prompt(r, context):
    """Official prompts/0shot.txt filled exactly as LongBench pred.py does."""
    t = LB_TEMPLATE
    return (t.replace('$DOC$', context.strip()).replace('$Q$', r['question'].strip())
            .replace('$C_A$', r['choice_A'].strip()).replace('$C_B$', r['choice_B'].strip())
            .replace('$C_C$', r['choice_C'].strip()).replace('$C_D$', r['choice_D'].strip()))


def longbench_record(r, context, *, gold_task_type="research_analysis", tt_source="rule_mapping",
                     tt_conf="medium", notes=None, **kw):
    extra = {}
    if context is not None:
        full = lb_full_prompt(r, context)
        trunc = len(full) > LB_MAX_CHARS
        half = LB_MAX_CHARS // 2
        extra.update(
            prompt_as_sent=(full[:half] + full[-half:]) if trunc else full,
            prompt_as_sent_truncated=trunc,
            prompt_as_sent_full_chars=len(full),
            prompt_as_sent_truncation=("middle truncation: first 10000 + last 10000 chars of the filled official "
                                       "0shot template (mirrors LongBench pred.py head+tail truncation)") if trunc else None,
            context_available_locally=True,
        )
    else:
        extra.update(prompt_as_sent=None, prompt_as_sent_truncated=None, prompt_as_sent_full_chars=None,
                     prompt_as_sent_truncation=None, context_available_locally=False)
    base = dict(
        bench_key="longbench_v2", benchmark="LongBench v2", source_id=r["_sid"], prompt=lb_question_block(r),
        gold_task_type=gold_task_type, task_type_label_source=tt_source, task_type_confidence=tt_conf,
        gold_execution_mode="direct", official_category=f"{r['domain']}/{r['sub_domain']}",
        official_difficulty=r["difficulty"],
        notes=notes if notes is not None else (
            "Subdomain rule: LongBench v2 Multi-Document QA (Academic/Financial/Governmental/Multi-news) or Table QA "
            "-> research_analysis, after a manual purity filter that removed lookup/extraction/arithmetic items; "
            "single request with pasted context -> direct. prompt = question+choices only; see prompt_as_sent / context_ref."),
        official_difficulty_field="difficulty", length=r["length"],
        context_ref={"hf_dataset": "zai-org/LongBench-v2 (formerly THUDM/LongBench-v2)", "file": "data.json",
                     "_id": r["_id"], "field": "context", "local_path": "raw/longbench_v2/data.json",
                     "context_chars": r.get("ctx_chars")},
        production_state_note=("autoroute.build_state clips first_user_message to 1500 chars and "
                               "current_user_message to 4000 chars (head only), so production Jev sees only the "
                               "instruction line and the start of the context, not the question."),
        prompt_format="prompt = question+choices part of official 0shot.txt; prompt_as_sent = full template",
    )
    base.update(extra)
    base.update(kw)
    return record(**base)


# ---------------------------------------------------------------- PlanningBench


@lru_cache(None)
def load_planningbench():
    rows = []
    with open(os.path.join(RAW, "planningbench", "PlanningBench-eval.jsonl"), encoding="utf-8") as f:
        for line in f:
            r = json.loads(line)
            r["_sid"] = int(r["idx"])
            rows.append(r)
    return rows


def planningbench_record(r, **kw):
    base = dict(
        bench_key="planningbench", benchmark="PlanningBench (tencent)", source_id=r["_sid"],
        prompt=r["messages"][0]["content"], gold_task_type="planning_design",
        task_type_label_source="rule_mapping", task_type_confidence="high",
        gold_execution_mode="direct", official_category=None, official_difficulty=None,
        notes=("Benchmark-level rule: constraint-driven planning benchmark -> planning_design; self-contained "
               "single user turn -> direct. Release has no per-item category/difficulty field. All prompts Chinese."),
        lang="zh", prompt_format="messages[0].content as-is (single user turn, no system prompt)",
    )
    base.update(kw)
    return record(**base)


# ---------------------------------------------------------------- NATURAL PLAN


@lru_cache(None)
def load_natural_plan(task):
    with open(os.path.join(RAW, "natural_plan", f"{task}.json"), encoding="utf-8") as f:
        return json.load(f)


# ---------------------------------------------------------------- AutomationBench

AB_PUBLIC = ["sales", "marketing", "operations", "support", "finance", "hr"]


@lru_cache(None)
def load_automationbench():
    rows = []
    with open(os.path.join(RAW, "automationbench", "first_requests_api.jsonl"), encoding="utf-8") as f:
        for line in f:
            r = json.loads(line)
            r["_sid"] = f"{r['domain']}:{r['example_id']}"
            rows.append(r)
    return rows


def ab_record(r, *, gold_task_type="workflow_operation", tt_source="rule_mapping", tt_conf="high",
              notes=None, **kw):
    msgs = r["messages"]
    sys_msg = next(m["content"] for m in msgs if m["role"] == "system")
    user = next(m["content"] for m in msgs if m["role"] == "user")
    base = dict(
        bench_key="automationbench", benchmark="AutomationBench", source_id=r["_sid"], prompt=user,
        system_prompt=sys_msg, tools=list(r["tools"]),
        gold_task_type=gold_task_type, task_type_label_source=tt_source, task_type_confidence=tt_conf,
        gold_execution_mode="agentic", official_category=r["domain"], official_difficulty=None,
        notes=notes if notes is not None else (
            "Benchmark-level rule: business workflow graded on final SaaS world state -> workflow_operation; "
            "multi-turn tool use -> agentic. First request = official CLI default toolset 'api'."),
        toolset="api", zapier_tools_listed=list(r.get("zapier_tools_listed") or []),
        example_id=r["example_id"],
        prompt_format="user message of the reconstructed first request (raw/automationbench/first_requests_api.jsonl)",
    )
    base.update(kw)
    return record(**base)


# ---------------------------------------------------------------- agentic first requests (mini-swe-agent)


@lru_cache(None)
def load_first_requests(src):
    rows = []
    with open(os.path.join(RAW, "agentic_first_requests", f"{src}_miniswe_first_requests.jsonl"), encoding="utf-8") as f:
        for line in f:
            r = json.loads(line)
            r["_sid"] = r["task_id"]
            rows.append(r)
    return rows


@lru_cache(None)
def task_meta(src, task_id):
    root = {"deepswe": DEEPSWE_ROOT, "tb4": TB4_ROOT, "tb2": TB2_ROOT}[src]
    with open(os.path.join(root, task_id, "task.toml"), "rb") as f:
        return tomllib.load(f).get("metadata", {})


def tool_names(tools):
    return [t["function"]["name"] if isinstance(t, dict) and "function" in t else t for t in tools]


# TB tasks: task_type filled only when obvious (software/debugging categories -> coding), always
# human_review_required.  prove-plus-comm is a Coq proof, not obviously coding -> null.
TB_TT_NULL_OVERRIDE = {("tb2", "prove-plus-comm")}


def tb_task_type(src, task_id, meta):
    cat = meta.get("category")
    if (src, task_id) in TB_TT_NULL_OVERRIDE:
        return None
    if src == "tb2" and cat in ("software-engineering", "debugging"):
        return "coding"
    if src == "tb4" and cat == "Software":
        return "coding"
    return None


def agentic_record(src, r, *, gold_task_type="__auto__", tt_source=None, tt_conf=None, notes=None, **kw):
    meta = task_meta(src, r["task_id"])
    msgs = r["messages"]
    sys_msg = next(m["content"] for m in msgs if m["role"] == "system")
    user = next(m["content"] for m in msgs if m["role"] == "user")
    if src == "deepswe":
        bench_key, bench = "deepswe", "DeepSWE"
        tt = "coding" if gold_task_type == "__auto__" else gold_task_type
        tts, ttc = tt_source or "rule_mapping", tt_conf or "high"
        oc, od, dfield = meta.get("category"), None, None
        n = notes or ("Benchmark-level rule: repository feature/bugfix SWE tasks -> coding; sandboxed agent "
                      "(mini-swe-agent via Pier) -> agentic.")
        extra = {"language": meta.get("language"), "repository_url": meta.get("repository_url")}
    else:
        bench_key = {"tb4": "terminal_bench_4", "tb2": "terminal_bench_2"}[src]
        bench = {"tb4": "Terminal-Bench 4.0", "tb2": "Terminal-Bench 2.0"}[src]
        tt = tb_task_type(src, r["task_id"], meta) if gold_task_type == "__auto__" else gold_task_type
        tts = tt_source or "human_review_required"
        ttc = tt_conf or ("medium" if tt else "low")
        if src == "tb4":
            oc = f"{meta.get('category')}/{meta.get('subcategory')}"
            od, dfield = None, None
            extra = {"expert_time_estimate_hours": meta.get("expert_time_estimate_hours")}
        else:
            oc = meta.get("category")
            od, dfield = meta.get("difficulty"), "difficulty"
            extra = {"tags": list(meta.get("tags") or []),
                     "expert_time_estimate_min": meta.get("expert_time_estimate_min"),
                     "junior_time_estimate_min": meta.get("junior_time_estimate_min")}
        n = notes or ("Terminal task in a sandbox -> agentic (rule_mapping). task_type "
                      + ("recommended 'coding' from the software/debugging category; needs human review."
                         if tt else "left null: not obvious from benchmark structure; needs human review."))
    base = dict(
        bench_key=bench_key, benchmark=bench, source_id=r["task_id"], prompt=user, system_prompt=sys_msg,
        tools=tool_names(r["tools"]), gold_task_type=tt, task_type_label_source=tts, task_type_confidence=ttc,
        gold_execution_mode="agentic", official_category=oc, official_difficulty=od, notes=n,
        official_difficulty_field=dfield,
        agent_harness="mini-swe-agent mini.yaml (tool-calling, single bash tool); uname placeholders in prompt",
        prompt_format=f"user message of raw/agentic_first_requests/{src}_miniswe_first_requests.jsonl",
    )
    base.update(extra)
    base.update(kw)
    return record(**base)


def by_sid(rows):
    return {str(r["_sid"]): r for r in rows}
