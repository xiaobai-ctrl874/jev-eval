"""Build datasets/jev_execution_mode_eval_v1.jsonl: 100 direct + 100 agentic items.

execution_mode labels come from benchmark structure (rule_mapping).  label_source /
label_confidence in this file describe execution_mode (primary="execution_mode").
Run: /root/bench/hle-venv/bin/python scripts/build_execution_mode.py [--out-dir DIR]
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import jev_common as C  # noqa: E402
from boundary_picks import boundary_ids  # noqa: E402
from build_classification import lb_math_pool, not_boundary  # noqa: E402

OUT_NAME = "datasets/jev_execution_mode_eval_v1.jsonl"
P = dict(primary="execution_mode")

DIRECT_QUOTAS = {"simpleqa": 13, "writingbench": 13, "livebench_math": 11, "math500": 11,
                 "livebench_reasoning": 13, "livecodebench": 13, "longbench_v2": 13, "planningbench": 13}
AGENTIC_QUOTAS = {"deepswe": 25, "tb4": 20, "tb2": 25, "ab_public": 24, "ab_simple": 6}


def direct():
    q = DIRECT_QUOTAS
    recs = []
    pool = [r for r in C.simpleqa_pool() if not_boundary("simpleqa_verified")(r)]
    recs += [C.simpleqa_record(r, **P) for r in C.sample_round_robin(pool, q["simpleqa"], lambda r: r["topic"])]
    pool = [r for r in C.writingbench_pool() if not_boundary("writingbench")(r)]
    recs += [C.wb_record(r, **P) for r in C.sample_round_robin(pool, q["writingbench"], lambda r: r["domain2"])]
    recs += [C.livebench_record(r, "math", **P)
             for r in C.sample_round_robin(lb_math_pool(), q["livebench_math"], lambda r: r["task"])]
    recs += [C.math500_record(r, **P)
             for r in C.sample_round_robin(C.load_math500(), q["math500"], lambda r: r["level"])]
    pool = [r for r in C.load_livebench("reasoning") if not_boundary("livebench_reasoning")(r)]
    recs += [C.livebench_record(r, "reasoning", **P)
             for r in C.sample_round_robin(pool, q["livebench_reasoning"], lambda r: r["task"])]
    rows, used = C.load_lcb()
    newest = [r for r in rows if r["_file"] == used[0]]
    recs += [C.lcb_record(r, **P)
             for r in C.sample_round_robin(newest, q["livecodebench"], lambda r: r["difficulty"])]
    pool = [r for r in C.longbench_ra_pool() if not_boundary("longbench_v2")(r)]
    lb = C.sample_round_robin(pool, q["longbench_v2"], lambda r: r["sub_domain"])
    ctx = C.longbench_contexts([r["_id"] for r in lb])
    recs += [C.longbench_record(r, ctx[r["_id"]], **P) for r in lb]
    pool = sorted([r for r in C.load_planningbench() if not_boundary("planningbench")(r)], key=lambda r: r["_sid"])
    recs += [C.planningbench_record(r, **P) for r in C.rng().sample(pool, q["planningbench"])]
    return recs


def agentic():
    q = AGENTIC_QUOTAS
    b = boundary_ids()
    recs = []
    for src, key, strat in (("deepswe", "deepswe", "language"), ("tb4", "terminal_bench_4", "category"),
                            ("tb2", "terminal_bench_2", "category")):
        pool = [r for r in C.load_first_requests(src) if C.make_id(key, r["_sid"]) not in b]
        picks = C.sample_round_robin(pool, q[src], lambda r, s=src, k=strat: C.task_meta(s, r["task_id"]).get(k))
        recs += [C.agentic_record(src, r, **P) for r in picks]
    ab = [r for r in C.load_automationbench() if C.make_id("automationbench", r["_sid"]) not in b]
    pub = C.sample_quota([r for r in ab if r["domain"] in C.AB_PUBLIC], {d: q["ab_public"] // 6 for d in C.AB_PUBLIC},
                         lambda r: r["domain"])
    simple = C.sample_round_robin([r for r in ab if r["domain"] == "simple"], q["ab_simple"], lambda r: "")
    recs += [C.ab_record(r, **P) for r in pub + simple]
    return recs


def build():
    return direct() + agentic()


def main(argv=None):
    out = C.out_dir_arg(argv)
    recs = build()
    C.write_jsonl(os.path.join(out, OUT_NAME), recs)
    print(OUT_NAME, len(recs))


if __name__ == "__main__":
    main(sys.argv[1:])
