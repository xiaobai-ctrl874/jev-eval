# Stage 1.5 实验 A：工具信息给 Jev 多少（2026-09-30）

Prompt V2（冻结）不变，只改变 Jev 看到的工具信息。脚本 `scripts/stage1_5_tool_ablation.py`，结果 `stage1_5/tool_ablation_results.jsonl`。

## 设计

| 项目 | 内容 |
|---|---|
| 题目（固定，不重抽） | agentic：DeepSWE 20、AutomationBench 30；direct 对照：SimpleQA 10、LiveCodeBench 10（各取 Stage 1 考卷中按 id 排序的前 10 题） |
| 对照题的工具 | 给 direct 对照题同样挂上工具（mini-swe-agent 的 bash 工具 + AutomationBench 的 3 个 API 工具），检验 Jev 会不会"看到工具就判 agentic" |
| A 完整定义 | 完整 JSON 工具定义（DeepSWE：bash；AutomationBench：官方 runner 默认 api 工具集的 3 个工具） |
| B 精简 | 每个工具只给名称、类别、一句说明（取工具自身说明的第一句）；不给参数、必填项、枚举等 |
| C 不给 | 只给 messages |

**更正一处 Stage 1 / V2 的输入问题**：之前重建 AutomationBench 首条请求时，工具字段只存了工具名，没有存完整定义（重建脚本的 bug）。所以 Stage 1 和 V2 中 AutomationBench 实际给 Jev 的是"只有名字"的工具列表。本实验改用 runner 真实发送的完整定义（`stage1_5/ab_tool_schemas.json`）。冻结的 Stage 1 / V2 结果未改动。

## 结果

| 指标 | A 完整定义 | B 精简 | C 不给 |
|---|---|---|---|
| task_type | 69 / 70 | 69 / 70 | 69 / 70 |
| execution_mode | 70 / 70 | 70 / 70 | 70 / 70 |
| agentic 题判为 agentic | 50 / 50 | 50 / 50 | 50 / 50 |
| direct 对照题判为 direct | 20 / 20 | 20 / 20 | 20 / 20 |
| 输入 token 平均 / 中位 / P90 | 2,763 / 2,694 / 3,107 | 2,197 / 1,989 / 2,917 | 2,085 / 1,858 / 2,880 |
| 延迟中位 | 168 ms | 166 ms | 167 ms |
| 70 次费用 | $0.00812 | $0.00646 | $0.00613 |

| 一致性 | task_type | execution_mode |
|---|---|---|
| B 与 A | 70 / 70 | 70 / 70 |
| C 与 A | 70 / 70 | 70 / 70 |

唯一的 task_type 错误三组相同：AutomationBench marketing:1045（gold 为 research_analysis，三组都判 workflow_operation），这是 gold 复核时已标明的歧义题。

## 工具很多时的规模

AutomationBench 的 limited_zapier 工具目录共 549 个工具：

| 表示方式 | 估算 token |
|---|---|
| 完整定义 | 约 190,678，远超 Jev 上限 |
| 精简 | 约 25,356，加上 Prompt 约 27,000，在 30,000 安全线内但余量很小 |

## 结论

- 本实验中工具信息对分类没有影响：三种方式逐题完全一致；给 direct 题挂上工具，Jev 也没有误判为 agentic。
- 本实验的工具集都很小（1–4 个），完整定义也只有几千 token，所以"完整定义 vs 精简"的差别主要体现在 token 上。
- **推荐生产默认用精简表示**：分类结果相同，token 更少；遇到大工具目录时完整定义根本放不进 Jev，精简后仍可放入。
- 不删除工具信息：按方案，instruction 含糊的真实请求里环境信息可能有用，本实验的题目 instruction 都很清楚，测不出这一点。
- 待注意：工具数达到数百个时，精简表示也接近 30,000 上限，届时需要按工具类别合并或只列类别，本实验未测。

## Jev 用量

210 次调用，输入 493,133 tokens，输出 31,200 tokens，费用 **$0.0207**（按输入 $0.042 / 百万 token；输出单价未公开未计入）。
