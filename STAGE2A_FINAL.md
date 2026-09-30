# Stage 2A 总结（2026-09-30）

本阶段只做证据审计和实验计划，没有运行任何候选模型。详见 `STAGE2_EXISTING_EVIDENCE_AUDIT.md`、`STAGE2_BUCKET_STATUS.md`、`STAGE2_BENCHMARK_PLAN.md`。

| 问题 | 回答 |
|---|---|
| 1. 哪些组合已有足够证据 | **没有**。公开证据都是 B 级（厂商 API 全精度、harness 不同），本项目在 Engy 上没有任何组合有多候选的 A 级对比 |
| 2. 哪些必须补跑 | 全部 8 个组合。其中 writing、research_analysis 还缺评分方式（需先定判卷）；reasoning_planning + agentic 没有合适 benchmark，本阶段不测 |
| 3. 每个组合最值得测的模型 | 事实问答：Kimi、DS 4.1、GLM-Flash；写作：Kimi、GLM-5.3、DS 4.1、GLM-Flash；数学：DS 4.1、Kimi、GLM-Flash；推理与规划：Kimi、DS 4.1、GLM-5.3；编程（direct）：Kimi、DS 4.1、GLM-5.3、GLM-Flash；研究分析：DS 4.1、Kimi、GLM-Flash；编程（agentic）：GLM-5.3、Kimi、DS 4.1、GLM-Flash；业务流程（agentic）：DS 4.1、GLM-5.3、GLM-Flash（Kimi 可选） |
| 4. 不必测的模型 | qwen3.6-35b-a3b（各项统一测评都很差）；deepseek-v4-flash-0731 在短请求组合中不测（几乎全面低于 DS 4.1 且略贵，只在长上下文有价值）；qwen3.8-27b 暂不测 |
| 5. 可直接复用的历史结果 | 严格说没有。唯一接近 A 级的是 9/23 DS 4.1 的 HumanEval+/MBPP+（83.9%），但当时未开推理，与计划的设置不同，且需你确认 9/29 的作废规则是否也包括 9/23 那次实验。建议只作参考 |
| 6. 必须作废或只能参考的 | 9/27–28 的 HLE、AutomationBench、DeepSWE 全部作废；9/23 的其余结果（被截断、子集）和 TrajectoryRL 文档（无原始数据）只能参考；沈阳服务器上的日志未审计 |
| 7. Stage 2B 最少要跑多少 | 第一轮约 400 次 direct 调用（6 组 × 约 20 题 × 3–4 个模型）+ 约 200 次判卷，以及约 100 个 agentic 任务（AutomationBench 约 60、DeepSWE 48） |
| 8. 预计总成本与时间 | 第一轮约 $40–170（DeepSWE 占大头，取决于 Engy 是否按缓存价计费），约 1–1.5 天；需要扩样时最坏约为 2–2.5 倍 |
| 9. 长上下文已知证据 | AA-LCR：Kimi 88.7 > DS 4.1 84.0 > GLM-Flash 80.0 ≈ 0731 79.7 = GLM 79.7；单题成本 Kimi 约为 DS 的 10 倍。Engy 输入上限：超过约 30 万 token 只有 0731（约 92 万）和 Kimi（约 105 万）能装下。只记录，规则留到 Stage 2B |
| 10. capability_need 如何复用 | 跑模型前先用 Jev V3 + 路由视图给每题分类；模型结果按三个档位切片，看相对差距是否随档位稳定变化。不单独出考卷 |
| 11. 推荐执行顺序 | ① 数学、编程（direct）、推理（自动评分，便宜）→ ② 事实问答（GPT-4.1 判卷）→ ③ AutomationBench（东京）→ ④ 写作、研究分析、规划（判卷方案定后）→ ⑤ DeepSWE（沈阳，最后） |

## 上下文原则（9/30 补充）

Stage 2 主实验只在共同可承载的样本上比较模型能力；容量超限样本进入 long-context 专项，不算模型错误。具体规则见 `STAGE2_CONTEXT_POLICY.md`：

- Jev 的 30K 只决定 Jev 看完整请求还是压缩视图，与模型能不能装下无关。
- 每题在调用模型前做容量检查（安全上限 = Engy 实测输入上限 × 0.95），只有所有候选都装得下的题才进入主实验。
- 装不下的题不计错，整题移入长上下文池，保留原 task_type，之后按 task_type 单独比较（超过约 28 万基本只剩 DS 0731 与 Kimi）。
- agentic 任务运行中超出窗口记为 `runtime_context_overflow`，单独统计。
- 模型能不能装下由网关确定性判断，不交给 Jev。

## 公开证据透露的几个值得验证的方向

- **DS 4.1 可能在很多组合里就是答案**：统一测评中数学、数据分析、AutomationBench 第一，推理与编程差距不大，单价只有 Kimi 的约 1/100。风险在事实问答：幻觉率 96.5%。
- **coding + agentic 可能不是 Kimi**：DeepSWE 榜单 GLM-5.3 与 Kimi 几乎持平，Terminal-Bench 4.0 上 Kimi 只有 12.6；GLM-5.3-Flash 以约 1/15 的成本拿到 63.4。
- **Kimi 的优势集中在推理、写作、长上下文**。

## 需要你决定

1. 9/23 实验是否也属于"9/29 之前作废"的范围。
2. 判卷方案：SimpleQA 用 GPT-4.1、WritingBench 与 PlanningBench 用哪个模型、research_analysis 用哪种评分。
3. 候选名单和第一轮题数是否按计划。
4. 是否开始 Stage 2B，以及从哪一步开始。
