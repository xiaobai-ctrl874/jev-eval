"""Structured-overflow routing inputs for the LongBench v2 items whose full input exceeded Jev's limit.
Simulates a document-attachment scenario: the routing input carries the complete question/instruction
and only metadata a production system could know (approximate input tokens, modality). No document text,
no benchmark name, no category/sub-domain metadata. Output: STRUCTURED_OVERFLOW_INPUTS.jsonl (not run)."""
import json, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from jev_token_estimate import estimate_tokens
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
S = {json.loads(l)["id"]: json.loads(l) for l in open(os.path.join(ROOT, "STAGE1_CLASSIFICATION_SET.jsonl"), encoding="utf-8")}
R = [json.loads(l) for l in open(os.path.join(ROOT, "STAGE1_JEV_RESULTS.jsonl"), encoding="utf-8")]
HEAD = "Please read the following text and answer the question below."
out = []
for r in R:
    if r["status"] == "ok" or r["benchmark"] != "LongBench v2":
        continue
    s = S[r["id"]]; p = s["prompt"]
    k = p.rfind("What is the correct answer")
    assert p.startswith(HEAD) and k > 0, r["id"]
    instruction = HEAD + "\n\n[The text is provided as a separate attached document.]\n\n" + p[k:].strip()
    full_state = {"messages": [{"role": "user", "content": p}]}
    state = {"messages": [{"role": "user", "content": instruction}],
             "attached_context": {"modality": "text", "approx_tokens": estimate_tokens(full_state, 0)}}
    out.append({"id": r["id"], "task_id": s["task_id"], "expected_task_type": s["expected_task_type"],
                "expected_execution_mode": s["expected_execution_mode"], "official_difficulty": s["official_difficulty"],
                "original_chars": len(p), "state": state})
with open(os.path.join(ROOT, "STRUCTURED_OVERFLOW_INPUTS.jsonl"), "w", encoding="utf-8") as f:
    for o in out:
        f.write(json.dumps(o, ensure_ascii=False) + "\n")
print(len(out), "items; approx_tokens range", min(o["state"]["attached_context"]["approx_tokens"] for o in out), max(o["state"]["attached_context"]["approx_tokens"] for o in out))
