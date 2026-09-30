# Jev 路由视图测试（2026-09-30）

脚本 `scripts/test_routing_view.py`；逐题结果 `JEV_ROUTING_VIEW_RESULTS.jsonl`。直接调用 Jev，Prompt V3 冻结，不经过网关，不调用任何候选模型。gold：LongBench 用 Stage 1.6 重审后的 gold，其余用 GOLD_V2。

## 测试 1：短请求回归（Stage 1 的 205 题）

| 指标 | 结果 |
|---|---|
| routing_mode | 201 题 full，4 题 compact_view（都是 LongBench，估算超过 30,000） |
| task_type | **199 / 204**，与原 V3 回归在同一 gold 下相同（199 / 204） |
| execution_mode | 205 / 205 |
| 与原 V3 回归不同的题 | 2 题（见下） |
| Jev 输入中位 / 最大 | 2,204 / 15,954 tokens |

与原 V3 回归不同的 2 题：

| 题目 | 原 V3 | 本次 | gold | 说明 |
|---|---|---|---|---|
| LiveBench 数学（IMO 公式填空） | math（0.42） | reasoning_planning（0.37） | math | 完整输入模式下给 Jev 的内容与原 V3 回归完全相同，结果仍变了。这是 Jev 在低置信度题上的非确定性，不是视图造成的 |
| LongBench AbbVie 半年新闻 | research_analysis | general_qa | general_qa | 这题现在走 compact_view，由错变对 |

## 测试 2：长 agentic 请求

构造：10 道 DeepSWE 的首条请求，在用户消息中附加约 10 万 token 的仓库源码（engy-core 的真实 Python 文件，放在 `<repository_context>` 块中），工具为 bash。

| 指标 | 结果 |
|---|---|
| 原始输入估算 | 约 124,800 tokens |
| routing_mode | 10 / 10 compact_view |
| 指令提取 | 10 / 10 按定界块分离，仓库内容未进入视图 |
| 检索 | 未使用（有工具环境） |
| task_type | **10 / 10 coding** |
| execution_mode | **10 / 10 agentic** |
| Jev 输入中位 / 最大 | 3,251 / 3,553 tokens |

## 测试 3：长 research 请求（25 道 LongBench 超长题）

| 输入方式（均为 Prompt V3） | 全部 25 题 | 只看高 / 中把握 gold（19 题） | research 召回（18 题） |
|---|---|---|---|
| 只给问题（Stage 1.7） | 17 / 25 = 68% | 13 / 19 | 15 / 18 |
| 固定位置：开头 / 中间 / 结尾（Stage 1.7） | 18 / 25 = 72% | 13 / 19 | 16 / 18 |
| 固定位置：五段（Stage 1.7） | 18 / 25 = 72% | 13 / 19 | 16 / 18 |
| **按指令检索（BM25）** | **19 / 25 = 76%** | **14 / 19** | **17 / 18** |

| 其他指标 | 检索视图 |
|---|---|
| 检索块数 | 21–33 块 |
| Jev 输入中位 / 最大 | 7,142 / 11,948 tokens |
| 延迟中位 / 最大 | 315 / 477 ms |

错误分布：7 道 gold 为 general_qa 的题有 5 道被判为 research_analysis（"根据多份材料判断哪个说法正确"类），1 道 research_analysis 判为 reasoning_planning。与固定位置采样的错误模式相同。

## 测试 4：大工具目录（549 个工具）

构造：30 道 AutomationBench 首条请求，工具换成 limited_zapier 工具集的全部 549 个完整定义（完整定义估算约 19 万 token）。

| 指标 | 结果 |
|---|---|
| 工具表示 | 30 / 30 按类别聚合 |
| routing_mode | 30 / 30 full（聚合后请求很小） |
| Jev 输入中位 / 最大 | 2,380 / 2,483 tokens |
| task_type | 29 / 30（唯一错误是已知歧义题 marketing:1045，置信度 0.42） |
| execution_mode | 30 / 30 agentic |

对照：同样 30 题用 3 个工具的精简表示（Stage 1.5）时，task_type 结果与这里一致，只有 1045 这道题在两次运行中结果不同（本来就是低置信度的歧义题）。

## token 估算校验

| 估算方式 | 实际 / 估算（270 个样本） |
|---|---|
| 初版（不单独处理数字） | 最大 1.65（一道以数字为主的财务表格题），中位 0.60 |
| 定版（数字每个 1 token） | 最大 1.05，中位 0.60 |

第一轮测试用的是初版估算，发现问题后改为定版，并用定版重跑了全部四组；本文所有结果都来自定版。第一轮结果保留在 `stage1_7/routing_view_results_estimator_v1.jsonl`。

## Jev 用量

| 轮次 | 调用 | 输入 tokens | 输出 tokens | 费用 |
|---|---|---|---|---|
| 定版（本文结果） | 270 | 849,138 | 40,133 | $0.0357 |
| 初版（已作废，保留记录） | 270 | — | — | $0.0369 |
| **合计** | **540** | | | **$0.0726** |

费用按输入 $0.042 / 百万 token 计算，输出单价未公开未计入。
