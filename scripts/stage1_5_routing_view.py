"""Stage 1.5 experiment B: long-context routing view for the 25 LongBench overflow tasks (Prompt V2 frozen).
Arm B (representative sampling): full question/instruction + input metadata + three deterministic samples of the
material (head / middle / tail, ~2K estimated tokens each). No benchmark name, no category labels.
Arm C (multi-slice, 5 positions) is built only with --arm C.
The model that would serve the request still receives the complete original input; this is only what Jev sees.
Output: stage1_5/routing_view_<arm>_results.jsonl"""
import argparse, concurrent.futures as cf, json, os, sys, httpx
sys.path.insert(0, os.path.dirname(__file__))
from jev_client import load_prompt, questions, classify, JEV_PRICE_PER_M_INPUT, DIMS
from jev_token_estimate import estimate_tokens

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OPEN, CLOSE = "<text>", "</text>"


def split(prompt):
    """Official LongBench v2 0-shot template: <instruction> <text>CONTEXT</text> <question+choices+format>."""
    a, b = prompt.index(OPEN), prompt.rindex(CLOSE)
    return prompt[:a].strip(), prompt[a + len(OPEN):b], prompt[b + len(CLOSE):].strip()


def tok(s):
    return estimate_tokens(s, 0)


def take(text, start, budget):
    """Deterministic slice starting at char `start` whose estimated size is ~budget tokens."""
    lo, hi = start, len(text)
    while hi - lo > 64:                                  # binary search on end position
        mid = (lo + hi) // 2
        if tok(text[start:mid]) <= budget:
            lo = mid
        else:
            hi = mid
    return text[start:lo]


def samples(ctx, positions, budget):
    out = []
    for p in positions:
        probe = take(ctx, 0, budget)                     # char length of one budget-sized slice
        width = len(probe)
        s = int(p * max(0, len(ctx) - width))
        out.append((p, take(ctx, s, budget)))
    return out


def view(prompt, arm):
    head_instr, ctx, question = split(prompt)
    positions, budget = ((0.0, 0.5, 1.0), 2000) if arm == "B" else ((0.0, 0.25, 0.5, 0.75, 1.0), 1300)
    names = {0.0: "BEGINNING", 0.25: "25% POSITION", 0.5: "MIDDLE", 0.75: "75% POSITION", 1.0: "END"}
    parts = ["[ROUTING TASK]", head_instr, "", question, "", "[INPUT METADATA]",
             f"original_input_tokens: {tok(prompt)}", "modality: text", "attachments_present: false",
             "note: the material is too long to show in full; below are excerpts taken at fixed positions.", "",
             "[REPRESENTATIVE CONTEXT]"]
    for p, t in samples(ctx, positions, budget):
        parts += [f"--- SAMPLE FROM {names[p]} OF THE MATERIAL ---", t.strip(), f"--- END OF SAMPLE ---", ""]
    return "\n".join(parts)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--arm", choices=["A", "B", "C"], required=True)
    ap.add_argument("--prompt", default=os.path.join(ROOT, "prompts", "jev_prompt_v2.json")); ap.add_argument("--out", default=None)
    a = ap.parse_args()
    key = open("/root/.jev_key").read().strip()
    qdef = questions(*load_prompt(a.prompt))
    so = {json.loads(l)["id"]: json.loads(l)["state"] for l in open(os.path.join(ROOT, "STRUCTURED_OVERFLOW_INPUTS.jsonl"), encoding="utf-8")}
    sets = {json.loads(l)["id"]: json.loads(l) for l in open(os.path.join(ROOT, "STAGE1_CLASSIFICATION_SET.jsonl"), encoding="utf-8")}
    gold = {json.loads(l)["id"]: json.loads(l) for l in open(os.path.join(ROOT, "GOLD_V2.jsonl"), encoding="utf-8")}
    ids = [json.loads(l)["id"] for l in open(os.path.join(ROOT, "STRUCTURED_OVERFLOW_INPUTS.jsonl"), encoding="utf-8")]
    client = httpx.Client(limits=httpx.Limits(max_connections=4))

    def one(i):
        s, g = sets[i], gold[i]
        if a.arm == "A":
            st = so[i]; v = st["messages"][0]["content"]
        else:
            v = view(s["prompt"], a.arm)
            st = {"messages": [{"role": "user", "content": v}]}
        rec = {"id": i, "task_id": s["task_id"], "arm": a.arm, "gold_task_type": g["gold_task_type_v2"],
               "gold_execution_mode": g["gold_execution_mode_v2"], "official_difficulty": s["official_difficulty"],
               "original_input_tokens_est": tok(s["prompt"]), "routing_view_tokens_est": estimate_tokens(st, 1580),
               "routing_view_chars": len(v)}
        for attempt in range(3):
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
            rec[f"jev_{d}"] = x.get("choice"); rec[f"jev_{d}_confidence"] = x.get("confidence")
            rec[f"jev_{d}_probabilities"] = x.get("probabilities")
        return rec

    with cf.ThreadPoolExecutor(4) as ex:
        res = list(ex.map(one, ids))
    out = a.out or os.path.join(ROOT, "stage1_5", f"routing_view_{a.arm}_results.jsonl")
    with open(out, "w", encoding="utf-8") as f:
        for r in res:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    ok = [r for r in res if r["status"] == "ok"]
    print(f"arm {a.arm}: {len(ok)}/{len(res)} ok; task_type {sum(r['jev_task_type'] == r['gold_task_type'] for r in ok)}/{len(ok)}")


if __name__ == "__main__":
    main()
