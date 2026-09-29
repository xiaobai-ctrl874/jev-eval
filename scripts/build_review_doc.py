"""Build the human-review document (review/REVIEW_v1.md) and a fill-in sheet (review/review_sheet_v1.csv)."""
import json, csv, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def load(n): return [json.loads(l) for l in open(os.path.join(ROOT, "datasets", n), encoding="utf-8")]
def ex(s, n=400):
    s = " ".join(str(s or "").split())
    return s if len(s) <= n else s[:n] + " …"
cls, bnd, exe, cap = load("jev_classification_eval_v1.jsonl"), load("jev_boundary_eval_v1.jsonl"), load("jev_execution_mode_eval_v1.jsonl"), load("jev_capability_eval_v1.jsonl")
tb = sorted({r["id"]: r for r in exe + cls + cap + bnd if r["benchmark"].startswith("Terminal")}.values(), key=lambda r: r["id"])
plan = [r for r in cls if r["gold_task_type"] == "planning_design"]
lb = [r for r in cls if r["gold_task_type"] == "research_analysis"]
out, sheet = [], []
out.append("# Jev 评测集 v1：人工复核\n")
out.append("每道题给出题面摘录（前 400 字符）和系统建议。请在 `review_sheet_v1.csv` 的 `your_label` 列填写你的判断（同意建议可填 ok），`comment` 列可留言。")
out.append("复核结果只用来确定标准答案，不会参考 Jev 或任何模型的输出。\n")
out.append("| 部分 | 题数 | 要确认什么 |\n|---|---|---|")
out.append(f"| A 易混题 | {len(bnd)} | 标准的 task_type |")
out.append(f"| B Terminal-Bench | {len(tb)} | task_type（agentic 已确定） |")
out.append(f"| C PlanningBench | {len(plan)} | 是\"规划\"还是\"设计\"，以及是否属于 planning_design |")
out.append(f"| D LongBench v2 | {len(lb)} | 是否真的属于 research_analysis |\n")
out.append("## A. 易混题\n")
for i, r in enumerate(sorted(bnd, key=lambda r: (r["pair"], r["id"])), 1):
    out.append(f"### A{i}. `{r['id']}`\n- 易混类别：{r['pair']}\n- 系统建议：**{r['recommended_gold']}**（把握：{r['confidence']}）\n- 为什么易混：{ex(r['why_ambiguous'], 300)}\n- 题面：{ex(r['prompt'])}\n")
    sheet.append(["A", r["id"], r["pair"], r["recommended_gold"], "", ""])
out.append("## B. Terminal-Bench 的 task_type\n")
for i, r in enumerate(tb, 1):
    sug = r.get("gold_task_type") or "（留空，未判断）"
    out.append(f"### B{i}. `{r['id']}`\n- 官方类别：{r.get('official_category')}；官方难度：{r.get('official_difficulty')}\n- 系统建议：**{sug}**\n- 题面：{ex(r['prompt'])}\n")
    sheet.append(["B", r["id"], r.get("official_category"), r.get("gold_task_type") or "", "", ""])
out.append("## C. PlanningBench：规划还是设计\n")
for i, r in enumerate(plan, 1):
    out.append(f"### C{i}. `{r['id']}`\n- 系统建议：**{r.get('sub_category')}**\n- 题面：{ex(r['prompt'])}\n")
    sheet.append(["C", r["id"], "planning vs design", r.get("sub_category"), "", ""])
out.append("## D. LongBench v2：是否属于 research_analysis\n")
out.append("注意：这里给的是问题和选项。实际发给模型的是\"很长的文档 + 问题\"，线上 Jev 只看得到文档开头。\n")
for i, r in enumerate(lb, 1):
    out.append(f"### D{i}. `{r['id']}`\n- 官方类别：{r.get('official_category')}；官方难度：{r.get('official_difficulty')}；长度：{r.get('length')}\n- 系统建议：**research_analysis**\n- 问题：{ex(r['prompt'], 600)}\n")
    sheet.append(["D", r["id"], r.get("official_category"), "research_analysis", "", ""])
open(os.path.join(ROOT, "review", "REVIEW_v1.md"), "w", encoding="utf-8").write("\n".join(out) + "\n")
with open(os.path.join(ROOT, "review", "review_sheet_v1.csv"), "w", encoding="utf-8-sig", newline="") as f:
    w = csv.writer(f); w.writerow(["part", "id", "context", "suggested", "your_label", "comment"]); w.writerows(sheet)
print(len(bnd), len(tb), len(plan), len(lb), len(sheet))
