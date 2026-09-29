"""Build datasets/jev_capability_eval_v1.jsonl: items with an official difficulty field
(plus AutomationBench simple vs public, which is NOT an official difficulty).

gold_capability_need = null everywhere (no reliable ground truth).  label_source /
label_confidence describe the task_type label.
Run: /root/bench/hle-venv/bin/python scripts/build_capability.py [--out-dir DIR]
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import jev_common as C  # noqa: E402
from boundary_picks import boundary_ids  # noqa: E402
from build_classification import not_boundary  # noqa: E402

OUT_NAME = "datasets/jev_capability_eval_v1.jsonl"


def lcb():
    rows, used = C.load_lcb()  # newest release file (test6)
    picks = C.sample_quota(rows, {"easy": 10, "medium": 10, "hard": 10}, lambda r: r["difficulty"],
                           lambda r: r["platform"])
    return [C.lcb_record(r) for r in picks]


def math500():
    picks = C.sample_quota(C.load_math500(), {lv: 6 for lv in (1, 2, 3, 4, 5)}, lambda r: r["level"],
                           lambda r: r["subject"])
    return [C.math500_record(r) for r in picks]


def longbench():
    pool = [r for r in C.longbench_ra_pool() if not_boundary("longbench_v2")(r)]
    picks = C.sample_quota(pool, {"easy": 15, "hard": 15}, lambda r: r["difficulty"], lambda r: r["length"])
    ctx = C.longbench_contexts([r["_id"] for r in picks])
    return [C.longbench_record(r, ctx[r["_id"]]) for r in picks]


def tb2():
    b = boundary_ids()
    pool = [r for r in C.load_first_requests("tb2") if C.make_id("terminal_bench_2", r["_sid"]) not in b]
    diff = lambda r: C.task_meta("tb2", r["task_id"]).get("difficulty")  # noqa: E731
    n_easy = sum(1 for r in pool if diff(r) == "easy")
    quotas = {"easy": n_easy, "medium": (30 - n_easy) // 2, "hard": 30 - n_easy - (30 - n_easy) // 2}
    picks = C.sample_quota(pool, quotas, diff, lambda r: C.task_meta("tb2", r["task_id"]).get("category"))
    return [C.agentic_record("tb2", r) for r in picks]


def automationbench():
    b = boundary_ids()
    ab = [r for r in C.load_automationbench() if C.make_id("automationbench", r["_sid"]) not in b]
    simple = C.sample_round_robin([r for r in ab if r["domain"] == "simple"], 15, lambda r: "")
    pub = C.sample_round_robin([r for r in ab if r["domain"] in C.AB_PUBLIC], 15, lambda r: r["domain"])
    note = (" Capability slice: AutomationBench 'simple' (README: foundational single/two-step tasks, unscored) vs "
            "public scored domains. This split is NOT an official difficulty label -> official_difficulty=null; "
            "the domain is in official_category.")
    out = []
    for r in simple + pub:
        rec = C.ab_record(r)
        rec["notes"] += note
        rec["ab_slice"] = "simple" if r["domain"] == "simple" else "public"
        out.append(rec)
    return out


def build():
    return lcb() + math500() + longbench() + tb2() + automationbench()


def main(argv=None):
    out = C.out_dir_arg(argv)
    recs = build()
    C.write_jsonl(os.path.join(out, OUT_NAME), recs)
    print(OUT_NAME, len(recs), "LCB files used:", C.load_lcb()[1])


if __name__ == "__main__":
    main(sys.argv[1:])
