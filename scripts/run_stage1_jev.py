"""Stage 1: classify every task in STAGE1_CLASSIFICATION_SET.jsonl with Jev.

Input to Jev = the complete, real first request: full messages (no summary, no truncation) and,
for agentic tasks, the full tool schemas from the reconstructed first requests in raw/.
Records Jev output, input/output tokens, latency and cost per task.
Usage: run_stage1_jev.py [--concurrency 4] [--only-failed]
"""
import argparse, concurrent.futures as cf, datetime, hashlib, json, os, sys, threading, httpx
sys.path.insert(0, os.path.dirname(__file__))
from jev_client import load_prompt, questions, classify, JEV_PRICE_PER_M_INPUT, JEV_URL, DIMS

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROMPT = os.path.join(ROOT, "prompts", "jev_prompt_stage1.json")
SET = os.path.join(ROOT, "STAGE1_CLASSIFICATION_SET.jsonl")
OUT = os.path.join(ROOT, "STAGE1_JEV_RESULTS.jsonl")


def first_requests():
    idx = {}
    for line in open(os.path.join(ROOT, "raw/agentic_first_requests/deepswe_miniswe_first_requests.jsonl")):
        r = json.loads(line); idx[("DeepSWE", r["task_id"])] = r
    for line in open(os.path.join(ROOT, "raw/automationbench/first_requests_api.jsonl")):
        r = json.loads(line); idx[("AutomationBench", f"{r['domain']}:{r['example_id']}")] = r
    return idx


def build_state(row, fr):
    if row["benchmark"] in ("DeepSWE", "AutomationBench"):
        req = fr[(row["benchmark"], row["task_id"])]
        return {"messages": req["messages"], "tools": req["tools"]}
    msgs = []
    if row.get("system_prompt"):
        msgs.append({"role": "system", "content": row["system_prompt"]})
    msgs.append({"role": "user", "content": row["prompt"]})
    return {"messages": msgs}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--concurrency", type=int, default=4)
    ap.add_argument("--only-failed", action="store_true")
    a = ap.parse_args()
    key = open("/root/.jev_key").read().strip()
    pre, qs = load_prompt(PROMPT)
    qdef = questions(pre, qs)
    phash = hashlib.sha256(open(PROMPT, "rb").read()).hexdigest()
    rows = [json.loads(l) for l in open(SET, encoding="utf-8")]
    done = {}
    if os.path.exists(OUT):
        for l in open(OUT, encoding="utf-8"):
            r = json.loads(l); done[r["id"]] = r
    todo = [r for r in rows if r["id"] not in done or (a.only_failed and done[r["id"]]["status"] != "ok")]
    fr = first_requests()
    lock = threading.Lock()
    client = httpx.Client(limits=httpx.Limits(max_connections=a.concurrency))

    def one(row):
        state = build_state(row, fr)
        state_chars = len(json.dumps(state, ensure_ascii=False))
        rec = {k: row.get(k) for k in ("id", "benchmark", "task_id", "benchmark_subtype", "set", "expected_task_type",
                                       "expected_execution_mode", "official_difficulty", "official_difficulty_raw",
                                       "taxonomy_fit", "taxonomy_gap")}
        rec.update({"prompt_file": "prompts/jev_prompt_stage1.json", "prompt_sha256": phash, "jev_url": JEV_URL,
                    "input_mode": "full_messages_no_truncation", "state_chars": state_chars,
                    "n_messages": len(state["messages"]), "n_tools": len(state.get("tools") or []),
                    "ts": datetime.datetime.now(datetime.timezone.utc).isoformat()})
        try:
            status, body, ms, req_chars = classify(client, key, state, qdef)
        except Exception as e:
            rec.update({"status": "error", "error": f"{type(e).__name__}: {str(e)[:300]}"})
            return rec
        rec.update({"http_status": status, "jev_latency_ms": ms, "request_chars": req_chars})
        if status != 200:
            rec.update({"status": "error", "error": json.dumps(body)[:500]})
            return rec
        u = body.get("usage") or {}
        ans = body.get("answers") or {}
        rec.update({"status": "ok", "jev_model": body.get("model"),
                    "input_tokens": u.get("input_tokens"), "output_tokens": u.get("output_tokens"),
                    "jev_cost_usd": round((u.get("input_tokens") or 0) * JEV_PRICE_PER_M_INPUT / 1e6, 8),
                    "jev_cost_basis": "input_tokens x $0.042/M (output price not published; output tokens recorded)"})
        for dim in DIMS:
            d = ans.get(dim) or {}
            rec[f"jev_{dim}"] = d.get("choice")
            rec[f"jev_{dim}_confidence"] = d.get("confidence")
            rec[f"jev_{dim}_probabilities"] = d.get("probabilities")
        return rec

    results = dict(done)
    with cf.ThreadPoolExecutor(a.concurrency) as ex:
        for i, rec in enumerate(ex.map(one, todo), 1):
            with lock:
                results[rec["id"]] = rec
                print(f"[{i}/{len(todo)}] {rec['id'][:60]:60} {rec['status']:5} "
                      f"{rec.get('jev_task_type')}/{rec.get('jev_execution_mode')}/{rec.get('jev_capability_need')} "
                      f"tok={rec.get('input_tokens')} {rec.get('jev_latency_ms')}ms {rec.get('error','')[:120]}", flush=True)
    with open(OUT, "w", encoding="utf-8") as f:
        for r in rows:
            if r["id"] in results:
                f.write(json.dumps(results[r["id"]], ensure_ascii=False) + "\n")
    ok = sum(1 for r in results.values() if r["status"] == "ok")
    print(f"done: {ok}/{len(rows)} ok")


if __name__ == "__main__":
    main()
