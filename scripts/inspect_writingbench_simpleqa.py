"""Inspect WritingBench (github X-PLUG/WritingBench benchmark_all.jsonl) and SimpleQA Verified CSV.
Download:
  curl -sSL -o raw/writingbench/benchmark_all.jsonl https://raw.githubusercontent.com/X-PLUG/WritingBench/main/benchmark_query/benchmark_all.jsonl
  curl -sSL -H "Authorization: Bearer $HF_TOKEN" -o raw/simpleqa_verified/simpleqa_verified.csv \
       https://huggingface.co/datasets/google/simpleqa-verified/resolve/main/simpleqa_verified.csv
"""
import collections, csv, json, re, os

BASE = "/root/bench/jev_eval/raw"

# ---- SimpleQA Verified
rows = list(csv.DictReader(open(f"{BASE}/simpleqa_verified/simpleqa_verified.csv")))
print("SimpleQA Verified rows:", len(rows))
print("multi_step x requires_reasoning:",
      collections.Counter((r["multi_step"], r["requires_reasoning"]) for r in rows))

# ---- WritingBench
wb = [json.loads(l) for l in open(f"{BASE}/writingbench/benchmark_all.jsonl")]
print("\nWritingBench rows:", len(wb))
print("lang:", collections.Counter(r["lang"] for r in wb))
d1 = collections.Counter(r["domain1"] for r in wb)
print("domain1:", d1.most_common())
d2 = collections.Counter((r["domain1"], r["domain2"]) for r in wb)
print("n subdomains:", len(d2))
for (a, b), n in sorted(d2.items()):
    print(f"  {a} | {b}: {n}")

L = [len(r["query"]) for r in wb]
L.sort()
print("query char len: min", L[0], "median", L[len(L)//2], "p90", L[int(.9*len(L))], "max", L[-1])

# Heuristic flag: sub-domain names / query intent suggesting analysis/report on provided materials
ANALYSIS_SUB = re.compile(r"(analy|report|review|assess|evaluat|audit|research|summar|due diligence|case|forecast|feasib|market|investment|financial|legal opinion|judgment|advice|consult|diagnos|data)", re.I)
ANALYSIS_Q = re.compile(r"(分析|研报|研究报告|调研|评估|诊断|尽职调查|可行性|审计|数据|analy[sz]e|analysis|evaluate|assessment|feasibility|due diligence|audit|research report|based on the (following|attached|provided) (data|materials?|documents?))", re.I)
flag_sub = {k for k in d2 if ANALYSIS_SUB.search(k[1])}
print("\nSubdomains whose NAME suggests analysis/research (heuristic, review manually):")
for k in sorted(flag_sub):
    print(f"  {k[0]} | {k[1]}: {d2[k]}")
fq = [r for r in wb if ANALYSIS_Q.search(r["query"][:400]) and len(r["query"]) > 3000]
print("\nItems with analysis keyword in first 400 chars AND query >3000 chars (long provided material):", len(fq))
print(" by domain1:", collections.Counter(r["domain1"] for r in fq).most_common())
long_mat = [r for r in wb if len(r["query"]) > 5000]
print("Items with query >5000 chars (heavy provided material):", len(long_mat))
out = f"{BASE}/writingbench/flagged_analysis_candidates.jsonl"
with open(out, "w") as f:
    for r in fq:
        f.write(json.dumps({"index": r["index"], "domain1": r["domain1"], "domain2": r["domain2"],
                            "lang": r["lang"], "qlen": len(r["query"]), "head": r["query"][:200]},
                           ensure_ascii=False) + "\n")
print("wrote", out)
