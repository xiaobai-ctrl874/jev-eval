# Jev Prompt V1 与 V2 对比（2026-09-30）

本轮只调用 Jev，没有运行任何候选模型。所有数字由 `scripts/analyze_v1_v2.py` 从结果文件计算。

## 1. 本轮做了什么

| 步骤 | 内容 |
|---|---|
| 冻结 baseline | `prompts/jev_prompt_stage1.json`（下称 V1）、`STAGE1_JEV_RESULTS.jsonl` 和 Stage 1 报告均未改动 |
| gold 复核 | 40 道争议题按建议确认（`GOLD_REVIEW_REQUIRED.md`、`STAGE1_GOLD_REVIEW_REQUIRED.csv`）。结果另存 `GOLD_V2.jsonl`，原考卷不改 |
| Prompt V2 | `prompts/jev_prompt_v2.json`（sha256 `eac800f8…26c7ec`）：新增 workflow_operation；重写 execution_mode；修改 math 与空间推理的边界说明；其余不动 |
| 上限实测 | Jev 最大成功 33,559 input tokens；定 `JEV_SAFE_INPUT_LIMIT` = 30,000（`JEV_CONTEXT_LIMIT_V2.md`） |
| V2 复测 | Stage 1 成功的 205 题全部重跑，输入和调用方式与 V1 相同，205/205 成功 |
| 超长实验 | 25 道 LongBench 超长题，按结构化方式单独运行，25/25 成功 |

**gold 的变化**（在 V2 运行之前确定，之后未再改动）

| 变化 | 题数 |
|---|---|
| LiveBench 几何切割题：reasoning_planning → math | 5 |
| AutomationBench：从"无类别"或勉强归类改为 workflow_operation | 29 |
| AutomationBench marketing:1045：维持 research_analysis | 1 |
| WritingBench 425（广告语 + 推广策划）：有歧义，不计入 task_type 准确率 | 1 |

注意：几何题的 gold 是在看到 V1 结果之后改的。V1 在这 5 题上本来就判为 math，所以在新 gold 下 V1 在这 5 题上"变对了"。对比时请记住这一点。

## 2. task_type

**总体**（204 题，排除 1 道歧义题；按 V2 gold 评分）

| Prompt | 正确 | 准确率 |
|---|---|---|
| V1 | 171 / 204 | 83.8% |
| **V2** | **197 / 204** | **96.6%** |

提升主要来自 workflow_operation：V1 没有这个类别，29 题全错；V2 29 题全对。

**只看 154 道 direct 考卷题**（不含 AutomationBench 和 DeepSWE）

| Prompt | 正确 | 准确率 |
|---|---|---|
| V1 | 150 / 154 | 97.4% |
| V2 | 148 / 154 | 96.1% |

V2 在这部分**少对 2 题**，是两道回退（见下）。作为对照：V1 按 Stage 1 原 gold 是 145/155 = 93.5%。

**各类别**（按 V2 gold）

| 类别 | 题数 | V2 正确 | V1 正确 | V2 的错误 |
|---|---|---|---|---|
| general_qa | 30 | 30 | 30 | — |
| writing_language | 29 | 28 | 28 | research_analysis 1 |
| math | 35 | 34 | 35 | reasoning_planning 1 |
| reasoning_planning | 25 | 25 | 25 | — |
| coding | 50 | 50 | 50 | — |
| research_analysis | 6 | 1 | 3 | general_qa 3、math 1、workflow_operation 1 |
| **workflow_operation** | 29 | **29** | 0 | — |

**子类**

| 子类 | 题数 | V2 结果 |
|---|---|---|
| reasoning（LiveBench 推理，非几何） | 10 | 全部 reasoning_planning |
| 几何切割（gold 已改为 math） | 5 | 全部 math |
| planning（PlanningBench） | 15 | 全部 reasoning_planning |
| DeepSWE | 20 | 全部 coding |
| AutomationBench | 30 | 全部 workflow_operation |

**V2 混淆矩阵**（行为 gold，列为 V2 判断）

| gold \ V2 | general_qa | writing | math | reasoning_planning | coding | research | workflow |
|---|---|---|---|---|---|---|---|
| general_qa | 30 | 0 | 0 | 0 | 0 | 0 | 0 |
| writing_language | 0 | 28 | 0 | 0 | 0 | 1 | 0 |
| math | 0 | 0 | 34 | 1 | 0 | 0 | 0 |
| reasoning_planning | 0 | 0 | 0 | 25 | 0 | 0 | 0 |
| coding | 0 | 0 | 0 | 0 | 50 | 0 | 0 |
| research_analysis | 3 | 0 | 1 | 0 | 0 | 1 | 1 |
| workflow_operation | 0 | 0 | 0 | 0 | 0 | 0 | 29 |

**V2 的全部 7 个错误**

| 题目 | gold | V2 | 置信度 | V1 | 说明 |
|---|---|---|---|---|---|
| AutomationBench marketing:1045 | research_analysis | workflow_operation | 0.91 | research_analysis | 本来就是歧义题（分析后通过系统交付） |
| LiveBench math（IMO 题，把公式填回证明） | math | reasoning_planning | 0.46 | math | **回退**。可能是新写的"不要只因出现数字就判 math"起了反作用；题目形式是"匹配公式"，不是解题 |
| LongBench 表 1 能否推出结论 | research_analysis | general_qa | 0.41 | general_qa | V1 也错 |
| LongBench 三个时间段伤亡比较 | research_analysis | math | 0.56 | math | V1 也错 |
| LongBench AbbVie 半年新闻 | research_analysis | general_qa | 0.62 | general_qa | V1 也错 |
| LongBench 非洲清洁炊具结论 | research_analysis | general_qa | 0.32 | research_analysis | **回退**，置信度很低 |
| WritingBench 26（总结 AI 落地经验） | writing_language | research_analysis | 0.98 | research_analysis | V1 也错；research_analysis 的 Prompt 描述里有 "research-style analysis"，与 taxonomy 定义不一致，本轮按"少改"原则没动 |

## 3. execution_mode

| gold | 题数 | V2 正确 | V1 正确 |
|---|---|---|---|
| direct | 155 | **155** | 150 |
| agentic | 50 | **50** | 50 |

SimpleQA 中 5 道被 V1 误判为 agentic 的事实题，**V2 全部修正为 direct**。V2 没有任何 execution_mode 错误。

## 4. capability_need（只报告分布，不计算准确率）

| 来源 | V2 分布 | 与 V1 相比 |
|---|---|---|
| SimpleQA Verified | 30 standard | 相同 |
| MATH-500 | 20 standard（1–5 级全部） | 相同 |
| LiveBench 数学 | 7 standard、3 strong | 相同 |
| LiveBench 推理 | 8 standard、7 strong | 相同 |
| LiveCodeBench | 22 standard、8 strong | 相同 |
| WritingBench | 17 standard、13 strong | 相同 |
| PlanningBench | 12 strong、3 frontier | 相同 |
| DeepSWE | 15 strong、5 frontier | 相同 |
| AutomationBench | 21 strong、9 standard | 相同 |
| LongBench v2（5 题） | 2 standard、3 strong | V1 为 3 standard、2 strong |

与官方难度的趋势：

| 来源 | 官方难度 × Jev 档位 | Spearman |
|---|---|---|
| LiveCodeBench | easy：10 standard；medium：8 standard、2 strong；hard：4 standard、6 strong | 0.554（V1 相同） |
| MATH-500 | 1–5 级全部 standard | 无法计算（Jev 不区分） |

## 5. 输入长度、延迟、费用

| 指标 | V2 | V1 |
|---|---|---|
| input tokens 中位 | 1,860 | 1,672（V2 Prompt 长约 200 token） |
| input tokens p90 / 最大 | 3,852 / 30,837 | — |
| 延迟中位 / p90 / 最大 | 172 / 211 / 418 ms | 161 / 211 / 1,442 ms |
| 205 次费用 | $0.0243 | $0.0227 |
| 估算 token 的最大低估 | 3.7%（低于上限设计时假设的 4%） | — |

费用只按输入 token × $0.042/百万计算，输出单价未公开。

## 6. 超长输入的结构化实验（不属于完整输入准确率）

输入：完整问题和选项，文档正文换成"作为单独附件提供"，另附原始长度估算；不含 benchmark 名称和子领域。

| 指标 | 结果 |
|---|---|
| 成功调用 | 25 / 25 |
| `structured_overflow_task_type_accuracy` | **14 / 25 = 56%** |
| 错判 | general_qa 10、reasoning_planning 1 |
| execution_mode | 全部 direct（正确） |
| 最大输入 | 2,121 tokens；25 次共 $0.002 |

错判为 general_qa 的题，问题本身多是"根据材料，以下哪个结论正确"的选择题。去掉材料后，Jev 看到的像普通问答。说明只给指令加长度，不足以可靠识别 research_analysis。

## 7. 回答 13 个问题

1. **6 类还是 7 类？** 7 类更合理。AutomationBench 在 6 类下 25/30 归不进任何类别；加入 workflow_operation 后 V2 在 29 道 gold 为 workflow_operation 的题上全对，且没有把其他类别的题误吸进来（除了本来就有歧义的 1045）。
2. **workflow_operation 是否解决了强塞 reasoning_planning 的问题？** 解决了。V1 把 23 道 AutomationBench 题放进 reasoning_planning；V2 这 30 题全部判为 workflow_operation，reasoning_planning 中不再混有业务流程题。
3. **reasoning_planning 是否继续合并？** 继续合并。planning 15/15、非几何 reasoning 10/10 全对，没有发现需要拆分的证据。
4. **几何题的最终 gold 定义？** 正式的几何或组合几何问题（正方体、正多边形、切割计数、带约束的极值），答案是唯一的形状或整数，归 math。空间关系、非正式的空间推理谜题归 reasoning_planning。不能只因为出现形状、数字、多边形、立方体或计数就判 math。
5. **task_type V2 准确率？** 204 题 197 对，96.6%。只看 direct 考卷是 148/154 = 96.1%，比 V1 少 2 题（两道回退）。research_analysis 仍是最弱的类别（6 题只对 1 题），样本太少，不能下结论。
6. **direct / agentic 是否稳定？** 稳定。V2 在 205 题上全对（direct 155、agentic 50）。
7. **SimpleQA 的误判是否解决？** 解决。5 题全部改判为 direct，V2 中 SimpleQA 没有任何 agentic 判断。
8. **Jev 安全输入上限？** 实测最大成功 33,559 input tokens（Jev 计数，含 Prompt），最小失败约 33,580。`JEV_SAFE_INPUT_LIMIT` = 30,000（调用前估算，含 Prompt）。
9. **正常请求的完整输入覆盖率？** 本考卷 230 题中 202 题（87.8%）在安全上限内；超过的 28 题全是 LongBench v2。真实线上流量的比例需要用线上日志另行统计。
10. **结构化超长输入是否可行？** 部分可行，目前不够可靠：task_type 准确率 56%，大量被判为 general_qa。不建议现在进入生产。
11. **未结构化的超长请求怎么处理？** 不调用 Jev，不截断、不摘要，直接走长上下文兜底（`overflow_fallback`），并记录 `routing_mode`。
12. **capability_need 能否作为 Policy 输入？** 现在不能。V1 和 V2 分布几乎相同；只在 LiveCodeBench 上与官方难度有中等单调关系，MATH-500 完全不区分。是否有用，要看候选模型实验中不同档位下模型的相对优势是否稳定变化。
13. **Stage 2 能否开始？** task_type（除 research_analysis）和 execution_mode 已经足够稳定，可以开始 Stage 2 的准备。开始前建议先决定：
    - 两道回退是否需要处理（IMO 公式填空题、LongBench 置信度 0.32 的题），还是作为已知误差接受；
    - research_analysis 样本太少（完整输入只有 6 题），是否补充更多不超长的数据源；
    - 生产中超长请求一律走 `overflow_fallback`，结构化方案暂不上线。

## 8. 局限

- 每类 25–50 题，一两题的差别在误差范围内；V1 与 V2 的 direct 部分只差 2 题，不能说 V2 变差或变好。
- 几何题 gold 在看过 V1 结果后才修改。
- AutomationBench 与 LongBench 的 gold 由 agent 判断、用户按建议确认，没有独立的第二人逐题复核。
- 考卷中的 agentic 首条请求是按官方模板拼出来的。
- Jev 单价和上限均为推断或历史记录，未经 TypeSafe 确认。

## 9. 文件

| 文件 | 内容 |
|---|---|
| `GOLD_REVIEW_REQUIRED.md`、`STAGE1_GOLD_REVIEW_REQUIRED.csv` | gold 复核材料与确认结果 |
| `GOLD_V2.jsonl` | 230 题的 V2 gold |
| `prompts/jev_prompt_v2.json` | 冻结的 Prompt V2 |
| `JEV_CONTEXT_LIMIT_V2.md`、`context_limit/results.jsonl` | 上限实测 |
| `ROUTING_INPUT_POLICY_V2.md` | 路由输入策略 |
| `STAGE1_V2_JEV_RESULTS.jsonl` | 205 题 V2 结果（含 V1 结果与 routing_mode） |
| `STRUCTURED_OVERFLOW_INPUTS.jsonl`、`STRUCTURED_OVERFLOW_RESULTS.jsonl` | 超长实验输入与结果 |
| `scripts/run_v2_jev.py`、`scripts/analyze_v1_v2.py` | 运行与分析脚本 |
