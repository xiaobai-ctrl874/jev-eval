# Jev 输入上限实测（V2）

测试时间：2026-09-30。脚本：`scripts/jev_context_limit_test.py`；原始记录：`context_limit/results.jsonl`。

## 方法

- 使用冻结的 Stage 1 Prompt，发送单条用户消息，内容是逐行重复的英文句子，按行数控制长度。
- 先按约 24K、28K、30K、31K、32K、33K、36K、40K token 分段测试，再在最后一个成功点和第一个失败点之间二分，直到相差 1 行（约 24 token）。
- 成功时的 token 数取自 Jev 返回的 `usage.input_tokens`，该数值已包含 Jev 自身的 Prompt（约 1,387 token）。失败时 Jev 不返回 token 数，按相邻成功点推算。

## 结果

| 输入 | 结果 | Jev 报告的 input_tokens | 延迟 |
|---|---|---|---|
| 约 24K | 成功 | 24,079 | 317 ms |
| 约 28K | 成功 | 28,471 | 352 ms |
| 约 30K | 成功 | 30,679 | 382 ms |
| 约 31K | 成功 | 31,783 | 453 ms |
| 约 32K | 成功 | 32,887 | 410 ms |
| 约 33K 及以上（3 个点） | 失败：`max_tokens_exceeded` | — | 约 150–180 ms |
| 二分：1,433 行 | 成功 | **33,559** | 405 ms |
| 二分：1,434 行 | 失败 | 约 33,580（推算） | 149 ms |

| 结论 | 数值 |
|---|---|
| `confirmed_max_success` | **33,559** input tokens（Jev 计数，含 Jev Prompt） |
| `confirmed_min_failure` | 约 **33,580** input tokens（比最大成功点多 1 行） |

推测：上限在 33.5K 左右，可能是模型窗口约 34K 减去为输出预留的部分。Jev 每次输出约 140 token。以上是实测值，TypeSafe 没有公开说明。

## 安全上限 `JEV_SAFE_INPUT_LIMIT`

调用 Jev 之前无法得到它的精确 token 数（没有 Jev 的分词器），所以在调用前按保守估算判断：

- 估算方法（`scripts/jev_token_estimate.py`）：中日韩字符每个按 1.1 token，其余字符每 2.5 个按 1 token，再加上 Prompt 的 token 数。
- 在 Stage 1 的 205 道成功题上校验：实际值 / 估算值最大为 1.04，中位 0.92，也就是说估算最多低估 4%。

**定义 `JEV_SAFE_INPUT_LIMIT` = 30,000（估算 token，含 Jev Prompt）。**

| 余量来源 | 大小 |
|---|---|
| 估算误差（实测最多低估 4%） | 30,000 × 1.04 = 31,200，仍低于 33,559 |
| 剩余缓冲 | 约 2,300 token，覆盖 Prompt 后续变长和未见过的文本类型 |

V2 Prompt 比 Stage 1 长约 200 token，已计入。

## 覆盖率

按上述规则，Stage 1 的 230 题中：

| 分类 | 题数 |
|---|---|
| 可以完整输入给 Jev（`routing_mode = full`） | **202（87.8%）** |
| 超过安全上限（`routing_mode = overflow_fallback`） | 28，全部是 LongBench v2 |

其中 3 道 LongBench 题在 Stage 1 实际调用成功（实际 token 低于 33,559），但估算超过 30,000，按新规则在生产中会走 overflow_fallback。V2 复测为了与 V1 对比，仍按原输入调用这 3 题，并在结果里单独标注。
