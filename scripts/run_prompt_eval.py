"""Run a Jev prompt version over a task set (one call per task, full input, same client as all earlier stages).
--set stage1_6_dev    : STAGE1_6_RESEARCH_SET.jsonl (dev, 36)
--set stage1_7_holdout: STAGE1_7_HOLDOUT_SET.jsonl (holdout, 50)
--set stage1_205      : the 205 Stage 1 tasks that succeeded, same input as V1/V2 (gold from GOLD_V2.jsonl)
Output: <out> jsonl; prints accuracy by gold class and Jev usage."""
import argparse, collections as C, concurrent.futures as cf, hashlib, json, os, sys, httpx
sys.path.insert(0, os.path.dirname(__file__))
from jev_client import load_prompt, questions, classify, JEV_PRICE_PER_M_INPUT, DIMS
import run_stage1_jev as S1
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load_set(name):
    if name in ("stage1_6_dev", "stage1_7_holdout"):
        f = {"stage1_6_dev": "STAGE1_6_RESEARCH_SET.jsonl", "stage1_7_holdout": "STAGE1_7_HOLDOUT_SET.jsonl"}[name]
        for s in map(json.loads, open(os.path.join(ROOT, f), encoding="utf-8")):
            yield s, {"messages": [{"role": "user", "content": s["prompt"]}]}, s["gold_task_type"], s["gold_execution_mode"], False
    else:
        sets = {json.loads(l)["id"]: json.loads(l) for l in open(os.path.join(ROOT, "STAGE1_CLASSIFICATION_SET.jsonl"), encoding="utf-8")}
        gold = {json.loads(l)["id"]: json.loads(l) for l in open(os.path.join(ROOT, "GOLD_V2.jsonl"), encoding="utf-8")}
        ok = [json.loads(l)["id"] for l in open(os.path.join(ROOT, "STAGE1_JEV_RESULTS.jsonl"), encoding="utf-8") if json.loads(l)["status"] == "ok"]
        fr = S1.first_requests()
        for i in ok:
            s, g = sets[i], gold[i]
            yield s, S1.build_state(s, fr), g["gold_task_type_v2"], g["gold_execution_mode_v2"], g["exclude_from_task_type_accuracy"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prompt", required=True); ap.add_argument("--set", required=True); ap.add_argument("--out", required=True)
    a = ap.parse_args()
    key = open("/root/.jev_key").read().strip()
    qdef = questions(*load_prompt(a.prompt)); phash = hashlib.sha256(open(a.prompt, "rb").read()).hexdigest()
    items = list(load_set(a.set))
    client = httpx.Client(limits=httpx.Limits(max_connections=4))

    def one(it):
        s, st, gt, gm, excl = it
        rec = {"id": s["id"], "benchmark": s["benchmark"], "benchmark_subtype": s.get("benchmark_subtype"),
               "gold_task_type": gt, "gold_execution_mode": gm, "exclude_from_task_type_accuracy": excl,
               "prompt_file": os.path.relpath(a.prompt, ROOT), "prompt_sha256": phash}
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
    with open(a.out, "w", encoding="utf-8") as f:
        for r in res:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    ok = [r for r in res if r["status"] == "ok"]; tt = [r for r in ok if not r["exclude_from_task_type_accuracy"]]
    print(f"{a.set} with {os.path.basename(a.prompt)}: {len(ok)}/{len(res)} ok | task_type {sum(r['jev_task_type'] == r['gold_task_type'] for r in tt)}/{len(tt)}"
          f" | mode {sum(r['jev_execution_mode'] == r['gold_execution_mode'] for r in ok)}/{len(ok)}")
    for g in sorted({r["gold_task_type"] for r in tt}):
        x = [r for r in tt if r["gold_task_type"] == g]
        print(f"   {g:20} {sum(r['jev_task_type'] == g for r in x):3}/{len(x):3}  wrong-> {dict(C.Counter(r['jev_task_type'] for r in x if r['jev_task_type'] != g))}")
    print(f"   jev calls {len(res)} in_tok {sum(r.get('jev_input_tokens') or 0 for r in ok)} out_tok {sum(r.get('output_tokens') or 0 for r in ok)} cost ${sum(r.get('jev_cost_usd') or 0 for r in ok):.5f}")


if __name__ == "__main__":
    main()
