# Stage 1.5 实验 B：超过 30K 的请求给 Jev 看什么（2026-09-30）

对象：Stage 1 中 25 道完整输入超出 Jev 上限的 LongBench v2 题，不换题、不补题、不删题。Prompt V2 冻结。脚本 `scripts/stage1_5_routing_view.py`，结果 `stage1_5/routing_view_{B,C}_results.jsonl`。

只研究 Jev 看到什么；真正做题的模型始终接收完整原始输入。

## 三种路由视图

| 方案 | Jev 看到的内容 | 大小（Jev 计数，中位 / 最大） |
|---|---|---|
| A 只给问题（已有结果，未重跑） | 完整问题和选项 + 原文长度 + "材料作为附件"的说明 | 1,871 / 2,121 |
| B 代表性采样 | 完整问题和选项 + 元数据（原文估算 token、模态） + 材料开头、中间、结尾各约 2K token | 6,056 / 13,438 |
| C 多段采样 | 同上，但从材料的 0%、25%、50%、75%、100% 五个位置各取约 1.3K token | 6,329 / 14,705 |

B、C 的共同规则：采样位置和长度固定，所有题用同一算法；不给 benchmark 名称、类别、子领域等标签；最大视图约 1.5 万 token，低于 30,000 安全线。部分中文材料的视图比 8–12K 的目标略大，因为估算对中文偏保守。

## 结果

| 方案 | task_type 正确 | research_analysis 召回 | 其他判断 | execution_mode |
|---|---|---|---|---|
| A 只给问题 | 14 / 25 = 56% | 14 / 25 | general_qa 10、reasoning_planning 1 | 25 / 25 direct |
| B 代表性采样 | 13 / 25 = 52% | 13 / 25 | general_qa 8、reasoning_planning 3、math 1 | 25 / 25 direct |
| C 多段采样 | 14 / 25 = 56% | 14 / 25 | general_qa 8、reasoning_planning 3 | 25 / 25 direct |

| 其他指标 | A | B | C |
|---|---|---|---|
| 延迟中位 / 最大 | — | 227 / 616 ms | 219 / 624 ms |
| capability_need | 15 strong、10 standard | 15 strong、10 standard | 17 strong、8 standard |
| 25 次费用 | $0.0020 | $0.0065 | $0.0070 |

B 与 C 的逐题判断几乎相同（只有 1 题从 math 变为 research_analysis）；B 与 A 相比，有 2 题从 general_qa 变对，但也有 3 题从对变错。research_analysis 判对的题，置信度从 0.37 到 0.95，分布很散。

## 关键对照：完整输入时这类题也分不准

同一 benchmark 中完整输入没有超限的 5 道 LongBench 题（Stage 1 / V2 成功调用），V2 只判对 1 题：

| 题目 | V2 判断 | 置信度 |
|---|---|---|
| 表 1 能否推出收入与霸凌的关系 | general_qa | 0.41 |
| 三个时间段伤亡比较 | math | 0.56 |
| （判对） | research_analysis | 0.60 |
| AbbVie 半年新闻 | general_qa | 0.62 |
| 非洲清洁炊具结论 | general_qa | 0.32 |

也就是说，**Jev 看到全部材料时，这类题的准确率是 1/5，并不比压缩视图的 52–56% 好**。问题不在于"压缩后看不到关键信息"，而在于 Jev 对"根据给定材料回答选择题"这类任务的归类，本身就和我们的 gold 不一致：它倾向于判为 general_qa。

## 结论

1. 在当前 Prompt V2 下，**任何一种路由视图都不能让这类题的分类变可靠**：三种方案都在 52–56%，属于方案里"明显不够"的区间。
2. 瓶颈不是截断或采样方式，而是类别定义：LongBench 这类"给定长材料 + 选择题"的任务，Jev 认为是 general_qa，我们的 gold 是 research_analysis。要提升，应先确认这类任务到底该归哪一类，并在 Prompt 里写清 general_qa 与 research_analysis 的边界（例如"答案依赖给定材料而非常识"），而不是继续调整采样。按本阶段规则，Prompt V2 与 gold 都未修改。
3. 按方案的决策规则，超长请求在生产 V1 中**暂不使用 Jev 语义路由**，走长上下文兜底（`overflow_fallback`）。
4. execution_mode 在三种视图下都稳定（全部 direct，正确）。
5. 局限：只有 25 题，且全部来自 LongBench v2 一个来源，材料类型单一。

## Jev 用量

| 方案 | 调用 | 输入 tokens | 输出 tokens | 费用 |
|---|---|---|---|---|
| B | 25 | 155,488 | 3,719 | $0.0065 |
| C | 25 | 166,277 | 3,720 | $0.0070 |

费用按输入 $0.042 / 百万 token 计算，输出单价未公开未计入。A 为已有结果，本阶段未重跑。
