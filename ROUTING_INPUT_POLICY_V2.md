# Jev 路由输入策略 V2（草案）

## 规则

| 情况 | routing_mode | 做法 |
|---|---|---|
| 完整路由输入的估算 token ≤ `JEV_SAFE_INPUT_LIMIT`（30,000） | `full` | 把完整 messages（含系统提示、完整工具定义）交给 Jev。不截头、不截尾、不摘要、不删正文 |
| 超过上限，且文档与用户指令在请求结构上本来就是分开的（例如文件或附件字段） | `structured_overflow` | 只把完整的用户指令和系统可靠可得的元数据交给 Jev（原始输入的估算 token、模态）。**不提供**文档正文、benchmark 名、类别或子领域等元数据。目前只做实验，未进入生产 |
| 超过上限，且文档和指令混在同一条消息里，无法可靠拆开 | `unstructured_overflow` | 不调用 Jev，直接走长上下文兜底 |
| 生产 V1：任何超过上限的请求 | `overflow_fallback` | 不调用 Jev。先按确定性条件筛模型（上下文容量、模态、worker 是否在线等），再进入长上下文兜底 Policy |

## 明确不做

- 不做自动摘要。
- 不做截头、截尾或"开头加结尾"。
- 不让 Jev 根据残缺输入去猜。
- 用户把超长文档直接粘贴进一条消息的情况，目前没有解决办法，标为 `unstructured_overflow`，走长上下文兜底。以后如果需要，再单独研究从消息中抽取任务指令或压缩的方法。

## 需要记录的字段

每次路由都记录：`routing_mode`、原始输入估算 token、实际交给 Jev 的输入 token（Jev 返回值）、是否调用了 Jev、Jev 延迟、Jev 费用。

## structured_overflow 实验

- 对象：Stage 1 中 25 道输入超出 Jev 上限的 LongBench v2 题，不删除、不换题、不补抽，也不计入完整输入的准确率。
- 输入（`STRUCTURED_OVERFLOW_INPUTS.jsonl`）：LongBench 官方模板的指令、完整问题和选项；文档正文替换为一句"文本作为单独附件提供"；另附 `attached_context: {modality: text, approx_tokens: N}`。
- 不提供文档数量：LongBench 的材料是一个拼接好的文本字段，原始结构里拿不到可靠的文档数量。
- 结果单独报告为 `structured_overflow_task_type_accuracy`。它回答的是"如果线上能把文档和指令分开，超长请求还能不能路由"，不代表完整输入的准确率。
