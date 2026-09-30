"""Measure Jev's input limit with synthetic single-message requests (Stage 1 prompt, frozen).
Writes context_limit/results.jsonl. Tokens reported by Jev (usage.input_tokens) on success;
on failure the size is estimated from the calibrated chars-per-token of the same filler."""
import json, os, sys, time, httpx
sys.path.insert(0, os.path.dirname(__file__))
from jev_client import load_prompt, questions, classify
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "context_limit", "results.jsonl"); os.makedirs(os.path.dirname(OUT), exist_ok=True)
key = open("/root/.jev_key").read().strip()
qdef = questions(*load_prompt(os.path.join(ROOT, "prompts", "jev_prompt_stage1.json")))
LINE = "Line {i}: the committee reviewed item {i} and recorded status pending for follow up.\n"
def body(n): return "".join(LINE.format(i=i) for i in range(n)) + "\nSummarize the status of all items."
c = httpx.Client()
def call(n):
    st = {"messages": [{"role": "user", "content": body(n)}]}
    s, d, ms, chars = classify(c, key, st, qdef, timeout=300)
    u = d.get("usage") or {}
    return {"lines": n, "chars": len(body(n)), "http_status": s, "ok": s == 200, "input_tokens": u.get("input_tokens"),
            "error": None if s == 200 else json.dumps(d)[:200], "latency_ms": ms}
f = open(OUT, "a")
def log(r): print(r, flush=True); f.write(json.dumps(r) + "\n"); f.flush()
base = call(0); log(base); cal = call(1000); log(cal)
per_line = (cal["input_tokens"] - base["input_tokens"]) / 1000; fixed = base["input_tokens"]
est = lambda n: round(fixed + per_line * n)
lines_for = lambda t: int((t - fixed) / per_line)
print(f"fixed={fixed} tokens/line={per_line:.3f}")
lo, hi = None, None
for t in (24000, 28000, 30000, 31000, 32000, 33000, 36000, 40000):
    r = call(lines_for(t)); r["target_tokens"] = t; r["est_tokens"] = est(r["lines"]); log(r)
    if r["ok"]: lo = max(lo or 0, r["lines"])
    elif hi is None or r["lines"] < hi: hi = r["lines"]
while lo is not None and hi is not None and hi - lo > 2:
    m = (lo + hi) // 2; r = call(m); r["est_tokens"] = est(m); r["bisect"] = True; log(r)
    if r["ok"]: lo = m
    else: hi = m
print("confirmed_max_success_lines", lo, "est", est(lo) if lo else None, "confirmed_min_failure_lines", hi, "est", est(hi) if hi else None)
