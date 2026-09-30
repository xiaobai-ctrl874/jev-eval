"""Prompt V2 re-test.
--mode full        : the 205 tasks that succeeded in Stage 1, same input and call path as Stage 1 (full messages)
                     -> STAGE1_V2_JEV_RESULTS.jsonl
--mode structured  : the 25 LongBench overflow tasks, structured routing input from STRUCTURED_OVERFLOW_INPUTS.jsonl
                     -> STRUCTURED_OVERFLOW_RESULTS.jsonl
Every record carries the production routing_mode that ROUTING_INPUT_POLICY_V2 would assign."""
import argparse, concurrent.futures as cf, datetime, hashlib, json, os, sys, httpx
sys.path.insert(0, os.path.dirname(__file__))
from jev_client import load_prompt, questions, classify, JEV_PRICE_PER_M_INPUT, DIMS
from jev_token_estimate import estimate_tokens
import run_stage1_jev as S1

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROMPT = os.path.join(ROOT, "prompts", "jev_prompt_v2.json")
SAFE_LIMIT = 30000


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["full", "structured"], required=True)
    ap.add_argument("--concurrency", type=int, default=4)
    a = ap.parse_args()
    key = open("/root/.jev_key").read().strip()
    qdef = questions(*load_prompt(PROMPT))
    prompt_tokens = 1384 + round((len(json.dumps(qdef, ensure_ascii=False)) - 5365) / 4)
    phash = hashlib.sha256(open(PROMPT, "rb").read()).hexdigest()
    gold = {json.loads(l)["id"]: json.loads(l) for l in open(os.path.join(ROOT, "GOLD_V2.jsonl"), encoding="utf-8")}
    s1 = {json.loads(l)["id"]: json.loads(l) for l in open(os.path.join(ROOT, "STAGE1_JEV_RESULTS.jsonl"), encoding="utf-8")}
    sets = {json.loads(l)["id"]: json.loads(l) for l in open(os.path.join(ROOT, "STAGE1_CLASSIFICATION_SET.jsonl"), encoding="utf-8")}
    if a.mode == "full":
        fr = S1.first_requests()
        items = [(i, S1.build_state(sets[i], fr)) for i, r in s1.items() if r["status"] == "ok"]
        out = os.path.join(ROOT, "STAGE1_V2_JEV_RESULTS.jsonl")
    else:
        items = [(o["id"], o["state"]) for o in map(json.loads, open(os.path.join(ROOT, "STRUCTURED_OVERFLOW_INPUTS.jsonl"), encoding="utf-8"))]
        out = os.path.join(ROOT, "STRUCTURED_OVERFLOW_RESULTS.jsonl")
    client = httpx.Client(limits=httpx.Limits(max_connections=a.concurrency))

    def one(item):
        i, state = item
        s, g = sets[i], gold[i]
        est = estimate_tokens(state, prompt_tokens)
        if a.mode == "full":
            mode = "full" if est <= SAFE_LIMIT else "overflow_fallback (called anyway for V1/V2 comparison)"
        else:
            mode = "structured_overflow"
        rec = {"id": i, "benchmark": s["benchmark"], "task_id": s["task_id"], "benchmark_subtype": s["benchmark_subtype"],
               "set": s["set"], "gold_task_type_v2": g["gold_task_type_v2"], "gold_execution_mode_v2": g["gold_execution_mode_v2"],
               "exclude_from_task_type_accuracy": g["exclude_from_task_type_accuracy"], "stage1_expected_task_type": s["expected_task_type"],
               "official_difficulty": s["official_difficulty"], "official_difficulty_raw": s["official_difficulty_raw"],
               "taxonomy_fit_stage1": s["taxonomy_fit"], "prompt_file": "prompts/jev_prompt_v2.json", "prompt_sha256": phash,
               "routing_mode": mode, "estimated_input_tokens": est, "state_chars": len(json.dumps(state, ensure_ascii=False)),
               "ts": datetime.datetime.now(datetime.timezone.utc).isoformat()}
        if a.mode == "full":
            v1 = s1[i]
            rec.update({f"v1_{d}": v1.get(f"jev_{d}") for d in DIMS})
            rec["v1_input_tokens"] = v1.get("input_tokens")
        try:
            status, body, ms, _ = classify(client, key, state, qdef)
        except Exception as e:
            rec.update({"status": "error", "error": f"{type(e).__name__}: {str(e)[:300]}"}); return rec
        rec.update({"http_status": status, "jev_latency_ms": ms})
        if status != 200:
            rec.update({"status": "error", "error": json.dumps(body)[:500]}); return rec
        u = body.get("usage") or {}
        rec.update({"status": "ok", "jev_model": body.get("model"), "input_tokens": u.get("input_tokens"),
                    "output_tokens": u.get("output_tokens"),
                    "jev_cost_usd": round((u.get("input_tokens") or 0) * JEV_PRICE_PER_M_INPUT / 1e6, 8)})
        for d in DIMS:
            x = (body.get("answers") or {}).get(d) or {}
            rec[f"jev_{d}"] = x.get("choice"); rec[f"jev_{d}_confidence"] = x.get("confidence")
            rec[f"jev_{d}_probabilities"] = x.get("probabilities")
        return rec

    with cf.ThreadPoolExecutor(a.concurrency) as ex:
        res = list(ex.map(one, items))
    with open(out, "w", encoding="utf-8") as f:
        for r in sorted(res, key=lambda r: r["id"]):
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    bad = [r for r in res if r["status"] != "ok"]
    print(f"{a.mode}: {len(res) - len(bad)}/{len(res)} ok -> {out}")
    for r in bad:
        print("  FAIL", r["id"], r.get("error", "")[:150])


if __name__ == "__main__":
    main()
