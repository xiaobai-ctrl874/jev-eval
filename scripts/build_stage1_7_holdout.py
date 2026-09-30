"""Stage 1.7 holdout for Prompt V3 (never used for tuning). Built and committed BEFORE any V3 run.
Items are disjoint from STAGE1_CLASSIFICATION_SET and STAGE1_6_RESEARCH_SET.
research_analysis 30 (TableBench DataAnalysis 22 + WritingBench data-analysis 8),
general_qa 10 (TableBench MatchBased 5 + SimpleQA Verified 5), reasoning_planning 10 (LiveBench reasoning
non-spatial 5 + PlanningBench 5). Seed 20261001. Output: STAGE1_7_HOLDOUT_SET.jsonl"""
import json, os, random, sys
sys.path.insert(0, os.path.dirname(__file__))
import jev_common as J
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "raw")
SEED = 20261001
used = set()
for f in ("STAGE1_CLASSIFICATION_SET.jsonl", "STAGE1_6_RESEARCH_SET.jsonl"):
    for l in open(os.path.join(ROOT, f), encoding="utf-8"):
        r = json.loads(l); used.add(r["id"]); used.add(f"{r['benchmark']}::{r['task_id']}")
out = []
def add(**k):
    assert k["id"] not in used, k["id"]; out.append(k)
def pick(pool, n, key):
    pool = sorted(pool, key=key); random.Random(SEED).shuffle(pool); return pool[:n]

tb = [json.loads(l) for l in open(os.path.join(RAW, "tablebench", "TableBench.jsonl"), encoding="utf-8")]
tb_prompt = lambda r: "Read the table below in JSON format:\n[TABLE]\n" + json.dumps(r["table"], ensure_ascii=False) + "\n\nQuestion: " + r["question"]
for sub, n, gold in (("CausalAnalysis", 6, "research_analysis"), ("ImpactAnalysis", 6, "research_analysis"),
                     ("DescriptiveAnalysis", 6, "research_analysis"), ("AnomalyDetection", 4, "research_analysis"),
                     ("MatchBased", 5, "general_qa")):
    pool = [r for r in tb if r["qsubtype"] == sub and f"tablebench:{r['id']}" not in used]
    for r in pick(pool, n, lambda r: r["id"]):
        add(id=f"tablebench:{r['id']}", benchmark="TableBench", task_id=r["id"], benchmark_subtype=f"{r['qtype']}/{sub}",
            prompt=tb_prompt(r), gold_task_type=gold, gold_execution_mode="direct", label_source="rule_mapping")
wb = {json.loads(l)["index"]: json.loads(l) for l in open(os.path.join(RAW, "writingbench", "benchmark_all.jsonl"), encoding="utf-8")}
for i in (64, 65, 66, 94, 104, 306, 566, 902):
    r = wb[i]
    add(id=f"writingbench:{i}", benchmark="WritingBench", task_id=str(i), benchmark_subtype=f"{r['domain1']}/{r['domain2']}",
        prompt=r["query"], gold_task_type="research_analysis", gold_execution_mode="direct", label_source="item_judgement",
        notes="request supplies data and asks for an analysis report")
sq = [r for r in J.simpleqa_pool() if f"simpleqa_verified:{r['_sid']}" not in used]
for r in pick(sq, 5, lambda r: r["_sid"]):
    add(id=f"simpleqa_verified:{r['_sid']}", benchmark="SimpleQA Verified", task_id=str(r["_sid"]), benchmark_subtype=r["topic"],
        prompt=r["problem"], gold_task_type="general_qa", gold_execution_mode="direct", label_source="rule_mapping")
lr = [r for r in J.load_livebench("reasoning") if r["task"] in ("zebra_puzzle", "web_of_lies_v2")
      and f"livebench_reasoning:{r['_sid']}" not in used]
for r in pick(lr, 5, lambda r: r["_sid"]):
    add(id=f"livebench_reasoning:{r['_sid']}", benchmark="LiveBench reasoning", task_id=r["_sid"], benchmark_subtype=r["task"],
        prompt=r["turns"][0], gold_task_type="reasoning_planning", gold_execution_mode="direct", label_source="benchmark_native")
pb = [r for r in J.load_planningbench() if f"planningbench:{r['_sid']}" not in used]
for r in pick(pb, 5, lambda r: r["_sid"]):
    add(id=f"planningbench:{r['_sid']}", benchmark="PlanningBench (tencent)", task_id=str(r["_sid"]), benchmark_subtype="planning",
        prompt=r["messages"][0]["content"], gold_task_type="reasoning_planning", gold_execution_mode="direct", label_source="rule_mapping")
with open(os.path.join(ROOT, "STAGE1_7_HOLDOUT_SET.jsonl"), "w", encoding="utf-8") as f:
    for o in out:
        f.write(json.dumps(o, ensure_ascii=False) + "\n")
from collections import Counter
print(len(out), Counter(o["gold_task_type"] for o in out))
