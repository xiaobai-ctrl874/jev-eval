"""Validate STAGE1_CLASSIFICATION_SET.jsonl.

Checks: exact field list; allowed values; label/fit/gap consistency; unique ids and id format;
every task_id traceable to the local raw data with prompt / system_prompt / tools equal to the
raw item (reconstructed the same way as the builder); per-set / per-class / per-source counts and
strata; official_difficulty only from the official field; AutomationBench judgements complete;
HF token absent; and a rebuild into a temp file must be byte-identical (sha256).
Exit code 1 on any failure.

Run: /root/bench/hle-venv/bin/python scripts/validate_stage1.py [--skip-rebuild]
"""
import collections
import hashlib
import json
import os
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_stage1 as B  # noqa: E402
import jev_common as C  # noqa: E402

PATH = os.path.join(C.REPO, B.OUT_NAME)
FAIL = []


def check(cond, msg):
    if not cond:
        FAIL.append(msg)


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def user_sys(msgs):
    return (next(m["content"] for m in msgs if m["role"] == "user"),
            next(m["content"] for m in msgs if m["role"] == "system"))


def raw_index():
    """bench_key -> {task_id: fn(row) -> (ok, extra-check-dict)}"""
    idx = {}
    idx["simpleqa_verified"] = {str(r["_sid"]): r for r in C.load_simpleqa()}
    idx["writingbench"] = {str(r["_sid"]): r for r in C.load_writingbench()}
    idx["math500"] = {r["_sid"]: r for r in C.load_math500()}
    idx["livebench_math"] = {r["_sid"]: r for r in C.load_livebench("math")}
    idx["livebench_reasoning"] = {r["_sid"]: r for r in C.load_livebench("reasoning")}
    idx["planningbench"] = {str(r["_sid"]): r for r in C.load_planningbench()}
    idx["livecodebench"] = {r["_sid"]: r for r in C.load_lcb()[0]}
    idx["longbench_v2"] = {r["_sid"]: r for r in C.load_longbench_meta()}
    idx["deepswe"] = {r["_sid"]: r for r in C.load_first_requests("deepswe")}
    idx["automationbench"] = {r["_sid"]: r for r in C.load_automationbench()}
    return idx


def trace(rec, raw):
    """Prompt / system / tools / difficulty must equal what the raw item gives."""
    b = rec["id"].split(":", 1)[0]
    p, s, t = rec["prompt"], rec["system_prompt"], rec["tools"]
    if b == "simpleqa_verified":
        return p == raw["problem"] and s is None and t is None
    if b == "writingbench":
        return p == raw["query"] and s is None and t is None and raw["domain2"] in C.WB_CLEAN
    if b == "math500":
        return (p == raw["problem"] and s is None and t is None
                and rec["official_difficulty"] == f"level_{raw['level']}"
                and rec["official_difficulty_raw"] == {"level": raw["level"]})
    if b in ("livebench_math", "livebench_reasoning"):
        cat = b.split("_")[1]
        return p == raw["turns"][0] and raw["category"] == cat and s is None and t is None \
            and rec["official_difficulty"] is None
    if b == "planningbench":
        return p == raw["messages"][0]["content"] and len(raw["messages"]) == 1 and s is None and t is None
    if b == "livecodebench":
        return (p == C.lcb_prompt(raw) and raw["question_content"] in p and s == C.LCB_SYSTEM and t is None
                and raw["_file"] == B.LCB_FILE and rec["official_difficulty"] == raw["difficulty"]
                and rec["official_difficulty_raw"] == {"difficulty": raw["difficulty"]})
    if b == "longbench_v2":
        return (p.startswith("Please read the following text and answer the question below.")
                and raw["question"].strip() in p and s is None and t is None
                and rec["official_difficulty"] == raw["difficulty"]
                and rec["official_difficulty_raw"] == {"difficulty": raw["difficulty"], "length": raw["length"]})
    if b == "deepswe":
        u, sy = user_sys(raw["messages"])
        return p == u and s == sy and t == C.tool_names(raw["tools"]) == ["bash"]
    if b == "automationbench":
        u, sy = user_sys(raw["messages"])
        return p == u and s == sy and t == list(raw["tools"]) == ["api_search", "api_fetch", "base64_encode"]
    return False


def main():
    skip_rebuild = "--skip-rebuild" in sys.argv
    with open(PATH, encoding="utf-8") as f:
        text = f.read()
    recs = [json.loads(l) for l in text.splitlines()]
    print(f"{B.OUT_NAME}: {len(recs)} rows, sha256 {sha(PATH)[:16]}")

    # fields / values
    for r in recs:
        rid = r.get("id")
        check(list(r.keys()) == B.FIELDS, f"{rid}: field list/order {list(r.keys())}")
        check(r["expected_task_type"] in B.TASK_TYPES or r["expected_task_type"] is None, f"{rid}: task_type")
        check(r["expected_execution_mode"] in B.EXEC_MODES, f"{rid}: execution_mode")
        check(r["taxonomy_fit"] in B.FITS, f"{rid}: taxonomy_fit")
        check(isinstance(r["taxonomy_gap"], bool), f"{rid}: taxonomy_gap not bool")
        check(r["label_source"] in B.LABEL_SOURCES, f"{rid}: label_source")
        check(r["set"] in B.SETS, f"{rid}: set")
        check(isinstance(r["prompt"], str) and r["prompt"].strip(), f"{rid}: empty prompt")
        check(r["tools"] is None or (isinstance(r["tools"], list) and all(isinstance(x, str) for x in r["tools"])),
              f"{rid}: tools must be null or list of names")
        check(isinstance(r["notes"], str) and r["notes"], f"{rid}: notes")
        check(r["official_difficulty_raw"] is None or isinstance(r["official_difficulty_raw"], dict),
              f"{rid}: official_difficulty_raw type")
        check(r["official_difficulty"] is None or r["official_difficulty_raw"] is not None,
              f"{rid}: normalized difficulty without raw field")
        # fit / gap consistency
        fit, gap, reason = r["taxonomy_fit"], r["taxonomy_gap"], r["taxonomy_gap_reason"]
        if fit == "clean":
            check(not gap and reason is None and r["expected_task_type"] is not None, f"{rid}: clean inconsistent")
        if fit == "ambiguous":
            check(gap and reason and r["expected_task_type"] is not None, f"{rid}: ambiguous inconsistent")
        if fit == "uncovered":
            check(gap and reason and r["expected_task_type"] is None, f"{rid}: uncovered inconsistent")
        if r["expected_task_type"] is None:
            check(fit == "uncovered", f"{rid}: null task_type must be uncovered")
        check(r["id"] == f"{r['id'].split(':', 1)[0]}:{r['task_id']}", f"{rid}: id != bench_key:task_id")

    ids = [r["id"] for r in recs]
    check(len(ids) == len(set(ids)), "duplicate ids")
    check(ids == sorted(ids), "rows not sorted by id")

    # traceability
    idx = raw_index()
    for r in recs:
        b = r["id"].split(":", 1)[0]
        raw = idx.get(b, {}).get(r["task_id"])
        check(raw is not None, f"{r['id']}: task_id not found in raw data for {b}")
        if raw is not None:
            check(trace(r, raw), f"{r['id']}: prompt/system/tools/difficulty do not trace to raw item")

    # counts
    by = collections.defaultdict(list)
    for r in recs:
        by[r["id"].split(":", 1)[0]].append(r)
    clean = [r for r in recs if r["set"] == "clean"]
    mode = [r for r in recs if r["set"] == "mode"]
    check(len(clean) == 180 and all(r["expected_execution_mode"] == "direct" for r in clean), "clean set: 180 direct")
    ct = collections.Counter(r["expected_task_type"] for r in clean)
    check(all(ct[t] == 30 for t in B.TASK_TYPES), f"clean per class {ct}")
    check(all(r["taxonomy_fit"] == "clean" for r in clean), "clean set rows must be taxonomy_fit=clean")
    check(len(mode) == 50 and all(r["expected_execution_mode"] == "agentic" for r in mode), "mode set: 50 agentic")
    exp = {"simpleqa_verified": 30, "writingbench": 30, "math500": 20, "livebench_math": 10,
           "livebench_reasoning": 15, "planningbench": 15, "livecodebench": 30, "longbench_v2": 30,
           "deepswe": 20, "automationbench": 30}
    for k, n in exp.items():
        check(len(by[k]) == n, f"{k}: {len(by[k])} != {n}")
    check(set(by) == set(exp), f"unexpected benchmarks {set(by) - set(exp)}")
    # strata
    check(all(v == 3 for v in collections.Counter(idx["simpleqa_verified"][r["task_id"]]["topic"]
                                                  for r in by["simpleqa_verified"]).values()), "SimpleQA 3/topic")
    check(not any(idx["simpleqa_verified"][r["task_id"]]["requires_reasoning"] for r in by["simpleqa_verified"]),
          "SimpleQA requires_reasoning item present")
    check(len({idx["writingbench"][r["task_id"]]["domain2"] for r in by["writingbench"]}) == 30,
          "WritingBench: 30 distinct domain2")
    check(collections.Counter(r["official_difficulty"] for r in by["math500"]) ==
          {f"level_{i}": 4 for i in range(1, 6)}, "MATH-500 4/level")
    check(collections.Counter(idx["livebench_math"][r["task_id"]]["task"] for r in by["livebench_math"]) ==
          B.LB_MATH_QUOTA, "LiveBench math quota")
    check(collections.Counter(idx["livebench_reasoning"][r["task_id"]]["task"] for r in by["livebench_reasoning"]) ==
          B.LB_REASONING_QUOTA, "LiveBench reasoning 5/family")
    check(all(r["benchmark_subtype"] == "reasoning" for r in by["livebench_reasoning"]), "reasoning subtype")
    check(all(r["benchmark_subtype"] == "planning" for r in by["planningbench"]), "planning subtype")
    cells = collections.Counter((idx["livecodebench"][r["task_id"]]["difficulty"],
                                 idx["livecodebench"][r["task_id"]]["platform"]) for r in by["livecodebench"])
    check(len(cells) == 6 and set(cells.values()) == {5}, f"LCB cells {cells}")
    lbm = [idx["longbench_v2"][r["task_id"]] for r in by["longbench_v2"]]
    check(all((m["domain"], m["sub_domain"]) in C.LB_RA_SUBDOMAINS for m in lbm), "LongBench sub_domain outside pool")
    check(not any(C.lb_excluded(m) or any(m["_id"].startswith(p) for p in B.LB_STAGE1_EXTRA_EXCLUDE) for m in lbm),
          "LongBench excluded item present")
    check(set(collections.Counter(m["sub_domain"] for m in lbm).values()) == {6}, "LongBench 6/sub_domain")
    for p in list(C.LB_EXCLUDE_PREFIX) + list(B.LB_STAGE1_EXTRA_EXCLUDE):
        hits = [m for m in C.load_longbench_meta() if m["_id"].startswith(p)]
        check(len(hits) == 1 and (hits[0]["domain"], hits[0]["sub_domain"]) in C.LB_RA_SUBDOMAINS,
              f"LongBench exclusion prefix {p} does not match exactly one pool item")
    check(all(r["expected_task_type"] == "coding" and r["label_source"] == "rule_mapping" for r in by["deepswe"]),
          "DeepSWE labels")
    abd = collections.Counter(r["benchmark_subtype"] for r in by["automationbench"])
    check(abd == {**{d: 4 for d in C.AB_PUBLIC}, "simple": 6}, f"AB domains {abd}")
    check(all(r["label_source"] == "item_judgement" for r in by["automationbench"]), "AB label_source")
    check({r["task_id"] for r in by["automationbench"]} == set(B.AB_JUDGEMENTS), "AB judgement keys != sampled ids")
    check(all(r["official_difficulty"] is None for r in by["automationbench"] + by["deepswe"]),
          "agentic rows have no official difficulty")

    # secrets
    tok_path = "/root/.hf_token"
    tok = os.environ.get("HF_TOKEN") or (open(tok_path).read().strip() if os.path.exists(tok_path) else "")
    check(not tok or tok not in text, "HF token found in output")

    # summary
    print("clean per class:", dict(sorted(ct.items())))
    print("mode per class:", dict(collections.Counter(str(r["expected_task_type"]) for r in mode)))
    fit = collections.Counter((r["benchmark_subtype"], r["taxonomy_fit"]) for r in by["automationbench"])
    print("AutomationBench taxonomy_fit by domain:",
          {d: {f: fit[(d, f)] for f in B.FITS if fit[(d, f)]} for d in C.AB_PUBLIC + ["simple"]})
    print("official_difficulty:", dict(collections.Counter(str(r["official_difficulty"]) for r in recs)))

    if not skip_rebuild:
        with tempfile.TemporaryDirectory() as tmp:
            out = os.path.join(tmp, B.OUT_NAME)
            subprocess.run([sys.executable, os.path.join(C.REPO, "scripts", "build_stage1.py"), "--out", out],
                           check=True, stdout=subprocess.DEVNULL)
            a, b = sha(PATH), sha(out)
            print(f"rebuild hash: {a[:16]} {'==' if a == b else '!='} {b[:16]}")
            check(a == b, "rebuild is not byte-identical")

    if FAIL:
        print(f"FAILED ({len(FAIL)}):")
        for m in FAIL[:50]:
            print("  -", m)
        sys.exit(1)
    print("ALL CHECKS PASSED")


if __name__ == "__main__":
    main()
