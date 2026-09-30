# Stage 2A：各组合状态（2026-09-30）

状态定义：**RESOLVED** 已有证据足以确定；**SCREENING_NEEDED** 知道大致候选，需小样本验证；**EVIDENCE_MISSING** 几乎没有可比证据；**BENCHMARK_MISSING** 缺合适的 benchmark 或评分方式。

**以下状态都是针对 normal context 的比较**：只在该组合所有候选都装得下的题上比较模型能力（规则见 `STAGE2_CONTEXT_POLICY.md`）。长上下文单独列在文末。

**没有任何组合是 RESOLVED**：公开证据都只是 B 级（厂商 API 全精度、不同 harness），本项目在 Engy 上没有任何一组"同一 benchmark、同一设置、多个候选"的 A 级对比。

| 组合 | 状态 | 最值得测的候选 | 依据（B 级） | 缺什么 |
|---|---|---|---|---|
| general_qa + direct | SCREENING_NEEDED | kimi-k3、deepseek-v4.1-flash、glm-5.3-flash | AA-Omniscience：Kimi 与 DS 4.1 准确率相近（47.6 / 46.4），但 DS 幻觉率 96.5%；GLM 系列幻觉最低但准确率低 | 没有候选的 SimpleQA 成绩；需决定计分是否惩罚"答错"而非"不答"；官方判卷为 GPT-4.1 |
| writing_language + direct | BENCHMARK_MISSING（评分） | kimi-k3、glm-5.3、deepseek-v4.1-flash、glm-5.3-flash | EQ-Bench：Kimi 与 GLM-5.3 远高于 DS；LiveBench 语言：Kimi 最高，GLM-Flash 指令遵循弱 | WritingBench 需要 LLM 判卷（官方推荐 Claude-3.7-Sonnet 或其 7B 评分模型），需决定判卷方案 |
| math + direct | SCREENING_NEEDED | deepseek-v4.1-flash、kimi-k3、glm-5.3-flash | LiveBench 数学 DS 4.1 第一（93.3 vs Kimi 84.4）；9/23 本地 B 级：DS 94.3 ≈ Kimi 94.7 | 候选都没有 AIME / MATH-500 统一成绩 |
| reasoning_planning + direct | SCREENING_NEEDED | kimi-k3、deepseek-v4.1-flash、glm-5.3 | Kimi 在 HLE、LiveBench 推理领先；DS 4.1 在 LiveBench 推理差 4 分 | 规划（planning）子类没有公开证据；PlanningBench 需按检查清单 LLM 判卷，判卷模型未指定 |
| coding + direct | SCREENING_NEEDED | kimi-k3、deepseek-v4.1-flash、glm-5.3、glm-5.3-flash | LiveBench 编程四者差 2.4 分以内；AA SciCode Kimi ≈ GLM 领先 DS 约 7 分；9/23 本地：DS 83.9 vs Kimi 86.3（不开推理） | LiveCodeBench 统一成绩 |
| research_analysis + direct | BENCHMARK_MISSING（评分） | deepseek-v4.1-flash、kimi-k3、glm-5.3-flash | LiveBench 数据分析：DS 4.1 = 0731 79.3 ≥ Kimi 78.7 > Flash 76.4 > GLM 70.2 | Stage 1.7 的 research 题是分类考卷，没有可自动评分的答案；TableBench 数据分析题是开放式回答，官方评分方式待核实 |
| coding + agentic | SCREENING_NEEDED | glm-5.3、kimi-k3、deepseek-v4.1-flash、glm-5.3-flash | DeepSWE 榜单：GLM 69.0 ≈ Kimi 68.5 > Flash 63.4 >> 0731 53.3；DS 4.1 未上榜（自报 74.2，自有 harness）；AA TB4.0：GLM 41.9 > Flash 32.8 > DS 4.1 26.8 >> Kimi 12.6 | 在 Engy 上用同一 harness 的对比；DS 4.1 的第三方成绩 |
| workflow_operation + agentic | SCREENING_NEEDED | deepseek-v4.1-flash、glm-5.3、glm-5.3-flash（kimi-k3 作参照可选） | AA AutomationBench：DS 4.1 68.9 > GLM 62.2 > Flash 60.4 > Kimi 58.3；厂商自报的数字互相矛盾 | 在 Engy 上用官方 runner 的对比 |
| reasoning_planning + agentic | BENCHMARK_MISSING | — | 无 | 没有合适的 benchmark，本阶段不测 |

## 各模型是否需要测

| 模型 | 结论 |
|---|---|
| deepseek-v4.1-flash | 所有组合都测：最便宜，且多项统一测评领先 |
| kimi-k3 | 大多数 direct 组合作为质量上限参照；coding + agentic 需要测；workflow 可选 |
| glm-5.3 | coding + agentic、workflow、推理、编程、写作 |
| glm-5.3-flash | 作为便宜的第二候选：agentic 两组、编程、事实问答、数学 |
| deepseek-v4-flash-0731 | 短请求组合**不测**：几乎所有测评都低于 DS 4.1，价格反而略高。只在长上下文（Engy 输入上限约 92 万，DS 4.1 只有 26 万）时有价值 |
| qwen3.6-35b-a3b | **不测**：AutomationBench 5.2、TB4.0 为 0、HLE 22.2 |
| qwen3.8-27b | 暂不测；它自报 LiveCodeBench 90.3，若 coding + direct 结果接近再考虑加入 |

## 长上下文（单独的实验线，只记录，不定规则）

长上下文不是 task_type，而是请求属性。Stage 2B 跑 normal context 实验时，任何因容量被排除的题都移入 `long_context_pool`，按 task_type、execution_mode、长度区间、可装下的模型分组，之后单独比较。当前各模型的安全上限（Engy 实测 × 0.95）：GLM-5.3-Flash 217,907、DS 4.1 249,037、GLM-5.3 280,166、DS 0731 874,547、Kimi 约 996,147。

| 证据 | 内容 |
|---|---|
| AA-LCR（B 级） | Kimi 88.7 > DS 4.1 84.0 > Qwen3.8 82.0 > GLM-Flash 80.0 ≈ DS 0731 79.7 = GLM 79.7 |
| AA-LCR 单题成本 | DS 4.1 $0.032、0731 $0.048、Kimi $0.309、GLM $0.149、Flash $0.017 |
| Engy 输入上限 | DS 4.1 26.2 万、GLM-Flash 22.9 万、GLM 29.5 万、0731 约 92 万、Kimi 约 105 万 |

也就是说：超过约 30 万 token 时只有 0731 和 Kimi 能装下；AA-LCR 上 Kimi 高 9 分，但单题成本约 6 倍。这些留到 Stage 2B 用模型实验决定。
