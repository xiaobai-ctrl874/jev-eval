# Jev 路由视图设计（2026-09-30）

实现：`scripts/routing_view.py`（目前只在 bench 中实现和测试，**未接入网关**；engy-core 没有改动）。Jev Prompt V3 冻结不变。

## 1. 在网关中的位置（后续接入时）

```text
buyer 请求（原始 messages、tools）
      │  原样保留，最终转发给选中的模型
      ▼
auto 路由预处理：build_routing_view(messages, tools)   ← 只读，生成 Jev 专用视图
      ▼
Jev（Prompt V3）→ task_type / execution_mode / capability_need
      ▼
Policy 选模型
      ▼
选中的模型收到 **完整原始请求**
```

接入点：engy-core 开发分支 `feat/auto-text-v1` 的 `engy/gateway/autoroute.py`，`AutoRouter.resolve()` 中现在调用 `build_state()`（只截每段开头）的那一行，换成 `build_routing_view()`；视图信息记入 `Decision` 的审计字段。

**为什么每个任务只构造一次**：路由是 sticky 的，一个任务或会话只在第一次路由时调用 Jev，之后的轮次沿用已选模型。后续不断增长的工具输出、文件内容、对话历史都不再经过 Jev，所以只需处理"第一次调用时输入就很大"的情况。

## 2. 两种模式

判断依据：`估算 token(完整视图) + 估算 token(Jev 固定问题 Prompt)` 是否 ≤ `JEV_SAFE_INPUT_LIMIT` = 30,000（Jev 实测上限 33,559）。

| 模式 | 条件 | Jev 看到什么 |
|---|---|---|
| `full` | ≤ 30,000 | 全部消息的完整文本（不截断、不摘要、不采样）+ 工具的精简表示（或类别聚合） |
| `compact_view` | > 30,000 | 任务指令（完整）+ 系统目标（首句，≤400 字符）+ 环境（工具精简表示或类别）+ 客观元数据 + 必要时按指令检索的相关片段；目标 ≤ 12,000 token |

## 3. 工具表示

| 情况 | 表示 |
|---|---|
| 精简列表估算 ≤ 3,000 token | 每个工具：`name` + `category` + 一句说明（取工具自身说明的第一句，≤160 字符） |
| 超过 3,000 token | 只给 `{类别: 工具数}`，例如 `{"crm_operations": 84, "messaging": 20, ...}` |
| 任何情况 | 不传参数、必填项、枚举、嵌套结构和返回结构 |

类别由工具名按关键词规则确定（如 bash/shell → command_execution，git/github → repository_operations，slack/gmail → messaging，salesforce/hubspot → crm_operations）；没有匹配时取名字的第一段加 `_operations`。

## 4. compact_view 的构造（纯代码，不调用任何额外模型）

1. **任务指令**：取当前（首条）用户消息。
   - 如果消息由多个内容片段组成，短片段是指令，超过 3,000 token 的片段视为附件材料。
   - 如果是单个长字符串，先找成对的定界块（如 `<text>…</text>`、`<repository_context>…</…>`、``` 代码块），超过 3,000 token 的块视为附件材料，在指令中用"附件 N 已省略：约 X token"代替。
   - 如果没有任何结构可以区分指令和材料，保留开头约 1,000 token 和结尾约 2,000 token 作为指令，中间视为材料，并在日志中记为 `instruction_source = unstructured_head_tail`。
2. **系统目标**：系统提示的第一句，最多 400 字符。
3. **环境**：同第 3 节的工具表示。
4. **元数据**（只放网关可以确定的）：原始输入估算 token、对话轮数、模态、非文本片段数、工具数；附件数只在材料由结构明确分开时给出。
5. **相关片段检索**：只在"有附件材料且没有工具环境"时做。材料切成约 400 token 的块，用任务指令作为查询做 BM25 词法排序，按得分从高到低加入，直到视图达到 12,000 token，最后按原文顺序排列。有工具环境（agentic）时不检索，只靠任务和环境判断。

## 5. token 估算

没有 Jev 的分词器，调用前用保守估算：中日韩字符每个 1.1 token，**数字每个 1 token**，其余字符每 2.5 个 1 token。

- 最初的版本没有单独处理数字，在一道以数字为主的财务表格题上低估了 65%。
- 修正后，在 270 个实测样本上，实际值最多是估算的 1.05 倍，中位 0.60 倍。
- 因此 30,000 的估算上限对应的实际值最多约 31,500，低于 Jev 上限 33,559。

## 6. 原始请求不被修改

`build_routing_view` 只读取 `messages` 和 `tools`，生成新的对象。测试中对每个请求都比较了调用前后的原始数据，270 个请求全部未被修改。

## 7. 日志字段

`routing_mode`、`original_estimated_tokens`、`jev_estimated_tokens`、`jev_actual_input_tokens`、`tools_original_count`、`tool_representation`（none / compact / aggregated）、`instruction_source`、`retrieval_used`、`retrieved_chunk_count`、Jev 三个维度的结果与置信度、`jev_latency_ms`。不记录用户正文。

## 8. 性能

构造视图在 700 万字符（约 290 万 token）的文档上最慢约 1.6 秒，中位 0.09 秒。最初的切块实现每切一块都复制剩余文本，在同一文档上要 200 秒，已改为按偏移切块。
