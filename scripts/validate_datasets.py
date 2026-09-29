"""Validate the Jev evaluation datasets and splits.

Checks: required fields; label values; ids unique per file; every source_id exists in raw data
and the prompt traces back to the raw item; cross-file consistency of shared ids; boundary extra
fields; expected counts; calibration/holdout disjoint and covering the union; stratum
proportions; and that re-running scripts/build_all.py into a temp dir reproduces byte-identical
files (sha256).  Exit code 1 on any failure.
Run: /root/bench/hle-venv/bin/python scripts/validate_datasets.py [--skip-rebuild]
"""
import collections
import hashlib
import json
import os
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import jev_common as C  # noqa: E402
from build_splits import CAL, FILES, HOLD, stratum  # noqa: E402

FAIL = []
WARN = []


def fail(msg):
    FAIL.append(msg)


def load(path):
    with open(path, encoding="utf-8") as f:
        return [json.loads(l) for l in f]


def raw_index():
    """bench_key -> {source_id: callable(record) -> bool prompt-trace check}"""
    idx = {}
    idx["simpleqa_verified"] = {str(r["_sid"]): (lambda rec, r=r: rec["prompt"] == r["problem"]) for r in C.load_simpleqa()}
    idx["writingbench"] = {str(r["_sid"]): (lambda rec, r=r: rec["prompt"] == r["query"]) for r in C.load_writingbench()}
    for cat in ("math", "reasoning"):
        idx[f"livebench_{cat}"] = {r["_sid"]: (lambda rec, r=r: rec["prompt"] == r["turns"][0]) for r in C.load_livebench(cat)}
    idx["math500"] = {r["_sid"]: (lambda rec, r=r: rec["prompt"] == r["problem"]) for r in C.load_math500()}
    rows, _ = C.load_lcb()
    idx["livecodebench"] = {r["_sid"]: (lambda rec, r=r: rec["prompt"] == C.lcb_prompt(r) and r["question_content"] in rec["prompt"]) for r in rows}
    idx["longbench_v2"] = {r["_sid"]: (lambda rec, r=r: r["question"].strip() in rec["prompt"]) for r in C.load_longbench_meta()}
    idx["planningbench"] = {str(r["_sid"]): (lambda rec, r=r: rec["prompt"] == r["messages"][0]["content"]) for r in C.load_planningbench()}
    npk = {}
    for t in ("calendar_scheduling", "meeting_planning", "trip_planning"):
        for k, d in C.load_natural_plan(t).items():
            npk[k] = (lambda rec, d=d: rec["prompt"] == d["prompt_5shot"])
    idx["natural_plan"] = npk
    ab = {}
    for r in C.load_automationbench():
        user = next(m["content"] for m in r["messages"] if m["role"] == "user")
        sysm = next(m["content"] for m in r["messages"] if m["role"] == "system")
        ab[r["_sid"]] = (lambda rec, u=user, s=sysm, t=list(r["tools"]): rec["prompt"] == u and rec["system_prompt"] == s and rec["tools"] == t)
    idx["automationbench"] = ab
    for src, key in (("deepswe", "deepswe"), ("tb4", "terminal_bench_4"), ("tb2", "terminal_bench_2")):
        d = {}
        for r in C.load_first_requests(src):
            user = next(m["content"] for m in r["messages"] if m["role"] == "user")
            sysm = next(m["content"] for m in r["messages"] if m["role"] == "system")
            d[r["_sid"]] = (lambda rec, u=user, s=sysm, t=C.tool_names(r["tools"]): rec["prompt"] == u and rec["system_prompt"] == s and rec["tools"] == t)
        idx[key] = d
    return idx


def check_file(fn, recs, idx):
    ids = [r["id"] for r in recs]
    dup = [i for i, c in collections.Counter(ids).items() if c > 1]
    if dup:
        fail(f"{fn}: duplicate ids {dup[:5]}")
    for r in recs:
        miss = [k for k in C.REQUIRED_FIELDS if k not in r]
        if miss:
            fail(f"{fn} {r.get('id')}: missing fields {miss}")
            continue
        if r["gold_task_type"] is not None and r["gold_task_type"] not in C.TASK_TYPES:
            fail(f"{fn} {r['id']}: bad gold_task_type {r['gold_task_type']}")
        if r["gold_execution_mode"] not in C.EXEC_MODES:
            fail(f"{fn} {r['id']}: bad gold_execution_mode")
        if r["gold_capability_need"] is not None:
            fail(f"{fn} {r['id']}: gold_capability_need must be null in v1")
        if r["label_source"] not in C.LABEL_SOURCES:
            fail(f"{fn} {r['id']}: bad label_source {r['label_source']}")
        if r["label_confidence"] not in C.CONFIDENCES:
            fail(f"{fn} {r['id']}: bad label_confidence")
        for k in ("task_type_label_source", "execution_mode_label_source"):
            if r.get(k) not in C.LABEL_SOURCES:
                fail(f"{fn} {r['id']}: bad {k}")
        if r["gold_task_type"] is None and r["task_type_label_source"] != "human_review_required":
            fail(f"{fn} {r['id']}: null task_type must be human_review_required")
        if not isinstance(r["prompt"], str) or not r["prompt"].strip():
            fail(f"{fn} {r['id']}: empty prompt")
        if r["tools"] is not None and not (isinstance(r["tools"], list) and all(isinstance(t, str) for t in r["tools"])):
            fail(f"{fn} {r['id']}: tools must be null or list of names")
        bench_key, sid = r["id"].split(":", 1)
        if sid != r["source_id"]:
            fail(f"{fn} {r['id']}: id/source_id mismatch")
        chk = idx.get(bench_key, {}).get(r["source_id"])
        if chk is None:
            fail(f"{fn} {r['id']}: source_id not found in raw data for {bench_key}")
        elif not chk(r):
            fail(f"{fn} {r['id']}: prompt/system/tools do not match raw item")
        if r["benchmark"] == "LongBench v2":
            if not r.get("context_ref"):
                fail(f"{fn} {r['id']}: LongBench item without context_ref")
            pas = r.get("prompt_as_sent")
            if r.get("context_available_locally"):
                if pas is None or len(pas) > C.LB_MAX_CHARS:
                    fail(f"{fn} {r['id']}: prompt_as_sent missing or > {C.LB_MAX_CHARS} chars")
                if r.get("prompt_as_sent_truncated") != (r.get("prompt_as_sent_full_chars", 0) > C.LB_MAX_CHARS):
                    fail(f"{fn} {r['id']}: truncation flag inconsistent")


def main():
    skip_rebuild = "--skip-rebuild" in sys.argv
    repo = C.REPO
    idx = raw_index()
    data = {fn: load(os.path.join(repo, fn)) for fn in FILES}
    for fn, recs in data.items():
        check_file(fn, recs, idx)

    cls, bnd, exe, cap = (data[f] for f in FILES)
    # expected composition
    c = collections.Counter(r["gold_task_type"] for r in cls)
    for t in C.TASK_TYPES:
        if c[t] != 30:
            WARN.append(f"classification: {t} has {c[t]} items (target 30)")
    if any(r["label_source"] == "human_review_required" for r in cls):
        fail("classification: contains human_review_required task_type labels")
    for r in bnd:
        for k in ("candidate_labels", "why_ambiguous", "recommended_gold", "confidence", "pair"):
            if k not in r:
                fail(f"boundary {r['id']}: missing {k}")
        if r["label_source"] != "human_review_required":
            fail(f"boundary {r['id']}: label_source must be human_review_required")
        if r.get("recommended_gold") not in r.get("candidate_labels", []):
            fail(f"boundary {r['id']}: recommended_gold not among candidate_labels")
    em = collections.Counter(r["gold_execution_mode"] for r in exe)
    if em["direct"] != 100 or em["agentic"] != 100:
        fail(f"execution_mode: expected 100/100, got {dict(em)}")
    for r in exe:
        if r["execution_mode_label_source"] != "rule_mapping" or r["label_source"] != "rule_mapping":
            fail(f"execution_mode {r['id']}: execution_mode label must be rule_mapping")
    ids_bnd = {r["id"] for r in bnd}
    for fn in (FILES[0], FILES[2], FILES[3]):
        inter = ids_bnd & {r["id"] for r in data[fn]}
        if inter:
            fail(f"{fn}: shares boundary ids {sorted(inter)[:3]}")
    for r in cap:
        if r["benchmark"] == "AutomationBench" and r["official_difficulty"] is not None:
            fail(f"capability {r['id']}: AutomationBench must have official_difficulty=null")

    # cross-file consistency
    seen = {}
    keys = ("benchmark", "source_id", "prompt", "system_prompt", "tools", "gold_task_type", "gold_execution_mode",
            "official_category", "official_difficulty", "task_type_label_source", "execution_mode_label_source")
    for fn, recs in data.items():
        for r in recs:
            sig = tuple(json.dumps(r.get(k), ensure_ascii=False, sort_keys=True) for k in keys)
            if r["id"] in seen and seen[r["id"]][1] != sig:
                diff = [k for k, a, b in zip(keys, seen[r["id"]][1], sig) if a != b]
                fail(f"id {r['id']} differs between {seen[r['id']][0]} and {fn}: {diff}")
            seen.setdefault(r["id"], (fn, sig))
    union = set(seen)

    # splits
    def read_ids(p):
        with open(os.path.join(repo, p), encoding="utf-8") as f:
            return [l.strip() for l in f if l.strip()]
    cal, hold = read_ids(CAL), read_ids(HOLD)
    if len(cal) != len(set(cal)) or len(hold) != len(set(hold)):
        fail("splits: duplicate ids inside a split file")
    if set(cal) & set(hold):
        fail(f"splits: {len(set(cal) & set(hold))} ids in both calibration and holdout")
    if set(cal) | set(hold) != union:
        fail(f"splits: cover mismatch (missing {len(union - set(cal) - set(hold))}, extra {len((set(cal) | set(hold)) - union)})")
    first = {}
    for fn in FILES:
        for r in data[fn]:
            first.setdefault(r["id"], r)
    calset = set(cal)
    tot = len(union)
    print(f"union ids: {tot}  calibration: {len(cal)} ({len(cal)/tot:.3f})  holdout: {len(hold)} ({len(hold)/tot:.3f})")
    print("stratum proportions by gold_task_type (calibration share):")
    by_tt = collections.defaultdict(list)
    for i, r in first.items():
        by_tt[r["gold_task_type"] or "null"].append(i in calset)
    for k in sorted(by_tt):
        v = by_tt[k]
        share = sum(v) / len(v)
        print(f"  {k:20s} n={len(v):4d} cal={sum(v):4d} share={share:.3f}")
        if len(v) >= 10 and abs(share - 0.7) > 0.1:
            fail(f"splits: task_type stratum {k} share {share:.3f} deviates >0.1 from 0.7")
    by_em = collections.defaultdict(list)
    for i, r in first.items():
        by_em[r["gold_execution_mode"]].append(i in calset)
    for k in sorted(by_em):
        v = by_em[k]
        print(f"  execution_mode={k:8s} n={len(v):4d} share={sum(v)/len(v):.3f}")
        if abs(sum(v) / len(v) - 0.7) > 0.1:
            fail(f"splits: execution_mode {k} share deviates")
    by_st = collections.defaultdict(list)
    for i, r in first.items():
        by_st[stratum(r)].append(i in calset)
    worst = max(abs(sum(v) - 0.7 * len(v)) for v in by_st.values())
    print(f"  fine strata (task_type x execution_mode x official_difficulty): {len(by_st)}; "
          f"max |cal - 0.7n| = {worst:.2f} items")
    if worst > 1.0 + 1e-9:
        fail("splits: a fine stratum deviates by more than 1 item from 70%")

    # secret hygiene: the HF token must not appear in any output
    tokp = "/root/.hf_token"
    if os.path.exists(tokp):
        tok = open(tokp).read().strip()
        for fn in FILES + [CAL, HOLD]:
            if tok and tok in open(os.path.join(repo, fn), encoding="utf-8").read():
                fail(f"{fn}: contains the HF token")

    # reproducibility
    if not skip_rebuild:
        tmp = tempfile.mkdtemp(prefix="jev_rebuild_")
        subprocess.run([sys.executable, os.path.join(repo, "scripts", "build_all.py"), "--out-dir", tmp],
                       check=True, capture_output=True)
        print("rebuild hash compare:")
        for fn in FILES + [CAL, HOLD]:
            a = hashlib.sha256(open(os.path.join(repo, fn), "rb").read()).hexdigest()
            b = hashlib.sha256(open(os.path.join(tmp, fn), "rb").read()).hexdigest()
            print(f"  {fn:45s} {a[:16]} {'==' if a == b else '!='} {b[:16]}")
            if a != b:
                fail(f"rebuild differs: {fn}")

    for fn, recs in data.items():
        print(f"{fn}: {len(recs)} rows")
    for w in WARN:
        print("WARN:", w)
    if FAIL:
        print(f"FAILED ({len(FAIL)} problems):")
        for f in FAIL[:50]:
            print("  -", f)
        sys.exit(1)
    print("ALL CHECKS PASSED")


if __name__ == "__main__":
    main()
