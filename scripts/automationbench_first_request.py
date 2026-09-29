"""Reconstruct AutomationBench first requests (system + user + tools) WITHOUT running any model.

Run with the AutomationBench venv:
  /root/bench/AutomationBench/.venv/bin/python /root/bench/jev_eval/scripts/automationbench_first_request.py [toolset]
toolset: api (CLI default) | limited_zapier | zapier
Outputs /root/bench/jev_eval/raw/automationbench/first_requests_<toolset>.jsonl and prints per-domain counts.
"""
import json
import os
import sys
from collections import Counter

from automationbench.domains import DOMAINS
from automationbench.runner import AutomationBenchEnv

toolset = sys.argv[1] if len(sys.argv) > 1 else "api"
out_dir = "/root/bench/jev_eval/raw/automationbench"
os.makedirs(out_dir, exist_ok=True)

all_rows = []
counts = {}
for dom, loader in DOMAINS.items():
    ds = loader()
    counts[dom] = len(ds)
    for r in ds:
        r = dict(r)
        r["_domain"] = dom
        all_rows.append(r)
print("per-domain counts:", counts, "total:", sum(counts.values()))

# Build an env only to get the tool registry (no model/client is created).
from datasets import Dataset
import verifiers as vf

tiny = Dataset.from_list([{k: v for k, v in all_rows[0].items() if k != "_domain"}])
env = AutomationBenchEnv(dataset=tiny, rubric=vf.Rubric(), toolset=toolset)
all_tools = env._all_oai_tools
tool_by_name = {t["function"]["name"]: t for t in all_tools}
print("registered tools for toolset", toolset, ":", len(all_tools))

sys_prompts = Counter()
out_path = f"{out_dir}/first_requests_{toolset}.jsonl"
with open(out_path, "w") as f:
    for r in all_rows:
        info = r["info"]
        if isinstance(info, str):
            info = json.loads(info)
        if toolset == "limited_zapier":
            tools = [tool_by_name[n] for n in info.get("zapier_tools", []) if n in tool_by_name]
        else:
            tools = all_tools
        msgs = r["prompt"]
        for m in msgs:
            if m["role"] == "system":
                sys_prompts[(r["_domain"], m["content"][:80])] += 1
        f.write(json.dumps({
            "domain": r["_domain"],
            "example_id": r.get("example_id"),
            "task": r.get("task"),
            "messages": msgs,
            "tools": tools if toolset == "limited_zapier" else [t["function"]["name"] for t in tools],
            "zapier_tools_listed": info.get("zapier_tools", []),
        }, ensure_ascii=False) + "\n")
print("wrote", out_path)
print("distinct system prompts (domain, prefix):")
for k, v in sys_prompts.items():
    print(" ", v, k)
