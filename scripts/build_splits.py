"""Build splits/calibration_ids.txt and splits/holdout_ids.txt (70/30) over the union of ids
in datasets 1-4.

Stratum of an id = (gold_task_type or 'null', gold_execution_mode, official_difficulty or '-'),
taken from the first file (classification, boundary, execution_mode, capability) containing the id;
the builders guarantee these fields are identical across files for a shared id.  Assignment:
ids are seeded-shuffled (seed 20260929), stable-sorted by stratum, then assigned systematically
(position i goes to calibration iff floor((i+1)*0.7) > floor(i*0.7)), which gives 70/30 overall
and within +-1 item of 70/30 inside every stratum.  An id lives in exactly one split, so items
shared across datasets land on the same side.
Run after the four dataset builders: /root/bench/hle-venv/bin/python scripts/build_splits.py [--out-dir DIR]
"""
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import jev_common as C  # noqa: E402

FILES = ["datasets/jev_classification_eval_v1.jsonl", "datasets/jev_boundary_eval_v1.jsonl",
         "datasets/jev_execution_mode_eval_v1.jsonl", "datasets/jev_capability_eval_v1.jsonl"]
CAL = "splits/calibration_ids.txt"
HOLD = "splits/holdout_ids.txt"
FRAC = 0.7


def stratum(rec):
    d = rec.get("official_difficulty")
    return (rec.get("gold_task_type") or "null", rec.get("gold_execution_mode") or "null",
            "-" if d is None else str(d))


def load_union(out):
    first = {}
    for fn in FILES:
        with open(os.path.join(out, fn), encoding="utf-8") as f:
            for line in f:
                r = json.loads(line)
                first.setdefault(r["id"], r)
    return first


def assign(first):
    ids = sorted(first)
    C.rng().shuffle(ids)
    ids.sort(key=lambda i: stratum(first[i]))  # stable: keeps the seeded order inside a stratum
    cal, hold = [], []
    for i, x in enumerate(ids):
        (cal if math.floor((i + 1) * FRAC) > math.floor(i * FRAC) else hold).append(x)
    return sorted(cal), sorted(hold)


def main(argv=None):
    out = C.out_dir_arg(argv)
    first = load_union(out)
    cal, hold = assign(first)
    os.makedirs(os.path.join(out, "splits"), exist_ok=True)
    for fn, ids in ((CAL, cal), (HOLD, hold)):
        with open(os.path.join(out, fn), "w", encoding="utf-8", newline="\n") as f:
            f.write("\n".join(ids) + "\n")
    print(CAL, len(cal), HOLD, len(hold))


if __name__ == "__main__":
    main(sys.argv[1:])
