"""Stage 1.5 experiment A: tool representation ablation (Full / Compact / No tools), Prompt V2 frozen.
70 fixed tasks: DeepSWE 20 + AutomationBench 30 (agentic) + SimpleQA 10 + LiveCodeBench 10 (direct control,
given the same kind of tool availability as the agentic tasks). Output: stage1_5/tool_ablation_results.jsonl"""
import concurrent.futures as cf, json, os, sys, httpx
sys.path.insert(0, os.path.dirname(__file__))
from jev_client import load_prompt, questions, classify, JEV_PRICE_PER_M_INPUT, DIMS
import run_stage1_jev as S1

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "stage1_5", "tool_ablation_results.jsonl")
AB_TOOLS = json.load(open(os.path.join(ROOT, "stage1_5", "ab_tool_schemas.json")))["api"]
CATEGORY = {"bash": "command_execution", "api_search": "api_discovery", "api_fetch": "api_request",
            "base64_encode": "utility"}


def compact(tools):
    """name + category + first sentence of the tool's own description; no parameters or schema."""
    out = []
    for t in tools:
        f = t["function"]
        desc = (f.get("description") or "").strip().split("\n")[0].split(". ")[0].rstrip(".") + "."
        out.append({"name": f["name"], "category": CATEGORY.get(f["name"], f["name"].split("_")[0]), "description": desc})
    return out


def tasks():
    sets = [json.loads(l) for l in open(os.path.join(ROOT, "STAGE1_CLASSIFICATION_SET.jsonl"), encoding="utf-8")]
    gold = {json.loads(l)["id"]: json.loads(l) for l in open(os.path.join(ROOT, "GOLD_V2.jsonl"), encoding="utf-8")}
    fr = S1.first_requests()
    bash = fr[("DeepSWE", next(s["task_id"] for s in sets if s["benchmark"] == "DeepSWE"))]["tools"]
    rows = []
    pick = lambda b, n: sorted((s for s in sets if s["benchmark"] == b), key=lambda s: s["id"])[:n]
    for s in pick("DeepSWE", 20) + pick("AutomationBench", 30) + pick("SimpleQA Verified", 10) + pick("LiveCodeBench code_generation_lite", 10):
        st = S1.build_state(s, fr)
        if s["benchmark"] == "DeepSWE":
            full_tools = st["tools"]
        elif s["benchmark"] == "AutomationBench":
            full_tools = AB_TOOLS          # real schemas (Stage 1 stored names only)
        else:
            full_tools = bash + AB_TOOLS   # direct control: same kind of environment
        rows.append((s, gold[s["id"]], st["messages"], full_tools))
    return rows


def main():
    key = open("/root/.jev_key").read().strip()
    qdef = questions(*load_prompt(os.path.join(ROOT, "prompts", "jev_prompt_v2.json")))
    client = httpx.Client(limits=httpx.Limits(max_connections=4))
    jobs = []
    for s, g, msgs, tools in tasks():
        for arm, st in (("A_full", {"messages": msgs, "tools": tools}),
                        ("B_compact", {"messages": msgs, "tools": compact(tools)}),
                        ("C_none", {"messages": msgs})):
            jobs.append((s, g, arm, st))

    def one(job):
        s, g, arm, st = job
        rec = {"task_id": s["task_id"], "id": s["id"], "benchmark": s["benchmark"], "tool_arm": arm,
               "gold_task_type": g["gold_task_type_v2"], "gold_execution_mode": g["gold_execution_mode_v2"],
               "role": "agentic" if s["benchmark"] in ("DeepSWE", "AutomationBench") else "direct_control",
               "n_tools": len(st.get("tools") or []), "tools_chars": len(json.dumps(st.get("tools") or [], ensure_ascii=False))}
        for attempt in range(3):
            try:
                status, body, ms, _ = classify(client, key, st, qdef)
                break
            except Exception as e:
                status, body, ms = None, {"error": repr(e)[:200]}, None
        rec.update({"http_status": status, "jev_latency_ms": ms})
        if status != 200:
            rec.update({"status": "error", "error": json.dumps(body)[:300]}); return rec
        u = body.get("usage") or {}
        rec.update({"status": "ok", "routing_input_tokens": u.get("input_tokens"), "output_tokens": u.get("output_tokens"),
                    "jev_cost_usd": round((u.get("input_tokens") or 0) * JEV_PRICE_PER_M_INPUT / 1e6, 8)})
        for d in DIMS:
            x = (body.get("answers") or {}).get(d) or {}
            rec[f"jev_{d}"] = x.get("choice"); rec[f"jev_{d}_confidence"] = x.get("confidence")
            rec[f"jev_{d}_probabilities"] = x.get("probabilities")
        return rec

    with cf.ThreadPoolExecutor(4) as ex:
        res = list(ex.map(one, jobs))
    with open(OUT, "w", encoding="utf-8") as f:
        for r in res:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(sum(r["status"] == "ok" for r in res), "/", len(res), "ok")
    for r in res:
        if r["status"] != "ok":
            print("FAIL", r["id"], r["tool_arm"], r.get("error"))


if __name__ == "__main__":
    main()
