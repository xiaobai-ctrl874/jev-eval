"""Build datasets/jev_boundary_eval_v1.jsonl from the hand-picked items in boundary_picks.py.

All rows: label_source=human_review_required; gold_task_type = recommended_gold (builder's
recommendation, NOT verified gold).  Run: /root/bench/hle-venv/bin/python scripts/build_boundary.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import jev_common as C  # noqa: E402
from boundary_picks import BOUNDARY_PICKS  # noqa: E402

OUT_NAME = "datasets/jev_boundary_eval_v1.jsonl"


def natural_plan_record(sid, **kw):
    task = sid.rsplit("_example_", 1)[0]
    d = C.load_natural_plan(task)[sid]
    knobs = {k: d[k] for k in ("num_people", "num_days", "duration", "num_cities") if k in d}
    return C.record(
        bench_key="natural_plan", benchmark="NATURAL PLAN", source_id=sid, prompt=d["prompt_5shot"],
        gold_execution_mode="direct", official_category=task, official_difficulty=None,
        prompt_format="prompt_5shot (the official evaluation setting; prompt_0shot kept in extra field)",
        prompt_0shot=d["prompt_0shot"], complexity_knobs=knobs, **kw)


def build():
    lb_rows = C.by_sid(C.load_longbench_meta())
    lb_ids = [s for (_, b, s, *_r) in BOUNDARY_PICKS if b == "longbench_v2"]
    ctx = C.longbench_contexts(lb_ids)
    recs = []
    for pair, bench, sid, cands, rec_gold, conf, why in BOUNDARY_PICKS:
        common = dict(gold_task_type=rec_gold, tt_source="human_review_required", tt_conf=conf,
                      notes=f"Boundary item ({pair}). gold_task_type is the builder's recommendation only; "
                            "needs human review.")
        extra = dict(pair=pair, candidate_labels=cands, why_ambiguous=why, recommended_gold=rec_gold,
                     confidence=conf)
        if bench == "livebench_math" or bench == "livebench_reasoning":
            cat = bench.split("_")[1]
            r = C.by_sid(C.load_livebench(cat))[sid]
            rec = C.livebench_record(r, cat, **common, **extra)
        elif bench == "longbench_v2":
            r = lb_rows[sid]
            rec = C.longbench_record(r, ctx[sid], **common, **extra)
        elif bench == "writingbench":
            r = C.by_sid(C.load_writingbench())[sid]
            rec = C.wb_record(r, **common, **extra)
        elif bench == "automationbench":
            r = C.by_sid(C.load_automationbench())[sid]
            rec = C.ab_record(r, **common, **extra)
        elif bench in ("terminal_bench_4", "terminal_bench_2", "deepswe"):
            src = {"terminal_bench_4": "tb4", "terminal_bench_2": "tb2", "deepswe": "deepswe"}[bench]
            r = C.by_sid(C.load_first_requests(src))[sid]
            rec = C.agentic_record(src, r, gold_task_type=rec_gold, tt_source="human_review_required",
                                   tt_conf=conf, notes=common["notes"], **extra)
        elif bench == "planningbench":
            r = C.by_sid(C.load_planningbench())[sid]
            rec = C.planningbench_record(r, gold_task_type=rec_gold, task_type_label_source="human_review_required",
                                         task_type_confidence=conf, notes=common["notes"], **extra)
        elif bench == "natural_plan":
            rec = natural_plan_record(sid, gold_task_type=rec_gold, task_type_label_source="human_review_required",
                                      task_type_confidence=conf, notes=common["notes"], **extra)
        else:
            raise ValueError(bench)
        recs.append(rec)
    return recs


def main(argv=None):
    out = C.out_dir_arg(argv)
    recs = build()
    C.write_jsonl(os.path.join(out, OUT_NAME), recs)
    print(OUT_NAME, len(recs))


if __name__ == "__main__":
    main(sys.argv[1:])
