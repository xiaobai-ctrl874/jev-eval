"""Stage 1.6: general_qa vs research_analysis.
1) Re-reviewed gold for the 30 LongBench v2 items (cognitive-operation rule, judged on question + choices only).
2) New clean research_analysis set (<30K, full input) + general_qa-over-material controls, gold fixed here BEFORE any Jev call.
Rule: general_qa = retrieve / identify / locate / verify / explain a definite answer, even inside long or multiple materials.
      research_analysis = synthesize, compare, aggregate, infer, evaluate, analyse trends or causes, derive a new conclusion
      from several pieces of information. Material length, number of documents and benchmark name are ignored.
Outputs: STAGE1_6_LONGBENCH_GOLD_REVIEW.jsonl, STAGE1_6_RESEARCH_SET.jsonl"""
import json, os, random
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "raw")
SEED = 20260929

LB = {  # task_id: (gold, confidence, reason)
 "66ec17e4821e116aacb1a6a7": ("research_analysis", "medium", "比较两套规则手册在洗售监管上的具体程度和侧重"),
 "66ed2c87821e116aacb1f149": ("research_analysis", "low", "判断能否从表 1 的数据推出收入与受霸凌的关系，属于数据推断；只涉及一张表"),
 "66ed364d821e116aacb1f47e": ("general_qa", "medium", "找出具有某项建模特点的那篇文章，属于定位"),
 "66f24538821e116aacb2865e": ("research_analysis", "high", "比较两种话语分析方法对'权力'的不同理解"),
 "66f2a7a9821e116aacb2a721": ("research_analysis", "low", "对比两个模型的能力，找出一方能做而另一方不能做的任务"),
 "66f2ad2b821e116aacb2ac0f": ("general_qa", "medium", "核对哪一项不属于论文列出的改进，属于逐条核对"),
 "66f2b5ec821e116aacb2b1ec": ("research_analysis", "low", "按条件筛选并比较同一艺人的专辑评分，属于多记录聚合比较；也可视为条件查询"),
 "66f3a311821e116aacb2de19": ("research_analysis", "low", "先统计事件类型出现次数，再在其中比较收入，属于多步聚合；也可视为结构化查询"),
 "66f3ac0b821e116aacb2e203": ("research_analysis", "low", "对多家公司计算资产负债比并比较，属于聚合计算；也可视为 math"),
 "66f3c1c3821e116aacb2eaf6": ("research_analysis", "high", "比较两个部门在打造精品案件上的侧重差异"),
 "66f3cca6821e116aacb2ef7c": ("research_analysis", "high", "比较两份政策文件平衡经济与环境的根本差异及其影响"),
 "66f3e473821e116aacb2fa73": ("general_qa", "medium", "根据辩论文本核对哪个说法正确，属于逐条核对事实"),
 "66f3f46f821e116aacb2ff5d": ("research_analysis", "high", "比较两份法规的法律责任设计并推断其取舍"),
 "66f3fb15821e116aacb303dc": ("general_qa", "medium", "根据论文核对哪些陈述错误，属于逐条核对"),
 "66f40b9c821e116aacb30a99": ("general_qa", "medium", "根据两份财报核对哪个说法不对，属于逐条核对"),
 "66f43414821e116aacb310a1": ("research_analysis", "low", "比较两家公司的共同点"),
 "66f53ab2821e116aacb33299": ("research_analysis", "medium", "汇总两家公司两年的收入结构，计算手机收入占比差异并比较"),
 "66f8c6b4bb02136c067c4480": ("research_analysis", "medium", "从多份报告汇总三个时段的伤亡数据，折算为每日并比较"),
 "66f95126bb02136c067c5070": ("general_qa", "medium", "核对哪一项不是论文相对另一篇的改进，属于逐条核对"),
 "66fa0d88bb02136c067c5a8a": ("research_analysis", "low", "结合材料评估哪种综合政策最合适；也可视为 reasoning_planning"),
 "66fa415cbb02136c067c671c": ("research_analysis", "high", "比较两部住房法规在环境问题上的最主要差异"),
 "66faa8efbb02136c067c7357": ("general_qa", "medium", "核对两份新闻稿中报道了哪些研发进展，属于逐条核对"),
 "66fb5f73bb02136c067c7ae7": ("general_qa", "low", "选项是可逐条核对的事实陈述；题目虽问'影响重大'，主要操作仍是核对"),
 "66fc05b6bb02136c067c88e4": ("research_analysis", "high", "综合两篇论文的发现，判断哪个结论最符合"),
 "66fcf2f2bb02136c067c9169": ("general_qa", "low", "判断哪个结论最可靠，实为逐条核对各选项的事实"),
 "67009bd8bb02136c067caba9": ("research_analysis", "high", "综合两国 IMF 报告推断对媒体报道的含义"),
 "67039cfabb02136c067cd04e": ("research_analysis", "high", "从数据归纳音乐类型的演变趋势及其与消费多样性的关系"),
 "6703a0ecbb02136c067cd11b": ("research_analysis", "high", "根据报告的年份和主题判断哪种假设最有依据"),
 "6704e10fbb02136c067ce1a0": ("research_analysis", "high", "比较两部海关法的处罚设计并推断其取舍"),
 "6704fe26bb02136c067ce670": ("general_qa", "medium", "根据两年报告核对各国禁毒情况的说法，属于逐条核对"),
}

WB = {  # WritingBench index: reason (analysis of data supplied in the request)
 56: "根据给定的客户流失数据分析原因", 58: "根据给定的客服使用数据写体验分析", 69: "根据四年年报数据分析 5G 投资回报",
 70: "分析三年营收结构的变化", 71: "对比两家银行五年理财产品收入", 72: "分析格力三年年报数据",
 91: "根据茅台五年财务数据做投资分析", 103: "根据半导体销售数据做市场分析",
}
TB_RESEARCH = {"CausalAnalysis": 6, "ImpactAnalysis": 6, "DescriptiveAnalysis": 6, "AnomalyDetection": 4}
TB_CONTROL = {"MatchBased": 6}


def tb_prompt(r):
    return ("Read the table below in JSON format:\n[TABLE]\n" + json.dumps(r["table"], ensure_ascii=False) +
            "\n\nQuestion: " + r["question"])


def main():
    sets = {json.loads(l)["id"]: json.loads(l) for l in open(os.path.join(ROOT, "STAGE1_CLASSIFICATION_SET.jsonl"), encoding="utf-8")}
    with open(os.path.join(ROOT, "STAGE1_6_LONGBENCH_GOLD_REVIEW.jsonl"), "w", encoding="utf-8") as f:
        for s in sorted((s for s in sets.values() if s["benchmark"] == "LongBench v2"), key=lambda s: s["id"]):
            g, conf, why = LB[s["task_id"]]
            f.write(json.dumps({"id": s["id"], "task_id": s["task_id"], "previous_gold": s["expected_task_type"],
                                "gold_stage1_6": g, "confidence": conf, "reason": why,
                                "judged_on": "question and choices only"}, ensure_ascii=False) + "\n")
    rows = [json.loads(l) for l in open(os.path.join(RAW, "tablebench", "TableBench.jsonl"), encoding="utf-8")]
    out = []
    for group, spec, gold in (("research", TB_RESEARCH, "research_analysis"), ("control", TB_CONTROL, "general_qa")):
        for sub, n in spec.items():
            pool = sorted((r for r in rows if r["qsubtype"] == sub), key=lambda r: r["id"])
            random.Random(SEED).shuffle(pool)
            for r in pool[:n]:
                out.append({"id": f"tablebench:{r['id']}", "benchmark": "TableBench", "task_id": r["id"], "group": group,
                            "benchmark_subtype": f"{r['qtype']}/{sub}", "prompt": tb_prompt(r), "gold_task_type": gold,
                            "gold_execution_mode": "direct", "label_source": "rule_mapping+item_check",
                            "reason": "按官方子类选题并逐题确认：" + ("需要综合多条数据得出因果、影响、趋势或异常的结论" if group == "research" else "只需在表中查找并核对一个事实")})
    wb = {json.loads(l)["index"]: json.loads(l) for l in open(os.path.join(RAW, "writingbench", "benchmark_all.jsonl"), encoding="utf-8")}
    for i, why in WB.items():
        r = wb[i]
        out.append({"id": f"writingbench:{i}", "benchmark": "WritingBench", "task_id": str(i), "group": "research",
                    "benchmark_subtype": f"{r['domain1']}/{r['domain2']}", "prompt": r["query"], "gold_task_type": "research_analysis",
                    "gold_execution_mode": "direct", "label_source": "item_judgement", "label_confidence": "medium",
                    "reason": why + "；产出是分析报告，与 writing_language 有交叉，按核心认知操作归 research_analysis"})
    with open(os.path.join(ROOT, "STAGE1_6_RESEARCH_SET.jsonl"), "w", encoding="utf-8") as f:
        for o in out:
            f.write(json.dumps(o, ensure_ascii=False) + "\n")
    print(len(out), "items;", sum(o["group"] == "research" for o in out), "research,", sum(o["group"] == "control" for o in out), "control")


if __name__ == "__main__":
    main()
