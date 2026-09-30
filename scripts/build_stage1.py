"""Build STAGE1_CLASSIFICATION_SET.jsonl (Jev Auto Router experiment, Stage 1).

Provisional taxonomy (6 task_type): general_qa, writing_language, math, reasoning_planning, coding,
research_analysis.  execution_mode: direct / agentic.

  set=clean (180, all direct): 30 per task_type.
  set=mode  (50, agentic):     DeepSWE 20 (coding) + AutomationBench 30 (item-judged task_type).

No model, Jev API or remote host is called.  Every random choice uses a fresh
random.Random(20260929) (jev_common.rng) over a sorted pool, rows are written sorted by id, so a
re-run is byte-identical.  Difficulty is only copied from official benchmark fields.

Run: /root/bench/hle-venv/bin/python scripts/build_stage1.py [--out PATH]
"""
from __future__ import annotations

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import jev_common as C  # noqa: E402
from stage1_ab_judgements import AB_JUDGEMENTS  # noqa: E402

SEED = 20260929
assert C.SEED == SEED
OUT_NAME = "STAGE1_CLASSIFICATION_SET.jsonl"

TASK_TYPES = ["general_qa", "writing_language", "math", "reasoning_planning", "coding",
              "research_analysis"]
EXEC_MODES = ["direct", "agentic"]
FITS = ["clean", "ambiguous", "uncovered"]
LABEL_SOURCES = ["benchmark_native", "rule_mapping", "item_judgement"]
SETS = ["clean", "mode"]
FIELDS = ["id", "benchmark", "task_id", "benchmark_subtype", "prompt", "system_prompt", "tools",
          "expected_task_type", "expected_execution_mode", "official_difficulty",
          "official_difficulty_raw", "taxonomy_fit", "taxonomy_gap", "taxonomy_gap_reason",
          "label_source", "set", "notes"]

# Quotas (documented in STAGE1_BENCHMARK_AUDIT.md)
MATH500_PER_LEVEL = 4                      # 5 levels x 4 = 20
LB_MATH_QUOTA = {"AMPS_Hard": 4, "math_comp": 3, "olympiad": 3}   # 10
LB_REASONING_QUOTA = {"zebra_puzzle": 5, "web_of_lies_v2": 5, "spatial": 5}   # 15
PLANNINGBENCH_N = 15
LCB_FILE = "test6.jsonl"                   # newest release delta (release_v6), 175 rows
LCB_PER_CELL = 5                           # 3 difficulty x 2 platform x 5 = 30
LB_PER_SUBDOMAIN = 6                       # 5 sub_domains x 6 = 30
DEEPSWE_N = 20
AB_PUBLIC_PER_DOMAIN = 4                   # 6 x 4 = 24
AB_SIMPLE_N = 6

# Stage-1 re-check of the LongBench v2 research_analysis pool.  The v1 exclusions
# (jev_common.LB_EXCLUDE_PREFIX) are kept; items below were additionally excluded after reading
# the question + choices during the Stage-1 re-check (reason given for each).
LB_STAGE1_EXTRA_EXCLUDE = {
    "66f41108": "Financial: single percentage-point difference between two reports (simple arithmetic lookup)",
    "6701cda0": "Multi-news: extraction of two stated reasons from news articles (simple extraction)",
    "66f7f382": "Table QA: argmax of one-minute price change over a price series (simple computation/lookup)",
    "66fc0152": "Multi-news: count which listed products treat neurological disease (extraction/counting)",
}


def row(**kw):
    r = {k: kw.pop(k) for k in FIELDS}
    if kw:
        raise KeyError(f"unexpected fields {sorted(kw)}")
    return r


def mid(bench_key, task_id):
    return f"{bench_key}:{task_id}"


# ------------------------------------------------------------------ clean set (direct)


def general_qa():
    pool = C.simpleqa_pool()          # requires_reasoning=False only
    topics = sorted({r["topic"] for r in pool})
    picks = C.sample_quota(pool, {t: 3 for t in topics}, lambda r: r["topic"], lambda r: r["answer_type"])
    out = []
    for r in picks:
        out.append(row(
            id=mid("simpleqa_verified", r["_sid"]), benchmark="SimpleQA Verified",
            task_id=str(r["_sid"]), benchmark_subtype=f"topic={r['topic']}|answer_type={r['answer_type']}",
            prompt=r["problem"], system_prompt=None, tools=None,
            expected_task_type="general_qa", expected_execution_mode="direct",
            official_difficulty=None,
            official_difficulty_raw={"multi_step": bool(r["multi_step"]),
                                     "requires_reasoning": bool(r["requires_reasoning"])},
            taxonomy_fit="clean", taxonomy_gap=False, taxonomy_gap_reason=None,
            label_source="rule_mapping", set="clean",
            notes=("task_id = original_index. Benchmark rule: short-form factual QA -> general_qa; no tools -> direct. "
                   "No difficulty field; multi_step/requires_reasoning are official metadata flags kept verbatim "
                   "(not a difficulty scale). Pool: requires_reasoning=False. Sampled 3 per topic, round-robin "
                   "over answer_type.")))
    return out


def writing():
    pool = C.writingbench_pool()
    picks = C.sample_round_robin(pool, 30, lambda r: r["domain2"])
    out = []
    for r in picks:
        out.append(row(
            id=mid("writingbench", r["_sid"]), benchmark="WritingBench", task_id=str(r["_sid"]),
            benchmark_subtype=f"{r['domain1']}/{r['domain2']}", prompt=r["query"], system_prompt=None, tools=None,
            expected_task_type="writing_language", expected_execution_mode="direct",
            official_difficulty=None, official_difficulty_raw=None,
            taxonomy_fit="clean", taxonomy_gap=False, taxonomy_gap_reason=None,
            label_source="rule_mapping", set="clean",
            notes=(f"task_id = index. lang={r['lang']}, query_chars={len(r['query'])}. Subdomain rule: domain2 in the "
                   "audited pure-writing list (copywriting/creative/academic section/official & correspondence/"
                   "summary); analysis/report/planning subdomains excluded, plus heuristic-flagged analysis "
                   "candidates and >5K-char analyze/evaluate queries. WritingBench has no difficulty field.")))
    return out


def math():
    m5 = C.sample_quota(C.load_math500(), {lv: MATH500_PER_LEVEL for lv in (1, 2, 3, 4, 5)},
                        lambda r: r["level"], lambda r: r["subject"])
    lbm_pool = [r for r in C.load_livebench("math")]
    lbm = C.sample_quota(lbm_pool, LB_MATH_QUOTA, lambda r: r["task"], lambda r: r["subtask"])
    out = []
    for r in m5:
        out.append(row(
            id=mid("math500", r["_sid"]), benchmark="MATH-500", task_id=r["_sid"],
            benchmark_subtype=r["subject"], prompt=r["problem"], system_prompt=None, tools=None,
            expected_task_type="math", expected_execution_mode="direct",
            official_difficulty=f"level_{r['level']}", official_difficulty_raw={"level": r["level"]},
            taxonomy_fit="clean", taxonomy_gap=False, taxonomy_gap_reason=None,
            label_source="rule_mapping", set="clean",
            notes=("task_id = unique_id. Benchmark rule: MATH competition problem -> math; direct. "
                   "official_difficulty from native field `level` (1-5). Prompt = bare problem (no single "
                   "official chat template). Sampled 4 per level, round-robin over subject.")))
    for r in lbm:
        hard = r.get("hardness")
        has_h = hard is not None and not (isinstance(hard, float) and hard != hard)
        out.append(row(
            id=mid("livebench_math", r["_sid"]), benchmark="LiveBench math", task_id=r["_sid"],
            benchmark_subtype=f"{r['task']}/{r['subtask']}", prompt=r["turns"][0], system_prompt=None, tools=None,
            expected_task_type="math", expected_execution_mode="direct",
            official_difficulty=None,
            official_difficulty_raw=({"hardness": float(hard)} if has_h else None),
            taxonomy_fit="clean", taxonomy_gap=False, taxonomy_gap_reason=None,
            label_source="benchmark_native", set="clean",
            notes=("task_id = question_id. Native category='math' -> math; single turn -> direct. "
                   f"release={r['livebench_release_date']}, removal={r['livebench_removal_date'] or 'none'}. "
                   + ("`hardness` is an HF schema field present only on olympiad rows; its scale is not documented "
                      "by LiveBench and unused by its scorer, so it is kept raw and not normalized. "
                      if has_h else "No difficulty field for this task. ")
                   + "Sampled per task (AMPS_Hard 4 / math_comp 3 / olympiad 3), round-robin over subtask.")))
    return out


def reasoning_planning():
    lbr = C.sample_quota(C.load_livebench("reasoning"), LB_REASONING_QUOTA, lambda r: r["task"],
                         lambda r: str(r["livebench_release_date"]))
    out = []
    for r in lbr:
        lv = r.get("level")
        has_l = lv is not None and not (isinstance(lv, float) and lv != lv)
        out.append(row(
            id=mid("livebench_reasoning", r["_sid"]), benchmark="LiveBench reasoning", task_id=r["_sid"],
            benchmark_subtype="reasoning", prompt=r["turns"][0], system_prompt=None, tools=None,
            expected_task_type="reasoning_planning", expected_execution_mode="direct",
            official_difficulty=None, official_difficulty_raw=({"level": int(lv)} if has_l else None),
            taxonomy_fit="clean", taxonomy_gap=False, taxonomy_gap_reason=None,
            label_source="benchmark_native", set="clean",
            notes=(f"task family = {r['task']}. task_id = question_id. Native category='reasoning' -> "
                   "reasoning_planning (subtype reasoning); direct. "
                   f"release={r['livebench_release_date']}, removal={r['livebench_removal_date'] or 'none'}. "
                   + ("`level` (zebra only) is an HF schema field whose scale is not documented by LiveBench; kept raw. "
                      if has_l else "")
                   + "5 per family (zebra_puzzle / web_of_lies_v2 / spatial), round-robin over release date.")))
    pool = sorted(C.load_planningbench(), key=lambda r: r["_sid"])
    for r in C.rng().sample(pool, PLANNINGBENCH_N):
        out.append(row(
            id=mid("planningbench", r["_sid"]), benchmark="PlanningBench (tencent)", task_id=str(r["_sid"]),
            benchmark_subtype="planning", prompt=r["messages"][0]["content"], system_prompt=None, tools=None,
            expected_task_type="reasoning_planning", expected_execution_mode="direct",
            official_difficulty=None, official_difficulty_raw=None,
            taxonomy_fit="clean", taxonomy_gap=False, taxonomy_gap_reason=None,
            label_source="rule_mapping", set="clean",
            notes=("task_id = idx. Benchmark rule: constraint-driven text planning -> reasoning_planning (subtype "
                   "planning); self-contained single user turn -> direct. Release has no category/difficulty "
                   "field. Chinese prompt. Seeded sample(15).")))
    return out


def coding():
    rows, used = C.load_lcb()
    assert used == (LCB_FILE,), used
    pool = [r for r in rows if r["_file"] == LCB_FILE]
    for r in pool:
        r["_cell"] = f"{r['difficulty']}|{r['platform']}"
    cells = sorted({r["_cell"] for r in pool})
    picks = C.sample_quota(pool, {c: LCB_PER_CELL for c in cells}, lambda r: r["_cell"],
                           lambda r: r["contest_date"][:7])
    out = []
    for r in picks:
        out.append(row(
            id=mid("livecodebench", r["_sid"]), benchmark="LiveCodeBench code_generation_lite",
            task_id=r["_sid"], benchmark_subtype=r["platform"], prompt=C.lcb_prompt(r),
            system_prompt=C.LCB_SYSTEM, tools=None,
            expected_task_type="coding", expected_execution_mode="direct",
            official_difficulty=r["difficulty"], official_difficulty_raw={"difficulty": r["difficulty"]},
            taxonomy_fit="clean", taxonomy_gap=False, taxonomy_gap_reason=None,
            label_source="rule_mapping", set="clean",
            notes=(f"task_id = question_id. Release file {LCB_FILE} (release_v6 delta, newest). "
                   f"contest_date={r['contest_date']}, title={r['question_title']!r}. Benchmark rule: code generation "
                   "-> coding; single-shot -> direct. Prompt/system rebuilt with lcb_runner OpenAIChat template "
                   "(GitHub main). Sampled 5 per difficulty x platform, round-robin over contest month.")))
    return out


def lb_pool():
    return [r for r in C.longbench_ra_pool()
            if not any(r["_id"].startswith(p) for p in LB_STAGE1_EXTRA_EXCLUDE)]


def research():
    pool = lb_pool()
    subs = sorted({r["sub_domain"] for r in pool})
    picks = C.sample_quota(pool, {s: LB_PER_SUBDOMAIN for s in subs}, lambda r: r["sub_domain"],
                           lambda r: f"{r['difficulty']}|{r['length']}")
    ctx = C.longbench_contexts([r["_id"] for r in picks])
    out = []
    for r in picks:
        c = ctx[r["_id"]]
        if c is None:
            raise RuntimeError(f"LongBench context missing for {r['_id']}")
        out.append(row(
            id=mid("longbench_v2", r["_sid"]), benchmark="LongBench v2", task_id=r["_sid"],
            benchmark_subtype=r["sub_domain"], prompt=C.lb_full_prompt(r, c), system_prompt=None, tools=None,
            expected_task_type="research_analysis", expected_execution_mode="direct",
            official_difficulty=r["difficulty"],
            official_difficulty_raw={"difficulty": r["difficulty"], "length": r["length"]},
            taxonomy_fit="clean", taxonomy_gap=False, taxonomy_gap_reason=None,
            label_source="rule_mapping", set="clean",
            notes=(f"task_id = _id. domain={r['domain']}. Rule: Multi-Document QA (Academic/Financial/Governmental/"
                   "Multi-news) or Table QA -> research_analysis after the manual purity filter (lookup/extraction/"
                   "arithmetic removed; Legal and KG reasoning excluded); question re-checked in Stage 1. "
                   "prompt = official prompts/0shot.txt filled with the full context, NOT truncated (pred.py "
                   "head+tail-truncates to the model's max_len in tokens, e.g. 120000 for gpt-4o; that is "
                   f"model-specific). prompt_chars={len(C.lb_full_prompt(r, c))}. official_difficulty = native "
                   "`difficulty`; `length` kept in raw. Sampled 6 per sub_domain, round-robin over difficulty x length.")))
    return out


# ------------------------------------------------------------------ mode set (agentic)

MSWE_NOTE = ("First request reconstructed for mini-swe-agent mini.yaml via Pier (system + instance_template, single "
             "`bash` tool); uname fields in <system_information> are placeholders; the DeepSWE leaderboard's exact "
             "mini-swe-agent version/limits are undocumented.")


def deepswe():
    reqs = C.load_first_requests("deepswe")
    for r in reqs:
        r["_lang"] = C.task_meta("deepswe", r["task_id"]).get("language")
    picks = C.sample_round_robin(reqs, DEEPSWE_N, lambda r: r["_lang"])
    out = []
    for r in picks:
        meta = C.task_meta("deepswe", r["task_id"])
        msgs = r["messages"]
        out.append(row(
            id=mid("deepswe", r["task_id"]), benchmark="DeepSWE", task_id=r["task_id"],
            benchmark_subtype=f"{meta.get('language')}/{meta.get('category')}",
            prompt=next(m["content"] for m in msgs if m["role"] == "user"),
            system_prompt=next(m["content"] for m in msgs if m["role"] == "system"),
            tools=C.tool_names(r["tools"]),
            expected_task_type="coding", expected_execution_mode="agentic",
            official_difficulty=None, official_difficulty_raw=None,
            taxonomy_fit="clean", taxonomy_gap=False, taxonomy_gap_reason=None,
            label_source="rule_mapping", set="mode",
            notes=(f"Official task {meta.get('task_id')} ({meta.get('repository_url')}); instruction.md + task.toml "
                   "metadata only. Rule: repo feature/bugfix work in a sandbox -> coding + agentic. No difficulty "
                   "field. " + MSWE_NOTE + " Sampled round-robin over language.")))
    return out


AB_NOTE = ("First request = AutomationBench CLI default toolset `api` (api_search, api_fetch, base64_encode) with the "
           "shared runner SYSTEM_PROMPT; the initial world state is not in the prompt (agent must discover it). "
           "Reconstructed locally from v1.0.6 code without running a model.")


def automationbench():
    meta = {}
    with open(os.path.join(C.RAW, "automationbench", "task_meta.jsonl"), encoding="utf-8") as f:
        for line in f:
            m = json.loads(line)
            meta[f"{m['domain']}:{m['example_id']}"] = m
    rows = C.load_automationbench()
    pub = C.sample_quota([r for r in rows if r["domain"] in C.AB_PUBLIC],
                         {d: AB_PUBLIC_PER_DOMAIN for d in C.AB_PUBLIC}, lambda r: r["domain"])
    simple = C.sample_round_robin([r for r in rows if r["domain"] == "simple"], AB_SIMPLE_N,
                                  lambda r: meta[r["_sid"]]["task_name"].split(".")[1].split("_")[0])
    out = []
    for r in pub + simple:
        sid = r["_sid"]
        j = AB_JUDGEMENTS.get(sid)
        if j is None:
            raise KeyError(f"no item judgement for AutomationBench {sid} ({meta[sid]['task_name']})")
        msgs = r["messages"]
        out.append(row(
            id=mid("automationbench", sid), benchmark="AutomationBench", task_id=sid,
            benchmark_subtype=r["domain"],
            prompt=next(m["content"] for m in msgs if m["role"] == "user"),
            system_prompt=next(m["content"] for m in msgs if m["role"] == "system"),
            tools=list(r["tools"]),
            expected_task_type=j["task_type"], expected_execution_mode="agentic",
            official_difficulty=None,
            official_difficulty_raw=({"domain": "simple"} if r["domain"] == "simple" else None),
            taxonomy_fit=j["fit"], taxonomy_gap=j["gap"], taxonomy_gap_reason=j["reason"],
            label_source="item_judgement", set="mode",
            notes=(f"task_name={meta[sid]['task_name']}; task_id = <domain>:<example_id>. "
                   f"Final-state assertions ({meta[sid]['n_assertions']}): "
                   f"{', '.join(sorted(set(meta[sid]['assertion_types'])))}. "
                   + ("domain 'simple' = README 'foundational single- and two-step tasks', excluded from the official "
                      "score; not a per-item difficulty label. " if r["domain"] == "simple" else "")
                   + AB_NOTE + " Judgement: " + j["why"])))
    return out


def build():
    clean = general_qa() + writing() + math() + reasoning_planning() + coding() + research()
    mode = deepswe() + automationbench()
    return clean + mode


def write(path, recs):
    recs = sorted(recs, key=lambda r: r["id"])
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        for r in recs:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(C.REPO, OUT_NAME))
    a = ap.parse_args(argv)
    recs = build()
    write(a.out, recs)
    print(a.out, len(recs))


if __name__ == "__main__":
    main(sys.argv[1:])
