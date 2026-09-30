"""Stage 1.6: classify STAGE1_6_RESEARCH_SET.jsonl with frozen Prompt V2 (full input, one call each)."""
import concurrent.futures as cf, json, os, sys, httpx
sys.path.insert(0, os.path.dirname(__file__))
from jev_client import load_prompt, questions, classify, JEV_PRICE_PER_M_INPUT, DIMS
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
key = open("/root/.jev_key").read().strip()
qdef = questions(*load_prompt(os.path.join(ROOT, "prompts", "jev_prompt_v2.json")))
items = [json.loads(l) for l in open(os.path.join(ROOT, "STAGE1_6_RESEARCH_SET.jsonl"), encoding="utf-8")]
client = httpx.Client(limits=httpx.Limits(max_connections=4))
def one(s):
    st = {"messages": [{"role": "user", "content": s["prompt"]}]}
    rec = {k: s[k] for k in ("id", "benchmark", "task_id", "group", "benchmark_subtype", "gold_task_type", "gold_execution_mode")}
    for _ in range(3):
        try:
            status, body, ms, _ = classify(client, key, st, qdef); break
        except Exception as e:
            status, body, ms = None, {"error": repr(e)[:200]}, None
    rec.update({"http_status": status, "jev_latency_ms": ms})
    if status != 200:
        rec.update({"status": "error", "error": json.dumps(body)[:300]}); return rec
    u = body.get("usage") or {}
    rec.update({"status": "ok", "jev_input_tokens": u.get("input_tokens"), "output_tokens": u.get("output_tokens"),
                "jev_cost_usd": round((u.get("input_tokens") or 0) * JEV_PRICE_PER_M_INPUT / 1e6, 8)})
    for d in DIMS:
        x = (body.get("answers") or {}).get(d) or {}
        rec[f"jev_{d}"] = x.get("choice"); rec[f"jev_{d}_confidence"] = x.get("confidence"); rec[f"jev_{d}_probabilities"] = x.get("probabilities")
    return rec
with cf.ThreadPoolExecutor(4) as ex:
    res = list(ex.map(one, items))
with open(os.path.join(ROOT, "STAGE1_6_JEV_RESULTS.jsonl"), "w", encoding="utf-8") as f:
    for r in res:
        f.write(json.dumps(r, ensure_ascii=False) + "\n")
print(sum(r["status"] == "ok" for r in res), "/", len(res), "ok")
