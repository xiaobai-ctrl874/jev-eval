# Stage 1.7：Prompt V3（2026-09-30）

目标：修正 general_qa、research_analysis、reasoning_planning 三者的边界，其他类别和维度不动。没有运行任何候选模型。

## 1. 过程与防过拟合措施

| 步骤 | 做法 | 仓库提交 |
|---|---|---|
| 1 | 先建留出集并提交，再起草 V3 | `e4ea7c5` |
| 2 | 只用 dev（Stage 1.6 的 36 题）起草和评估；第一版就达到 35/36，不再迭代 | — |
| 3 | 冻结 V3，然后才第一次运行留出集 | `7df24f3` |
| 4 | 留出集、205 题回归、25 道超长题三种视图 | 本报告 |

留出集（`STAGE1_7_HOLDOUT_SET.jsonl`，50 题）与 Stage 1 考卷和 dev 完全不重叠：research_analysis 30（TableBench 数据分析 22 + WritingBench 带数据的分析题 8）、general_qa 10（TableBench 查表 5 + SimpleQA 5）、reasoning_planning 10（LiveBench 推理的 zebra 与 web_of_lies 5 + PlanningBench 5）。

## 2. V3 改了什么

文件 `prompts/jev_prompt_v3.json`（sha256 `442be64b…3bbe6e`，只读）。与 V2 相比只改 task_type：

| 位置 | 改动 |
|---|---|
| 总说明 | 新增五条区分规则：查找 / 核对 / 解释确定答案 → general_qa；综合、比较、汇总、解读给定材料并推出趋势、原因、影响、异常、结论 → research_analysis；主要靠逻辑、规则、约束、规划、空间推理 → reasoning_planning；不能因为输入长、含文档或表格、出现 "analysis" 就判 research_analysis；不能因为问"为什么"就判 reasoning_planning，基于给定数据的推断归 research_analysis |
| general_qa | 补充"在给定材料中查找、核对或解释确定答案，即使材料很长" |
| research_analysis | 改为"基于证据的分析"：综合、比较、汇总、解读文档、表格、数据或多来源，得出不在任何单条信息中直接写明的结论 |
| reasoning_planning | 末尾补一句：基于给定数据的因果、影响、趋势推断属于 research_analysis |

其余 4 个类别、execution_mode、capability_need 与 V2 逐字相同。V3 的 Prompt 比 V2 长约 1,400 字符（约 350 token）。

## 3. 结果

| 考卷 | V2 | V3 |
|---|---|---|
| dev（36 题） | 16 / 36 | 35 / 36 |
| **留出集（50 题）** | 28 / 50 | **50 / 50** |
| 其中 research_analysis | 8 / 30 | **30 / 30** |
| 其中 general_qa | 10 / 10 | 10 / 10 |
| 其中 reasoning_planning | 10 / 10 | 10 / 10 |
| Stage 1 的 205 题回归（按 GOLD_V2） | 197 / 204 | **202 / 204** |
| execution_mode（205 题） | 205 / 205 | 205 / 205 |

**205 题回归**：V3 与 V2 相比有 5 题判断不同，全部是由错变对（1 道 IMO 公式填空题恢复为 math，4 道 LongBench 从 general_qa 或 math 变为 research_analysis）。没有任何类别退步：general_qa 30/30、writing_language 28/29、math 35/35、reasoning_planning 25/25、coding 50/50、workflow_operation 29/29。剩下的 2 个错误与 V2 相同（WritingBench 26 判为 research_analysis；AutomationBench 1045 判为 workflow_operation），都是已知的歧义题。capability_need 分布基本不变。

## 4. 新出现的倾向：多文档"核对说法"的题被判为 research_analysis

按 Stage 1.6 重审的 gold（逐条核对"根据材料哪个说法对 / 错"归 general_qa），LongBench 的情况是：

| 输入方式 | V2 | V3 | V3 按 gold 分组 |
|---|---|---|---|
| 完整输入（5 题） | 2 / 5 | 2 / 5 | research 2/2 对；general_qa 3 题全判为 research_analysis |
| 超长：只给问题 | 15 / 25 | 17 / 25 | research 15/18；general_qa 2/7 |
| 超长：开头 / 中间 / 结尾采样 | 17 / 25 | 18 / 25 | research 16/18；general_qa 2/7 |
| 超长：五段采样 | 18 / 25 | 18 / 25 | research 16/18；general_qa 2/7 |
| 以上三种，只看高 / 中把握的 gold（19 题） | 13–15 / 19 | 13 / 19 | — |

- V3 对 research_analysis 的召回在超长视图下也很高（16/18）。
- 但 7 道 gold 为 general_qa 的 LongBench 题，有 5 道被判为 research_analysis。这些题都是"根据多份材料，判断哪个说法正确"，V3 把"跨多份材料核对"看作了综合分析。
- 这是 V3 在"多文档核对"上的边界偏移，而不是信息丢失：三种视图结果几乎相同，只给问题和给采样内容差别很小。
- 这类题的 gold 本身把握只是中或低；两类在长文档下选不同模型的影响有多大，需要 Stage 2 的模型实验说明。

## 5. 结论

1. **Prompt V3 达到通过标准**：新留出集 research_analysis 30/30（要求约 85–90%），general_qa 和 reasoning_planning 对照没有退步，205 题回归没有任何类别退步。
2. **超长请求**：修好 Prompt 后，三种视图在超长题上是 68–72%（全部 25 题），只看高 / 中把握的 gold 是 68%。按预设标准仍属"60–70%，暂不使用"的区间。结果对应方案里的情况 B：Prompt 修好了，但超长题仍不够准；而且主要误差来自"多文档核对"这一边界，采样本身带来的提升很小。**生产继续使用 `overflow_fallback`。**
3. **如果以后要做超长语义路由**，更值得做的是在 Prompt 中写清"跨多份材料核对说法"属于 general_qa，而不是继续改采样方式；按本阶段规则，V3 已冻结，未再修改。

## 6. Jev 用量（本阶段）

| 项目 | 调用 | 输入 tokens | 输出 tokens | 费用 |
|---|---|---|---|---|
| dev（V3 草稿） | 36 | 93,684 | 5,334 | $0.00393 |
| 留出集 V3 | 50 | 128,024 | 7,450 | $0.00538 |
| 留出集 V2（对照） | 50 | 114,424 | 7,508 | $0.00481 |
| 205 题回归 V3 | 205 | 634,693 | 30,453 | $0.02666 |
| 超长：只给问题 | 25 | 53,329 | 3,708 | $0.00224 |
| 超长：开头 / 中间 / 结尾 | 25 | 162,288 | 3,707 | $0.00682 |
| 超长：五段采样 | 25 | 173,077 | 3,707 | $0.00727 |
| **合计** | **416** | **1,359,519** | **61,867** | **$0.0571** |

费用按输入 $0.042 / 百万 token 计算，输出单价未公开未计入。

## 7. 文件

| 文件 | 内容 |
|---|---|
| `prompts/jev_prompt_v3.json` | 冻结的 V3（与 `jev_prompt_v3_dev1.json` 相同） |
| `STAGE1_7_HOLDOUT_SET.jsonl` | 留出集 |
| `stage1_7/dev_v3_dev1.jsonl` | dev 结果 |
| `stage1_7/holdout_v3.jsonl`、`stage1_7/holdout_v2.jsonl` | 留出集结果 |
| `stage1_7/regression205_v3.jsonl` | 205 题回归 |
| `stage1_7/overflow_{A,B,C}_v3.jsonl` | 超长题三种视图 |
| `scripts/run_prompt_eval.py` | 通用评测脚本 |
