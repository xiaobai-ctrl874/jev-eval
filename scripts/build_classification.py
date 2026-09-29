"""Build datasets/jev_classification_eval_v1.jsonl (~30 high-purity items per task_type).

Run: /root/bench/hle-venv/bin/python scripts/build_classification.py [--out-dir DIR]
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import jev_common as C  # noqa: E402
from boundary_picks import boundary_ids  # noqa: E402

OUT_NAME = "datasets/jev_classification_eval_v1.jsonl"


def not_boundary(bench_key):
    b = boundary_ids()
    return lambda r: C.make_id(bench_key, r["_sid"]) not in b


def general_qa():
    pool = [r for r in C.simpleqa_pool() if not_boundary("simpleqa_verified")(r)]
    topics = sorted({r["topic"] for r in pool})
    picks = C.sample_quota(pool, {t: 3 for t in topics}, lambda r: r["topic"], lambda r: r["answer_type"])
    return [C.simpleqa_record(r, notes_extra="Sampled 3 per topic, round-robin over answer_type; requires_reasoning=True excluded.")
            for r in picks]


def writing():
    pool = [r for r in C.writingbench_pool() if not_boundary("writingbench")(r)]
    picks = C.sample_round_robin(pool, 30, lambda r: r["domain2"])
    return [C.wb_record(r) for r in picks]


def lb_math_pool():
    nb = not_boundary("livebench_math")
    return [r for r in C.load_livebench("math") if nb(r) and not C.lb_math_twin_excluded(r)]


def math():
    lbm = C.sample_quota(lb_math_pool(), {"AMPS_Hard": 5, "math_comp": 5, "olympiad": 5},
                         lambda r: r["task"], lambda r: r["subtask"])
    m5 = C.sample_quota(C.load_math500(), {lv: 3 for lv in (1, 2, 3, 4, 5)},
                        lambda r: r["level"], lambda r: r["subject"])
    return [C.livebench_record(r, "math") for r in lbm] + [C.math500_record(r) for r in m5]


def reasoning():
    nb = not_boundary("livebench_reasoning")
    pool = [r for r in C.load_livebench("reasoning") if nb(r)]
    picks = C.sample_quota(pool, {"zebra_puzzle": 10, "web_of_lies_v2": 10, "spatial": 10},
                           lambda r: r["task"], lambda r: str(r["livebench_release_date"]))
    return [C.livebench_record(r, "reasoning") for r in picks]


def coding():
    rows, used = C.load_lcb()
    newest = [r for r in rows if r["_file"] == used[0]]
    picks = C.sample_quota(newest, {"easy": 10, "medium": 10, "hard": 10},
                           lambda r: r["difficulty"], lambda r: r["platform"])
    return [C.lcb_record(r) for r in picks]


def research():
    nb = not_boundary("longbench_v2")
    pool = [r for r in C.longbench_ra_pool() if nb(r)]
    subs = sorted({r["sub_domain"] for r in pool})
    picks = C.sample_quota(pool, {s: 6 for s in subs}, lambda r: r["sub_domain"],
                           lambda r: f"{r['difficulty']}|{r['length']}")
    ctx = C.longbench_contexts([r["_id"] for r in picks])
    return [C.longbench_record(r, ctx[r["_id"]]) for r in picks]


# Own sub-category tag (planning vs design) for the sampled PlanningBench items, judged item by
# item from the prompt text -> human_review_required.  Default 'planning'; exceptions listed here.
PB_SUBCAT_OVERRIDES = {}


def planning():
    nb = not_boundary("planningbench")
    pool = sorted([r for r in C.load_planningbench() if nb(r)], key=lambda r: r["_sid"])
    picks = C.rng().sample(pool, 30)
    out = []
    for r in picks:
        sub = PB_SUBCAT_OVERRIDES.get(r["_sid"], "planning")
        out.append(C.planningbench_record(
            r, sub_category=sub, sub_category_label_source="human_review_required",
            sub_category_note=("Builder's recommendation from reading the prompt: operational scheduling/allocation/"
                               "routing plan -> 'planning'. Needs human confirmation.")))
    return out


def workflow():
    nb = not_boundary("automationbench")
    pool = [r for r in C.load_automationbench() if r["domain"] in C.AB_PUBLIC and nb(r)]
    picks = C.sample_quota(pool, {d: 5 for d in C.AB_PUBLIC}, lambda r: r["domain"])
    return [C.ab_record(r) for r in picks]


def build():
    recs = general_qa() + writing() + math() + reasoning() + coding() + research() + planning() + workflow()
    return recs


def main(argv=None):
    out = C.out_dir_arg(argv)
    recs = build()
    C.write_jsonl(os.path.join(out, OUT_NAME), recs)
    print(OUT_NAME, len(recs), "LCB files used:", C.load_lcb()[1])


if __name__ == "__main__":
    main(sys.argv[1:])
