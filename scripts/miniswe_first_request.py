"""Reconstruct the first request mini-swe-agent (config mini.yaml, as used by Pier/Harbor `-c mini.yaml`)
would send for DeepSWE / Terminal-Bench tasks. No model call, no container.

Run: /root/bench/.msa/bin/python /root/bench/jev_eval/scripts/miniswe_first_request.py
Notes:
- {{system}} {{release}} {{version}} {{machine}} come from uname() INSIDE the task container at runtime;
  here they are filled with placeholder "Linux <release> <version> x86_64" (UNKNOWN exact values).
- Pier/Harbor pass the raw instruction.md text as --task (Harbor may append MCP server info if configured; none for these tasks).
- tools = [BASH_TOOL] from minisweagent.models.utils.actions_toolcall (tool-calling mode of mini.yaml).
"""
import json
import os
from pathlib import Path

import yaml
from jinja2 import StrictUndefined, Template
import minisweagent
from minisweagent.models.utils.actions_toolcall import BASH_TOOL

cfg_path = Path(minisweagent.__file__).parent / "config" / "mini.yaml"
cfg = yaml.safe_load(cfg_path.read_text())
sys_t = cfg["agent"]["system_template"]
inst_t = cfg["agent"]["instance_template"]
placeholder = dict(system="Linux", release="<release>", version="<version>", machine="x86_64")

SOURCES = {
    "deepswe": "/root/bench/deep-swe/tasks",
    "tb4": "/root/bench/tb4/terminal-bench-4.0.0/tasks",
    "tb2": "/root/bench/tb2/terminal-bench",
}
out_dir = "/root/bench/jev_eval/raw/agentic_first_requests"
os.makedirs(out_dir, exist_ok=True)
for name, root in SOURCES.items():
    n = 0
    with open(f"{out_dir}/{name}_miniswe_first_requests.jsonl", "w") as f:
        for d in sorted(Path(root).iterdir()):
            ins = d / "instruction.md"
            if not ins.is_file():
                continue
            task = ins.read_text()
            msgs = [
                {"role": "system", "content": Template(sys_t, undefined=StrictUndefined).render(task=task, **placeholder)},
                {"role": "user", "content": Template(inst_t, undefined=StrictUndefined).render(task=task, **placeholder)},
            ]
            f.write(json.dumps({"source": name, "task_id": d.name, "messages": msgs, "tools": [BASH_TOOL],
                                "instruction_chars": len(task)}, ensure_ascii=False) + "\n")
            n += 1
    print(name, n, "tasks")
print("config:", cfg_path, "mini-swe-agent", getattr(minisweagent, "__version__", "?"))
