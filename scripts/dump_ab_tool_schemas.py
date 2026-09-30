"""Dump the real OpenAI-format tool schemas the AutomationBench runner sends (verifiers env._all_oai_tools).
Stage 1 / V2 stored tool NAMES only for AutomationBench (bug in automationbench_first_request.py); this fixes it
without touching the frozen Stage 1 files. Run with /root/bench/AutomationBench/.venv/bin/python."""
import json
from automationbench.domains import DOMAINS
from automationbench.runner import AutomationBenchEnv
from datasets import Dataset
import verifiers as vf
row = dict(DOMAINS["sales"]()[0])
out = {}
for ts in ("api", "limited_zapier", "zapier"):
    env = AutomationBenchEnv(dataset=Dataset.from_list([row]), rubric=vf.Rubric(), toolset=ts)
    out[ts] = env._all_oai_tools
    print(ts, len(env._all_oai_tools), "tools,", len(json.dumps(env._all_oai_tools)), "chars")
json.dump(out, open("/root/bench/jev_eval/stage1_5/ab_tool_schemas.json", "w"), ensure_ascii=False)
