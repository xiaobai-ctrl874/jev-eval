"""Stage 1 gold review material: STAGE1_GOLD_REVIEW_REQUIRED.csv + GOLD_REVIEW_REQUIRED.md.
Covers the disputed Stage 1 items and the pre-registered 7-class gold for AutomationBench.
Recommendations are written before any V2 run; the human decision column is left empty."""
import csv, json, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
S = {json.loads(l)["id"]: json.loads(l) for l in open(os.path.join(ROOT, "STAGE1_CLASSIFICATION_SET.jsonl"), encoding="utf-8")}
R = {json.loads(l)["id"]: json.loads(l) for l in open(os.path.join(ROOT, "STAGE1_JEV_RESULTS.jsonl"), encoding="utf-8")}

def lb_question(p):
    k = p.rfind("What is the correct answer")
    return p[k:] if k >= 0 else p[-2000:]

SPATIAL_MATH = ("题目是正式的几何对象（正方体、正多边形、平面切割），答案是唯一的形状名或整数，"
                "解题需要几何关系和计数，属于几何或组合几何题")
SPATIAL_RP = ("LiveBench 把它归为 spatial 推理，考的是空间想象而不是公式推导，不需要计算或证明；"
              "按 taxonomy，空间推理属于 reasoning_planning")
ITEMS = [
 ("spatial", "livebench_reasoning:4c6e9d7cd2f5506ef5d07f1545dad8d1ca31bfd74ad3ca3e1a6d34accac62db2", "math",
  "正方体顶点 A、C、G、E 构成什么形状，是标准的立体几何题", SPATIAL_RP),
 ("spatial", "livebench_reasoning:6882b248e31a65f287a7a2ab617b31ebfed771511e730697ceb43f0b5a3dd067", "math",
  "需要用距离和平面位置判断切割面是否碰到正方体或球，属于几何位置关系计算", SPATIAL_RP),
 ("spatial", "livebench_reasoning:a0f4b0be2055ef97c455771f2de3eb3f41c9018603d96c93225be734b70dcdce", "math",
  "正五边形两条对角线切割后的块数，是平面几何计数", SPATIAL_RP),
 ("spatial", "livebench_reasoning:e0df6bab9a48ea72072778dc1f8a804810438529347c88b5028b15045b20a203", "math",
  "切割后三角形的个数，需要识别几何图形", SPATIAL_RP),
 ("spatial", "livebench_reasoning:f8e84ee53942b7e6881fd483a404f6d2c875e816fd79f07cf4181d5d0e3a5b31", "math",
  "带约束的最大块数，是组合几何中的经典极值问题", SPATIAL_RP),
 ("writing", "writingbench:26", "writing_language（低把握）",
  "没有给定任何材料，靠已有知识写一篇总结分析文章；按 taxonomy，research_analysis 要求综合给定材料，所以更接近写作",
  "题目明确要求'分析'和'比较'，现行 Prompt 的 research_analysis 描述里有 'producing research-style analysis'，与 taxonomy 定义不一致"),
 ("writing", "writingbench:425", "有歧义，建议单列不计入准确率",
  "WritingBench 把它归为广告语写作，产出主要是广告语",
  "题目同时要求'具体的推广策划方案'，有明确目标、周期、地区、受众等约束，这部分是 reasoning_planning"),
 ("longbench", "longbench_v2:66ed2c87821e116aacb1f149", "research_analysis（低把握）",
  "需要读懂论文中的表 1 并判断收入与受霸凌程度的关系能否成立，属于表格分析",
  "只涉及一张表，接近查表；Jev 判为 general_qa"),
 ("longbench", "longbench_v2:66f8c6b4bb02136c067c4480", "research_analysis",
  "要从多份人道主义报告里汇总三个时间段的死亡和受伤人数，再按天折算比较，属于多文档数据整合",
  "核心步骤是算术（除以天数、比较），Jev 判为 math"),
 ("longbench", "longbench_v2:66fb5f73bb02136c067c7ae7", "research_analysis",
  "要综合 AbbVie 半年内多篇新闻稿，判断哪些事件对战略和运营影响重大，是典型的多文档综合",
  "Jev 判为 general_qa；选项里的事实可逐条核对，但需要跨文档比对"),
]

AB_RP = {  # pre-registered 7-class gold for the 30 AutomationBench items; default workflow_operation
 "automationbench:marketing:1045": ("research_analysis", "核心是分析内容清单并给出优先级建议，写回或发送只是交付方式；与 workflow_operation 有歧义"),
 "automationbench:hr:5028": ("workflow_operation", "要逐个核对薪资带宽和审批例外，再在 Gmail 里建草稿，评分看流程是否合规；与 writing_language 有歧义"),
}
rows, md = [], []
md += ["# Stage 1 gold 人工复核", "",
       "目的：在写 Prompt V2 之前，先确认争议题的语义 gold，避免 Prompt 过拟合错误的 gold。",
       "建议是在 V2 运行之前写的；请在 `STAGE1_GOLD_REVIEW_REQUIRED.csv` 的 `human_gold` 列填写最终判断。", "",
       "判断标准服务于 Router：如果将来各模型在这类题上的表现更接近数学题，就允许归 math。", ""]
titles = {"spatial": "A. LiveBench spatial / 几何（5 题）", "writing": "B. WritingBench（2 题）", "longbench": "C. LongBench v2 成功题中的错误（3 题）"}
cur = None
for grp, i, rec, why_a, why_b in ITEMS:
    s, r = S[i], R[i]
    if grp != cur:
        md += [f"## {titles[grp]}", ""]; cur = grp
    task = lb_question(s["prompt"]) if grp == "longbench" else s["prompt"]
    extra = f"（完整输入 {len(s['prompt']):,} 字符，这里只列问题和选项；材料开头：{s['prompt'][60:260].strip()} …）" if grp == "longbench" else ""
    label_a, label_b = {"spatial": ("为什么可能属于 math", "为什么可能属于 reasoning_planning"),
                        "writing": ("支持现有 gold（writing_language）", "支持改为其他类别"),
                        "longbench": ("支持 research_analysis", "支持 Jev 的判断")}[grp]
    md += [f"### `{i}`", "", f"- 子类：{s.get('benchmark_subtype')}；官方难度：{s.get('official_difficulty')}",
           f"- 当前 gold：**{s['expected_task_type']}**；Jev V1：**{r['jev_task_type']}**（置信度 {r['jev_task_type_confidence']:.2f}）",
           f"- {label_a}：{why_a}", f"- {label_b}：{why_b}", f"- 建议：**{rec}**", "", "题目全文" + extra + "：", "", "```", task.strip(), "```", ""]
    rows.append([grp, i, s["expected_task_type"], r["jev_task_type"], round(r["jev_task_type_confidence"], 3), why_a, why_b, rec, "", "", task.strip()])

md += ["## D. AutomationBench 在 7 类下的 gold（30 题，V2 运行前登记）", "",
       "Stage 1 里这 30 题按 6 类判断，25 题归不进任何一类。V2 增加 workflow_operation 后，需要事先登记新的 gold。",
       "判断依据：任务的核心目标是不是通过工具读取并改变外部系统状态来完成业务流程。execution_mode 全部是 agentic。", "",
       "| 题目 | 领域 | Stage 1 判断 | 建议 7 类 gold | 说明 |", "|---|---|---|---|---|"]
for i, s in sorted(S.items()):
    if s["benchmark"] != "AutomationBench":
        continue
    g, why = AB_RP.get(i, ("workflow_operation", "读取并更新 CRM、表格、邮件、Slack 等外部系统，按业务规则执行流程"))
    md.append(f"| `{i}` | {s['benchmark_subtype']} | {s['taxonomy_fit']} / {s['expected_task_type']} | **{g}** | {why} |")
    rows.append(["automationbench", i, s["expected_task_type"], R[i]["jev_task_type"], round(R[i]["jev_task_type_confidence"], 3),
                 why, "", g, "", "", s["prompt"].strip()])
md += ["", "## E. 不需要复核的", "",
       "SimpleQA Verified 中 5 道被 Jev V1 判为 agentic 的题，gold 仍为 direct：题目只要求回答一个事实，没有要求操作任何外部环境。", ""]
open(os.path.join(ROOT, "GOLD_REVIEW_REQUIRED.md"), "w", encoding="utf-8").write("\n".join(md))
with open(os.path.join(ROOT, "STAGE1_GOLD_REVIEW_REQUIRED.csv"), "w", encoding="utf-8-sig", newline="") as f:
    w = csv.writer(f)
    w.writerow(["group", "task_id", "current_gold", "jev_v1", "jev_v1_confidence", "reason_for_a", "reason_for_b", "recommended_gold", "human_gold", "human_comment", "full_task"])
    w.writerows(rows)
print(len(rows))
