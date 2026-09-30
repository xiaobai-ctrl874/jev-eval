"""Direct Jev client for Stage 1: full real messages (no summary, no truncation) + full tool schemas."""
import json, time, httpx
JEV_URL = "https://api.typesafe.ai/v1/systemone"
JEV_MODEL = "jev-latest"
JEV_PRICE_PER_M_INPUT = 0.042   # USD per 1M input tokens (TypeSafe list price recorded 2026-09-23); verify against billing
DIMS = ("task_type", "execution_mode", "capability_need")

def load_prompt(path):
    d = json.load(open(path, encoding="utf-8"))
    return d["preamble"], d["questions"]

def questions(preamble, qs):
    # same assembly as autoroute.AutoRouter._questions
    return {dim: {"type": "choice", "instructions": preamble + "\n\n" + qs[dim]["instructions"],
                  "criteria": dict(qs[dim]["criteria"])} for dim in DIMS}

def classify(client, key, state, qdef, timeout=180.0):
    body = {"model": JEV_MODEL, "state": state, "questions": qdef}
    t0 = time.monotonic()
    r = client.post(JEV_URL, json=body, headers={"authorization": f"Bearer {key}"}, timeout=timeout)
    ms = int((time.monotonic() - t0) * 1000)
    return r.status_code, (r.json() if r.headers.get("content-type", "").startswith("application/json") else {"raw": r.text[:500]}), ms, len(json.dumps(body, ensure_ascii=False))
