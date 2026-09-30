# Stage 2B 实验计划（草案，待确认，尚未运行）

## 1. 通用规则

| 项目 | 规则 |
|---|---|
| 题目 | 固定随机种子抽样，保存题号；同一 benchmark 的所有候选模型做**同一批题** |
| 调用参数 | 只传 `reasoning_effort=max`，不传温度、top_p、max_tokens（由网关用模型最大值；DS 4.1 在 Engy 上最大输出 65,536）。与 DeepSWE 榜单做法一致 |
| 超时 | direct 题单题 1,800 秒（DS 在高负载下约 20 token/s，600 秒会大量超时）；agentic 用 benchmark 官方时限；超时单独记录，最后列给你决定 |
| 失败 | 网络、429、5xx 等失败整题重跑，不计入成绩 |
| 评分 | 官方评分方式；需要 LLM 判卷的，同一 benchmark 所有模型用同一个判卷模型 |
| agentic | 同一 benchmark 版本、同一题、同一 agent、同一工具、同一最大步数、同一判卷、同一超时，只换底层模型 |
| 每题记录 | task_id、task_type、execution_mode、capability_need（Jev V3 + 路由视图，跑模型之前先分类）、model、score / passed、cost、input_tokens、output_tokens、latency、timeout、hard_failure、agent_steps、benchmark、benchmark_version |
| 选型规则 | 设最高分为 Smax：若某便宜模型的分数 ≥ Smax − 1（满分尺度的 1 个百分点），且成本比最高分模型低 ≥ 20%，选便宜模型；否则选最高分模型；质量和成本都接近时再看延迟 |
| 统计 | 候选之间做逐题配对：报告胜 / 负 / 平和配对 bootstrap 95% 置信区间；只差一两题时不下结论 |
| 花费 | Engy 和 Jev 的花费全部记录进结果和报告 |

**扩样与停止（各 direct 组合通用）**：第一轮 20 题。若最便宜的候选与最高分之差的 95% 置信区间与"±1 分"区间有重叠，或差距在 5 分以内，则扩到 50 题；若差距超过 10 分且置信区间不跨 0，则停止。agentic 第一轮 10–15 题，差距接近时再扩。

## 2. 各组合的实验

| 组合 | benchmark 与题数（第一轮） | 候选 | 评分 | 调用数 | 预计 Engy 费用 | 预计时间 |
|---|---|---|---|---|---|---|
| math + direct | MATH-500 按 1–5 级分层 10 题 + LiveBench 数学 10 题 | DS 4.1、Kimi K3、GLM-5.3-Flash | MATH-500 答案匹配；LiveBench 官方自动评分 | 60 | 约 $2 | 约 1 小时 |
| coding + direct | LiveCodeBench 最新两批（v5、v6），按难度 × 平台分层 20 题 | DS 4.1、Kimi K3、GLM-5.3、GLM-5.3-Flash | 官方测试用例执行（只下载所选题的测试数据） | 80 | 约 $3.5 | 约 1.5 小时 |
| reasoning_planning + direct | LiveBench 推理 10 题（子类 reasoning）+ PlanningBench 10 题（子类 planning） | Kimi K3、DS 4.1、GLM-5.3 | LiveBench 自动评分；PlanningBench 按检查清单由 LLM 判卷（判卷模型待定） | 60 | 约 $2–3 | 约 1 小时 |
| general_qa + direct | SimpleQA Verified 20 题（按主题分层） | Kimi K3、DS 4.1、GLM-5.3-Flash | 官方判卷为 GPT-4.1（可经 OpenRouter 调用）；同时报告"答对率"和"答错率"，因为 DS 4.1 幻觉率很高 | 60 + 60 判卷 | 约 $0.6 | 约 30 分钟 |
| writing_language + direct | WritingBench 纯写作子集 20 题 | Kimi K3、GLM-5.3、DS 4.1、GLM-5.3-Flash | 官方 rubric + LLM 判卷（官方推荐 Claude-3.7-Sonnet，或官方 7B 评分模型；需你决定） | 80 + 80 判卷 | 约 $1.2 + 判卷约 $2–3 | 约 1 小时 |
| research_analysis + direct | 需先定评分方式（见第 3 节） | DS 4.1、Kimi K3、GLM-5.3-Flash | 待定 | 60 | 约 $1–2 | 约 1 小时 |
| workflow_operation + agentic | AutomationBench 公开集 15 题（6 个业务领域覆盖） | DS 4.1、GLM-5.3、GLM-5.3-Flash；Kimi K3 作参照（可选） | 官方 runner 与断言判分（api 工具集、最多 50 步） | 45–60 个任务 | 约 $3–7 | 约 1 小时（东京） |
| coding + agentic | DeepSWE v1.1 12 题 | GLM-5.3、Kimi K3、DS 4.1、GLM-5.3-Flash | 官方 harness mini-swe-agent（Pier）+ 官方判卷；每题 2 核 8 GB、agent 时限 3 小时 | 48 个任务 | 约 $26–150（取决于 Engy 是否按缓存价计费；每题输入约 350 万 token，98% 可命中缓存） | 约 6–8 小时（沈阳，并发 4–6） |

费用估算方法：按 Engy 当前单价，假设最高推理档每题输出约 2K（事实问答）到 10–15K（数学、编程）token，输入 2–5K token；agentic 按 9/27–28 的实测单题 token 量。实际以运行记录为准。

## 3. 需要你先决定的评分问题

| 问题 | 选项 |
|---|---|
| SimpleQA 判卷 | 用 OpenRouter 上的 GPT-4.1（与官方一致）；需要确认 OpenRouter 可用的具体版本 |
| WritingBench 判卷 | (a) Claude（经 OpenRouter，与官方推荐一致）；(b) 官方 7B 评分模型，需要 GPU 部署。所有候选必须用同一个判卷 |
| PlanningBench 判卷 | README 没写判卷模型；建议与 WritingBench 用同一个判卷模型 |
| research_analysis 评分 | (a) LiveBench 数据分析（自动评分，但更偏表格处理，不完全是"分析推断"）；(b) TableBench 数据分析题 + LLM 判卷（与参考答案比较）；(c) 两者都用。Stage 1.7 的考卷只有分类标签，不能直接用来评分 |

## 4. 执行顺序

1. **math、coding + direct、reasoning（LiveBench 部分）**：自动评分，便宜，最快出结论。
2. **general_qa**：需要 GPT-4.1 判卷。
3. **workflow_operation + agentic**：在东京跑 AutomationBench。
4. **writing、research、planning**：等判卷方案定下后再跑。
5. **coding + agentic（DeepSWE）**：最贵、最慢，需要在沈阳跑，放在最后；按沈阳的规则并发从 4 起，盯住视频 worker 日志。

## 5. 最少规模

第一轮：direct 6 个组合约 20 题 × 3–4 个模型 ≈ **400 次模型调用**（另加约 200 次判卷）；agentic 2 个组合 ≈ **约 100 个任务**。

| 部分 | 第一轮费用 | 第一轮时间 |
|---|---|---|
| direct（6 组） | 约 $12–15（含判卷） | 约 5–6 小时（可部分并行） |
| AutomationBench | 约 $3–7 | 约 1 小时 |
| DeepSWE | 约 $26–150 | 约 6–8 小时 |
| **合计** | **约 $40–170** | **约 1–1.5 天** |

若需要扩样，最坏情况费用约为第一轮的 2–2.5 倍。

## 6. capability_need 如何复用同一批数据

每道题在跑模型之前先用 Jev（V3 + 路由视图）分类一次，记录 capability_need。模型跑完后按 standard / strong / frontier 切片，看各档位下模型之间的相对差距是否稳定变化。如果某个组合在 frontier 档里便宜模型明显落后、而在 standard 档里追平，capability_need 才有进入 Policy 的价值。不为此单独设计考卷。
