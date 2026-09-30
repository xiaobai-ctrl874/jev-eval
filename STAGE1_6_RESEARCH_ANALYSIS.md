# Stage 1.6：general_qa 与 research_analysis（2026-09-30）

只处理这一对类别。Prompt V2 冻结不变；没有运行任何候选模型。

## 判断规则（按认知操作，不看材料长短）

| 类别 | 核心操作 |
|---|---|
| general_qa | 查找、识别、定位、核对、解释一个确定的答案；即使答案藏在长文档、多篇文章或大表格里 |
| research_analysis | 综合、比较、汇总、推断、评估、分析趋势或原因，从多条信息得出新的结论 |

不考虑材料长度、文档数量和 benchmark 名称。"根据材料，下列哪个说法正确 / 错误"这类逐条核对的选择题归 general_qa。

所有 gold 在调用 Jev 之前写入并提交（仓库 `11f4775`），之后未改。

## 1. 重审 30 道 LongBench

文件：`STAGE1_6_LONGBENCH_GOLD_REVIEW.jsonl`（每题有判断理由和把握程度，只根据问题和选项判断）。

| 结果 | 题数 |
|---|---|
| 仍为 research_analysis | 20（把握高 10、中 3、低 7） |
| 改为 general_qa | 10（把握中 8、低 2） |

把握低的 7 道 research_analysis 主要是结构化数据查询类（按条件筛选、统计后比较），也可以看作查询或数学。

**用新 gold 重新计分**（使用已有的 Jev 结果，没有新调用）：

| 输入方式 | 原 gold | 新 gold | 新 gold，排除低把握题 |
|---|---|---|---|
| 完整输入（5 道未超长的题） | 1 / 5 | 2 / 5 | — |
| 超长：只给问题 | 14 / 25 = 56% | 15 / 25 = 60% | 13 / 19 = 68% |
| 超长：开头 / 中间 / 结尾采样 | 13 / 25 = 52% | 17 / 25 = 68% | 15 / 19 = 79% |
| 超长：五段采样 | 14 / 25 = 56% | 18 / 25 = 72% | 15 / 19 = 79% |

gold 修正后，采样视图的效果明显好于只给问题，但仍在"需谨慎"的区间。

## 2. 新的纯 research_analysis 考卷

文件：`STAGE1_6_RESEARCH_SET.jsonl`，结果 `STAGE1_6_JEV_RESULTS.jsonl`。全部完整输入，最大约 3,600 token。

| 来源 | 题数 | 内容 |
|---|---|---|
| TableBench 数据分析 | 22 | 因果分析 6、影响因素分析 6、描述与洞察 6、异常识别 4（按官方子类选题，固定种子，逐题确认） |
| WritingBench | 8 | 根据请求中给出的数据写分析报告（客户流失、客服使用、5G 投资回报、营收结构、两家银行对比、格力年报、茅台五年数据、半导体销售） |
| 对照：TableBench 查表核对 | 6 | gold 为 general_qa |

TableBench 的输入格式是"JSON 表格 + 问题"，由我们拼出，不是 TableBench 官方的完整提示模板。

## 3. 结果

| 组 | 正确 | Jev 的判断 |
|---|---|---|
| research_analysis 30 题 | **10 / 30 = 33%** | research_analysis 10、general_qa 9、reasoning_planning 8、writing_language 2、math 1 |
| general_qa 对照 6 题 | 6 / 6 | 全部 general_qa |

| 子类 | 正确 | 主要判为 |
|---|---|---|
| WritingBench 财报分析 | 4 / 4 | — |
| WritingBench 投资分析 | 1 / 1 | — |
| WritingBench 用户研究 | 1 / 2 | writing_language |
| WritingBench 市场分析 | 0 / 1 | writing_language |
| TableBench 描述与洞察 | 0 / 6 | general_qa（全部） |
| TableBench 因果分析 | 2 / 6 | reasoning_planning |
| TableBench 影响因素分析 | 1 / 6 | general_qa、reasoning_planning、math |
| TableBench 异常识别 | 1 / 4 | reasoning_planning、general_qa |

execution_mode 36 / 36 为 direct（正确）。capability_need：30 standard、6 strong。

## 4. 结论

1. **按预设的判断规则，这是 Prompt 问题，不只是 gold 问题**：真正纯的 research_analysis 题 Jev 只判对 33%，远低于其他类别（95% 以上）。
2. 错误有两种模式：
   - 针对表格的"描述、洞察"类问题被判为 general_qa，Jev 把"看表回答"都当成问答。
   - "因果、影响、异常"类问题被判为 reasoning_planning，Jev 把"推断原因"当成逻辑推理。
3. 明确写成"分析报告"的请求识别得好（财报分析 4/4），说明 Jev 目前主要靠"analysis report"这类字面线索识别 research_analysis。
4. 反方向没有问题：查表核对事实的对照题 6/6 正确，说明 general_qa 的定义本身不会把查找题吸走。
5. LongBench 的 gold 确实有一部分定错了（30 题中 10 题应为 general_qa），修正后超长采样视图的准确率从 52–56% 升到 68–72%。

## 5. 建议（需要人工决定）

按 Stage 1.6 的决策规则，下一步应出 **Prompt V3**，只改 research_analysis 与 general_qa、reasoning_planning 的边界：

- research_analysis 的描述改为按认知操作定义：综合、比较、汇总、推断趋势 / 原因 / 影响、从数据得出结论，并说明"材料可以是给定的文档、表格或数据"。
- general_qa 写明：查找、核对、解释一个确定答案，即使在给定材料中查找。
- reasoning_planning 写明：不包括"从数据推断原因或影响"，这类属于 research_analysis。

V3 的验证方式：用这次的 36 题作为调参集；另行准备一批同类新题作为留出集（例如 TableBench 其余数据分析题、LongBench 未用过的题），避免对这 36 题过拟合。改完后还要在 Stage 1 的 205 题上复测，确认其他类别没有退步。

## Jev 用量

| 项目 | 调用 | 输入 tokens | 输出 tokens | 费用 |
|---|---|---|---|---|
| 新考卷 36 题 | 36 | 83,892 | 5,374 | $0.0035 |
| LongBench 重新计分 | 0 | — | — | $0 |

费用按输入 $0.042 / 百万 token 计算，输出单价未公开未计入。
