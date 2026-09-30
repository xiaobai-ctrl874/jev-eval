"""Dump AutomationBench per-task metadata (no model is run): domain, example_id, task_name and the
assertion type list of every task.  Used by build_stage1.py (benchmark_subtype / traceability) and
as evidence for the item judgements.

Run with the AutomationBench venv:
  /root/bench/AutomationBench/.venv/bin/python /root/bench/jev_eval/scripts/automationbench_task_meta.py
Output: /root/bench/jev_eval/raw/automationbench/task_meta.jsonl
"""
import json
import os

from automationbench.domains import DOMAINS

out = "/root/bench/jev_eval/raw/automationbench/task_meta.jsonl"
os.makedirs(os.path.dirname(out), exist_ok=True)
n = 0
with open(out, "w", encoding="utf-8") as f:
    for dom, loader in DOMAINS.items():
        for r in loader():
            info = r["info"]
            if isinstance(info, str):
                info = json.loads(info)
            asserts = info.get("assertions") or []
            if isinstance(asserts, str):
                asserts = json.loads(asserts)
            f.write(json.dumps({
                "domain": dom,
                "example_id": r.get("example_id"),
                "task_name": info.get("task_name"),
                "assertion_types": [a.get("type") for a in asserts if isinstance(a, dict)],
                "n_assertions": len(asserts),
            }, ensure_ascii=False) + "\n")
            n += 1
print("wrote", out, n)
