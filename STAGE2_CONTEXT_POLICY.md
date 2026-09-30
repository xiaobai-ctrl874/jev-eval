# Stage 2 上下文与容量规则（2026-09-30）

**状态：已冻结（2026-09-30）。** 后续如需修改，另建新版本。

本文件只定实验设计和统计规则，不涉及任何模型调用。Jev 层（Prompt V3、taxonomy、30K full / compact_view、BM25、精简工具）冻结，不改。

## 候选模型的容量（Engy 实测，9/30）

| 模型 | 输入上限 `model_input_limit` | 安全上限 `capacity_safe_limit`（× 0.95） | 备注 |
|---|---|---|---|
| glm-5.3-flash | 229,376 | 217,907 | 输出上限 32,768 |
| deepseek-v4.1-flash | 262,144 | 249,037 | 输出上限 65,536；9/29 曾接受 280,621，9/30 收紧 |
| glm-5.3 | 294,912 | 280,166 | 输出上限 32,768 |
| deepseek-v4-flash-0731 | 920,576 | 874,547 | 9/29 曾接受 1,042,101 |
| kimi-k3 | 约 1,048,576（输入 + 输出的总窗口） | 约 996,147 | 临界区网关放行、后端拒绝：后端计数比网关估算多约 1%，0.95 的余量可以覆盖 |

- 这些上限都是按网关自己的 token 计数测得的。实验中的 `estimated_input_tokens` 优先使用网关同一段计数代码；拿不到时用 `routing_view.estimate_tokens` 的保守估算，并在记录中注明来源。
- 容量可能变化（9/29 到 9/30 就收紧过），正式实验开始前重测一次并记录日期。

## 1. Jev 的 30K 和模型容量有什么区别

| | Jev 的 30K | 模型容量 |
|---|---|---|
| 是什么 | Jev 路由输入的安全上限（Jev 实测最大 33,559） | 真正做题的模型能接受的输入长度 |
| 决定什么 | Jev 看完整请求（full）还是压缩视图（compact_view） | 哪些模型有资格接这个请求 |
| 超过时 | 网关构造压缩视图给 Jev，最终模型仍收到完整原始请求 | 这个模型不参与该请求的比较和选择 |

所以"请求超过 30K"不等于"长上下文任务"。一个 100K 的请求，Jev 看的是压缩视图，但 5 个候选模型都能装下，它仍属于 normal context。

## 2. 什么题属于 normal-context 主实验

对某个组合（例如 coding + direct），先求该组合全部候选中最小的安全上限：

```text
bucket_safe_limit = min(各候选的 capacity_safe_limit)
```

一道题只有在 `estimated_input_tokens ≤ bucket_safe_limit`，即对所有候选都 `capacity_eligible = true` 时，才进入 `normal_context_primary_set`，参与分数、成本、延迟、胜负平和 bootstrap 置信区间的比较。

例：coding + direct 的候选含 GLM-5.3-Flash，bucket_safe_limit = 217,907。

## 3. 什么情况下移到 long_context_pool

模型调用前，对每个候选做容量检查：只要有任何一个候选 `capacity_eligible = false`，这道题就不进入 normal-context 主实验，而是标记 `moved_to_long_context_pool = true`，放进长上下文池，留给长上下文专项。题目不丢弃。

## 4. 容量超限是否计错

**不计错。** 装不下的模型记为 `result_status = capacity_ineligible`，不记 0 分，也不记答错，并从该组合的 normal-context 主统计中整题排除（所有候选都排除，而不是只排除装不下的那个）。

## 5. 容量不一致时如何保证公平

主实验只在"所有候选都装得下"的题上比较。这样两个模型的分差只反映任务能力，而不会混进"一个装得下、一个装不下"的容量差异。例如 Kimi 90%、DS 80%，如果其中 10 分来自 DS 装不下的题，那比较的就不是能力。

每个组合都要报告：`total_sampled_tasks`、`normal_context_tasks`、`capacity_excluded_tasks`。模型比较只基于 `normal_context_tasks`。

## 6. 为什么超过约 30 万 token 只剩 Kimi K3 和 DS 0731

按安全上限，GLM-5.3-Flash 在约 21.8 万、DS 4.1 在约 24.9 万、GLM-5.3 在约 28 万就都装不下了；DS 0731（约 87.5 万）和 Kimi（约 99.6 万）还能装。超过约 87.5 万后只剩 Kimi。

## 7. 长上下文是否仍按 task_type 分类

是。长上下文是请求属性（`context_length`），不是 task_type。每题仍保留 Jev 给出的 task_type、execution_mode、capability_need，例如"research_analysis + direct + 40 万"、"coding + agentic + 50 万"。

## 8. 长上下文以后怎么决定 Kimi 还是 DS 0731

- 按"请求长度"做确定性容量过滤，只比较装得下的模型；装不下由网关判断，不交给 Jev。
- 按 task_type 分组比较分数、成本、延迟，不同 task_type 允许有不同答案。
- 选型规则与 normal context 相同：先找最高分；另一个模型若分差 ≤ 满分尺度 1 个百分点且成本低 ≥ 20%，选便宜的；否则选最高分。不因为只剩两个模型就改规则。
- 公开证据（AA-LCR：Kimi 88.7 vs 0731 79.7；单题成本 Kimi 约为 0731 的 6 倍）只作参考，不直接写成规则。
- 当前不专门构造大量 1M token 的题。Stage 2B 先照常跑已有 benchmark，把因容量被排除的题收进池子，统计数量、task_type 和长度分布；只有样本明显不足时，再考虑补长上下文 benchmark。

## 9. agentic 任务中途超过模型容量怎么记

agentic 任务要分两件事记录：

| 情况 | 处理 |
|---|---|
| 第一次请求就有候选装不下 | 与 direct 相同：该任务移到长上下文池，不进主实验 |
| 第一次都装得下，但运行过程中轨迹变长，sticky 的模型超过自己的窗口 | 记为 `runtime_context_overflow`，单独统计，**不算作普通的模型质量失败**；当前阶段只记录，不设计中途换模型 |

**风险提醒（不是预设结论）**：按 DeepSWE 榜单逐轮数据和旧的上限粗略推算，部分长轨迹可能超限（GLM-5.3-Flash 约 13%、DS 约 12%、GLM-5.3 约 4%、Kimi 约 0）。这些数字只用来提醒风险，正式实验以实测的 `runtime_context_overflow` 为准。DeepSWE 的报告要同时给出实测超限率和"去掉运行中超限的题之后的分数"。

## 10. 网关容量过滤与 Jev、Policy 如何配合

```text
请求
 ├─ Jev（Prompt V3；≤30K 看完整请求，>30K 看压缩视图）→ task_type / execution_mode / capability_need
 ├─ 网关容量过滤（确定性）：按估算 token 与各模型安全上限，删掉装不下的模型
 └─ Policy：在剩下的模型里，按该组合（和长度区间）的选择结果挑模型
```

- 两步的先后可以互换（也可以先过滤再查 Policy），关键是"模型能不能装下"由网关判断，绝不交给 Jev。
- 剩下 0 个模型：返回网关现有的容量错误。
- 剩下 1 个：直接用它。
- 剩下多个：按 Policy 选。

## 新增的逐题记录字段

`estimated_input_tokens`、`estimated_tokens_source`（gateway / routing_view）、`context_bucket`（normal / long）、每个候选的 `capacity_eligible`、`model_input_limit`、`capacity_safe_limit`、`exclusion_reason`（none / capacity_ineligible）、`moved_to_long_context_pool`、`result_status`（含 capacity_ineligible）、agentic 另加 `runtime_context_overflow`。
