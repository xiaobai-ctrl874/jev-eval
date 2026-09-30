"""Stage 1.5 experiment B: real serving input capacity of the primary candidates on api.engy.ai.
Rejections are free and quote the gateway's own numbers; successes are kept to the minimum near each edge.
Filler prompt, "reply ok". Output: stage1_5/context_capacity_probes.jsonl (every request and response)."""
import json, os, re, sys, time, httpx
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "stage1_5", "context_capacity_probes.jsonl")
KEY = os.environ["ENGY_API_KEY"]; URL = "https://api.engy.ai/v1/chat/completions"
MODELS = sys.argv[1:] or ["deepseek-v4.1-flash", "deepseek-v4-flash-0731", "glm-5.3-flash", "glm-5.3", "kimi-k3"]
LINE = "Line {i}: the committee reviewed item {i} and recorded status pending for follow up.\n"
f = open(OUT, "a")
c = httpx.Client(timeout=1200)


def body_text(n):
    return "".join(LINE.format(i=i) for i in range(n)) + "\nReply with exactly one word: ok"


def call(model, lines, max_tokens, tag):
    body = {"model": model, "messages": [{"role": "user", "content": body_text(lines)}], "stream": False}
    if max_tokens is not None:
        body["max_tokens"] = max_tokens
    t0 = time.time()
    try:
        r = c.post(URL, json=body, headers={"Authorization": "Bearer " + KEY})
        d = r.json() if "json" in r.headers.get("content-type", "") else {"raw": r.text[:500]}
        status = r.status_code
    except Exception as e:
        d, status = {"exception": repr(e)[:300]}, None
    u = d.get("usage") or {}
    msg = json.dumps(d.get("error") or d.get("raw") or d.get("exception") or "")[:600] if status != 200 else None
    rec = {"model": model, "tag": tag, "lines": lines, "max_tokens": max_tokens, "status": status,
           "prompt_tokens": u.get("prompt_tokens"), "completion_tokens": u.get("completion_tokens"),
           "charged_micro": (d.get("x_engy") or {}).get("charged_micro"), "secs": round(time.time() - t0, 1), "error": msg}
    print(json.dumps(rec)[:400], flush=True); f.write(json.dumps(rec) + "\n"); f.flush()
    return rec


def nums(err):
    """Pull the gateway's numbers out of a capacity rejection."""
    out = {}
    for k, pat in (("prompt", r"prompt (?:is )?(\d+) tokens"), ("window", r"context window of (\d+)"),
                   ("max_input", r"at most (\d+) input"), ("max_output", r"/ (\d+)\s*output"),
                   ("live_window", r"largest live window is (\d+)"), ("input_msgs", r"(\d+) from the input messages")):
        m = re.search(pat, err or "")
        if m:
            out[k] = int(m.group(1))
    return out


models = {m["id"]: m for m in httpx.get("https://api.engy.ai/v1/models", headers={"Authorization": "Bearer " + KEY}).json()["data"]}
for model in MODELS:
    adv = models[model]["context_length"]
    print(f"=== {model}: /v1/models context_length {adv}", flush=True)
    # 1) oversized probe (rejected at the edge, free): learns the fleet window and the gateway's tokens/line
    over = call(model, int((adv + 60000) / 22), 8, "oversize")
    n = nums(over["error"]); tpl = n["prompt"] / over["lines"] if "prompt" in n else 24.0
    window = n.get("window") or adv
    # 2) just under the fleet window with a tiny output: either succeeds or is rejected by the operator spec
    r = call(model, int((window - 2000) / tpl), 8, "under_window_small_output")
    cap = window - 2000
    if r["status"] != 200:
        n2 = nums(r["error"])
        cap = n2.get("max_input") or cap
        r = call(model, int((cap - 1500) / tpl), 8, "under_spec_small_output")   # expected success
    # 3) normal output budget (explicit 65536, typical benchmark max): boundary from free rejections + one success
    mt = 65536
    lim = min(cap, window - mt)
    call(model, int((lim + 3000) / tpl), mt, "over_normal_output")               # expected rejection (free)
    call(model, int((lim - 3000) / tpl), mt, "under_normal_output")              # expected success (short reply)
