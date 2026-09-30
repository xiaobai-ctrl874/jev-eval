"""Test the Jev routing view (scripts/routing_view.py) directly against Jev with frozen Prompt V3. No gateway.
Groups:
 short     : the 205 Stage 1 tasks (all < 30K) -> expect routing_mode=full, same classification as V3 regression
 long_agentic : 10 DeepSWE first requests + ~100K tokens of repository source attached in the user message
 long_research: the 25 LongBench overflow tasks -> compact_view with BM25 retrieval
 many_tools   : the 30 AutomationBench tasks with the full 549-tool catalog -> tools aggregated by category
Output: JEV_ROUTING_VIEW_RESULTS.jsonl (+ per-group summary printed)."""
import argparse, concurrent.futures as cf, glob, json, os, sys, httpx
sys.path.insert(0, os.path.dirname(__file__))
from jev_client import load_prompt, questions, classify, JEV_PRICE_PER_M_INPUT, DIMS
from routing_view import build_routing_view, estimate_tokens
import run_stage1_jev as S1

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROMPT = os.path.join(ROOT, "prompts", "jev_prompt_v3.json")


def repo_context(target=100_000):
    """Deterministic ~target-token blob of real source files (engy-core), as a repository snapshot would be attached."""
    parts, total = [], 0
    for f in sorted(glob.glob("/root/engy-core-git/engy/**/*.py", recursive=True)):
        body = open(f, encoding="utf-8").read()
        piece = f"### file: {os.path.relpath(f, '/root/engy-core-git')}\n{body}\n"
        parts.append(piece); total += estimate_tokens(piece)
        if total >= target:
            break
    return "".join(parts)


def cases(groups):
    sets = {json.loads(l)["id"]: json.loads(l) for l in open(os.path.join(ROOT, "STAGE1_CLASSIFICATION_SET.jsonl"), encoding="utf-8")}
    gold2 = {json.loads(l)["id"]: json.loads(l) for l in open(os.path.join(ROOT, "GOLD_V2.jsonl"), encoding="utf-8")}
    gold6 = {json.loads(l)["id"]: json.loads(l) for l in open(os.path.join(ROOT, "STAGE1_6_LONGBENCH_GOLD_REVIEW.jsonl"), encoding="utf-8")}
    fr = S1.first_requests()
    tools = json.load(open(os.path.join(ROOT, "stage1_5", "ab_tool_schemas.json")))
    ok_ids = [json.loads(l)["id"] for l in open(os.path.join(ROOT, "STAGE1_JEV_RESULTS.jsonl"), encoding="utf-8") if json.loads(l)["status"] == "ok"]
    ab_first = {f"{r['domain']}:{r['example_id']}": r for r in map(json.loads, open(os.path.join(ROOT, "raw/automationbench/first_requests_api.jsonl")))}
    if "short" in groups:
        for i in ok_ids:
            s, g = sets[i], gold2[i]
            st = S1.build_state(s, fr)
            t = tools["api"] if s["benchmark"] == "AutomationBench" else st.get("tools")
            gt = gold6[i]["gold_stage1_6"] if i in gold6 else g["gold_task_type_v2"]
            yield "short", i, s["benchmark"], st["messages"], t, gt, g["gold_execution_mode_v2"], g["exclude_from_task_type_accuracy"]
    if "long_agentic" in groups:
        repo = repo_context()
        ds = sorted((s for s in sets.values() if s["benchmark"] == "DeepSWE"), key=lambda s: s["id"])[:10]
        for s in ds:
            req = fr[("DeepSWE", s["task_id"])]
            msgs = [dict(m) for m in req["messages"]]
            u = next(k for k in range(len(msgs) - 1, -1, -1) if msgs[k]["role"] == "user")
            msgs[u] = {"role": "user", "content": msgs[u]["content"] + "\n\n<repository_context>\n" + repo + "\n</repository_context>"}
            yield "long_agentic", s["id"] + "+repo", "DeepSWE", msgs, req["tools"], "coding", "agentic", False
    if "long_research" in groups:
        for i in (json.loads(l)["id"] for l in open(os.path.join(ROOT, "STRUCTURED_OVERFLOW_INPUTS.jsonl"), encoding="utf-8")):
            s = sets[i]
            yield "long_research", i, "LongBench v2", [{"role": "user", "content": s["prompt"]}], None, gold6[i]["gold_stage1_6"], "direct", False
    if "many_tools" in groups:
        for s in sorted((s for s in sets.values() if s["benchmark"] == "AutomationBench"), key=lambda s: s["id"]):
            yield "many_tools", s["id"] + "+549tools", "AutomationBench", ab_first[s["task_id"]]["messages"], tools["limited_zapier"], \
                gold2[s["id"]]["gold_task_type_v2"], "agentic", False


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--groups", default="short,long_agentic,long_research,many_tools")
    a = ap.parse_args(); groups = a.groups.split(",")
    key = open("/root/.jev_key").read().strip()
    qdef = questions(*load_prompt(PROMPT)); ptok = estimate_tokens(qdef)
    client = httpx.Client(limits=httpx.Limits(max_connections=4))
    gold6 = {json.loads(l)["id"]: json.loads(l) for l in open(os.path.join(ROOT, "STAGE1_6_LONGBENCH_GOLD_REVIEW.jsonl"), encoding="utf-8")}

    def one(c):
        grp, i, bench, msgs, tools, gt, gm, excl = c
        before = json.dumps([msgs, tools], sort_keys=True)
        state, info = build_routing_view(msgs, tools, prompt_tokens=ptok)
        assert json.dumps([msgs, tools], sort_keys=True) == before, "routing view mutated the original request"
        rec = {"group": grp, "id": i, "benchmark": bench, "gold_task_type": gt, "gold_execution_mode": gm,
               "gold_confidence": (gold6.get(i) or {}).get("confidence"), "exclude_from_task_type_accuracy": excl,
               "original_request_unchanged": True, **info}
        for _ in range(3):
            try:
                status, body, ms, _ = classify(client, key, state, qdef); break
            except Exception as e:
                status, body, ms = None, {"error": repr(e)[:200]}, None
        rec.update({"http_status": status, "jev_latency_ms": ms})
        if status != 200:
            rec.update({"status": "error", "error": json.dumps(body)[:300]}); return rec
        u = body.get("usage") or {}
        rec.update({"status": "ok", "jev_actual_input_tokens": u.get("input_tokens"), "output_tokens": u.get("output_tokens"),
                    "jev_cost_usd": round((u.get("input_tokens") or 0) * JEV_PRICE_PER_M_INPUT / 1e6, 8)})
        for d in DIMS:
            x = (body.get("answers") or {}).get(d) or {}
            rec[f"jev_{d}"] = x.get("choice"); rec[f"jev_{d}_confidence"] = x.get("confidence"); rec[f"jev_{d}_probabilities"] = x.get("probabilities")
        return rec

    with cf.ThreadPoolExecutor(4) as ex:
        res = list(ex.map(one, cases(groups)))
    out = os.path.join(ROOT, "JEV_ROUTING_VIEW_RESULTS.jsonl")
    prev = [json.loads(l) for l in open(out, encoding="utf-8")] if os.path.exists(out) else []
    keep = [r for r in prev if r["group"] not in groups]
    with open(out, "w", encoding="utf-8") as f:
        for r in keep + res:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    for g in groups:
        x = [r for r in res if r["group"] == g and r["status"] == "ok"]; tt = [r for r in x if not r["exclude_from_task_type_accuracy"]]
        toks = sorted(r["jev_actual_input_tokens"] for r in x)
        print(f"{g}: {len(x)} ok | task {sum(r['jev_task_type'] == r['gold_task_type'] for r in tt)}/{len(tt)} | mode {sum(r['jev_execution_mode'] == r['gold_execution_mode'] for r in x)}/{len(x)}"
              f" | modes {dict((m, sum(r['routing_mode'] == m for r in x)) for m in ('full', 'compact_view'))} | jev tok med {toks[len(toks)//2] if toks else None} max {toks[-1] if toks else None}"
              f" | calls {len(x)} in {sum(toks)} out {sum(r['output_tokens'] for r in x)} cost ${sum(r['jev_cost_usd'] for r in x):.5f}")


if __name__ == "__main__":
    main()
