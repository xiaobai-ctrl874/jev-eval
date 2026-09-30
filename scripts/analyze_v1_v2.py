"""V1 vs V2 analysis. Prints all numbers used in STAGE1_V1_V2_COMPARISON.md."""
import json, collections as C, statistics as st
V2 = [json.loads(l) for l in open("STAGE1_V2_JEV_RESULTS.jsonl")]
SO = [json.loads(l) for l in open("STRUCTURED_OVERFLOW_RESULTS.jsonl")]
T7 = ["general_qa","writing_language","math","reasoning_planning","coding","research_analysis","workflow_operation"]
def acc(rows, pred, gold): n=len(rows); k=sum(r[pred]==r[gold] for r in rows); return k,n
tt = [r for r in V2 if not r["exclude_from_task_type_accuracy"]]
print("== task_type, V2 prompt vs V2 gold (all 205 minus 1 excluded)", acc(tt,"jev_task_type","gold_task_type_v2"))
print("   V1 prompt vs V2 gold (same items)", acc(tt,"v1_task_type","gold_task_type_v2"))
clean=[r for r in tt if r["set"]=="clean"]
print("== clean direct set:", "V2", acc(clean,"jev_task_type","gold_task_type_v2"), "V1", acc(clean,"v1_task_type","gold_task_type_v2"))
s1=[r for r in V2 if r["set"]=="clean"]
print("   V1 vs Stage1 gold (baseline 93.5%)", sum(r["v1_task_type"]==r["stage1_expected_task_type"] for r in s1), len(s1))
print("== per class (V2 gold): class n V2_correct V1_correct | V2 errors")
for t in T7:
    s=[r for r in tt if r["gold_task_type_v2"]==t]
    print(f"   {t:20} {len(s):3} {sum(r['jev_task_type']==t for r in s):3} {sum(r['v1_task_type']==t for r in s):3} | {dict(C.Counter(r['jev_task_type'] for r in s if r['jev_task_type']!=t))}")
print("== subtypes")
for name,f in (("reasoning (LiveBench reasoning)",lambda r:r["benchmark"]=="LiveBench reasoning"),("planning (PlanningBench)",lambda r:r["benchmark"].startswith("PlanningBench")),("AutomationBench",lambda r:r["benchmark"]=="AutomationBench"),("DeepSWE",lambda r:r["benchmark"]=="DeepSWE")):
    s=[r for r in V2 if f(r)]
    print(f"   {name}: n={len(s)} V2 {dict(C.Counter(r['jev_task_type'] for r in s))} | V1 {dict(C.Counter(r['v1_task_type'] for r in s))} | gold {dict(C.Counter(r['gold_task_type_v2'] for r in s))}")
sp=[r for r in V2 if r["benchmark"]=="LiveBench reasoning" and r["gold_task_type_v2"]=="math"]
print("   spatial 5 now gold math:", [(r["v1_task_type"],r["jev_task_type"]) for r in sp])
lr=[r for r in V2 if r["benchmark"]=="LiveBench reasoning" and r["gold_task_type_v2"]!="math"]
print("   other LiveBench reasoning 10:", C.Counter(r["jev_task_type"] for r in lr))
print("== confusion matrix V2 (rows gold, cols pred)")
print("   " + " ".join(f"{t[:6]:>6}" for t in T7))
for g in T7:
    print(f"   {g[:18]:18}" + " ".join(f"{sum(1 for r in tt if r['gold_task_type_v2']==g and r['jev_task_type']==p):6}" for p in T7))
print("== all V2 task_type errors")
for r in tt:
    if r["jev_task_type"]!=r["gold_task_type_v2"]:
        print(f"   {r['id'][:70]:70} gold={r['gold_task_type_v2']} v2={r['jev_task_type']} ({r['jev_task_type_confidence']:.2f}) v1={r['v1_task_type']}")
print("   excluded:", [(r["id"], r["v1_task_type"], r["jev_task_type"]) for r in V2 if r["exclude_from_task_type_accuracy"]])
print("== execution_mode")
for m in ("direct","agentic"):
    s=[r for r in V2 if r["gold_execution_mode_v2"]==m]
    print(f"   {m}: n={len(s)} V2 {sum(r['jev_execution_mode']==m for r in s)} V1 {sum(r['v1_execution_mode']==m for r in s)}")
sq=[r for r in V2 if r["benchmark"]=="SimpleQA Verified"]
print("   SimpleQA V1 agentic ids -> V2:", [(r["id"], r["jev_execution_mode"]) for r in sq if r["v1_execution_mode"]=="agentic"], "V2 agentic total", sum(r["jev_execution_mode"]=="agentic" for r in sq))
print("   V2 mode errors:", [(r["id"], r["gold_execution_mode_v2"], r["jev_execution_mode"]) for r in V2 if r["jev_execution_mode"]!=r["gold_execution_mode_v2"]])
print("== capability_need distribution V2 (V1)")
for b in sorted({r["benchmark"] for r in V2}):
    s=[r for r in V2 if r["benchmark"]==b]
    print(f"   {b:36} V2 {dict(C.Counter(r['jev_capability_need'] for r in s))}  V1 {dict(C.Counter(r['v1_capability_need'] for r in s))}")
def spear(x,y):
    def rk(v):
        o=sorted(range(len(v)),key=lambda i:v[i]); r=[0]*len(v); i=0
        while i<len(v):
            j=i
            while j+1<len(v) and v[o[j+1]]==v[o[i]]: j+=1
            for k in range(i,j+1): r[o[k]]=(i+j)/2+1
            i=j+1
        return r
    a,b=rk(x),rk(y)
    try: return round(st.correlation(a,b),3)
    except Exception: return None
O={"standard":0,"strong":1,"frontier":2}
for b,key in (("LiveCodeBench code_generation_lite",{"easy":0,"medium":1,"hard":2}),("MATH-500",None)):
    s=[r for r in V2 if r["benchmark"]==b]
    od=[(key[r["official_difficulty"]] if key else int(str(r["official_difficulty"]).split("_")[-1])) for r in s]
    for tag,f in (("V2","jev_capability_need"),("V1","v1_capability_need")):
        print(f"   {b} {tag}: table {sorted(C.Counter((d,r[f]) for d,r in zip(od,s)).items())} spearman {spear(od,[O[r[f]] for r in s])}")
print("== routing mode / cost")
print("   routing_mode", C.Counter(r["routing_mode"] for r in V2))
tok=sorted(r["input_tokens"] for r in V2); lat=sorted(r["jev_latency_ms"] for r in V2)
print(f"   V2 tokens p50 {tok[len(tok)//2]} p90 {tok[int(.9*len(tok))]} max {tok[-1]} | latency p50 {lat[len(lat)//2]} p90 {lat[int(.9*len(lat))]} max {lat[-1]} | cost {sum(r['jev_cost_usd'] for r in V2):.4f}")
print(f"   V1 tokens p50 {sorted(r['v1_input_tokens'] for r in V2)[len(V2)//2]}")
print("   max estimate/actual among full:", max(r["input_tokens"]/r["estimated_input_tokens"] for r in V2))
print("== structured overflow")
print("   task_type", acc(SO,"jev_task_type","gold_task_type_v2"), C.Counter(r["jev_task_type"] for r in SO))
print("   mode", C.Counter(r["jev_execution_mode"] for r in SO), "cap", C.Counter(r["jev_capability_need"] for r in SO))
print("   tokens max", max(r["input_tokens"] for r in SO), "cost", round(sum(r["jev_cost_usd"] for r in SO),5))
for r in SO:
    if r["jev_task_type"]!=r["gold_task_type_v2"]: print("   wrong", r["id"], r["benchmark_subtype"], r["jev_task_type"], round(r["jev_task_type_confidence"],2))
