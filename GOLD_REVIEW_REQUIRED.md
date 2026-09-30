# Stage 1 gold 人工复核

目的：在写 Prompt V2 之前，先确认争议题的语义 gold，避免 Prompt 过拟合错误的 gold。
建议是在 V2 运行之前写的；请在 `STAGE1_GOLD_REVIEW_REQUIRED.csv` 的 `human_gold` 列填写最终判断。

判断标准服务于 Router：如果将来各模型在这类题上的表现更接近数学题，就允许归 math。

## A. LiveBench spatial / 几何（5 题）

### `livebench_reasoning:4c6e9d7cd2f5506ef5d07f1545dad8d1ca31bfd74ad3ca3e1a6d34accac62db2`

- 子类：reasoning；官方难度：None
- 当前 gold：**reasoning_planning**；Jev V1：**math**（置信度 0.89）
- 为什么可能属于 math：正方体顶点 A、C、G、E 构成什么形状，是标准的立体几何题
- 为什么可能属于 reasoning_planning：LiveBench 把它归为 spatial 推理，考的是空间想象而不是公式推导，不需要计算或证明；按 taxonomy，空间推理属于 reasoning_planning
- 建议：**math**

题目全文：

```
Suppose I have a regular cube. The top face is a square with vertices A, B, C, D, and these four vertices are directly above the vertices E, F, G, H, respectively. If I create a shape whose vertices are exactly A, C, G, E, what is the resulting shape? Is it a square, pentagon, tetrahedron, square pyramid, circle, triangular prism, or sphere? Think step by step, and then put your answer in **bold** as a single phrase (for example, **sphere**). If you don't know, guess.
```

### `livebench_reasoning:6882b248e31a65f287a7a2ab617b31ebfed771511e730697ceb43f0b5a3dd067`

- 子类：reasoning；官方难度：None
- 当前 gold：**reasoning_planning**；Jev V1：**math**（置信度 0.96）
- 为什么可能属于 math：需要用距离和平面位置判断切割面是否碰到正方体或球，属于几何位置关系计算
- 为什么可能属于 reasoning_planning：LiveBench 把它归为 spatial 推理，考的是空间想象而不是公式推导，不需要计算或证明；按 taxonomy，空间推理属于 reasoning_planning
- 建议：**math**

题目全文：

```
Suppose I have a physical, solid unit cube. The top face is a square with vertices A, B, C, D, and these four vertices are directly above the vertices E, F, G, H, respectively. I also have a physical, solid unit sphere, with center J. The cube and sphere are not overlapping, and the three points A, D, J are colinear. The distance between A and J is 10. Let K denote the midpoint of AJ. Now, I make a cut through point K, such that the plane of the cut is orthogonal to AJ. From the original cube and sphere, how many pieces are there now after the cut? Think step by step, and then put your answer in **bold** as a single integer (for example, **0**). If you don't know, guess.
```

### `livebench_reasoning:a0f4b0be2055ef97c455771f2de3eb3f41c9018603d96c93225be734b70dcdce`

- 子类：reasoning；官方难度：None
- 当前 gold：**reasoning_planning**；Jev V1：**math**（置信度 0.92）
- 为什么可能属于 math：正五边形两条对角线切割后的块数，是平面几何计数
- 为什么可能属于 reasoning_planning：LiveBench 把它归为 spatial 推理，考的是空间想象而不是公式推导，不需要计算或证明；按 taxonomy，空间推理属于 reasoning_planning
- 建议：**math**

题目全文：

```
Suppose I have a physical, solid, regular pentagon with vertices ABCDE, and I make two cuts through AC and BD. How many pieces are there after the cuts?  Think step by step, and then put your answer in **bold** as a single integer (for example, **0**). If you don't know, guess.
```

### `livebench_reasoning:e0df6bab9a48ea72072778dc1f8a804810438529347c88b5028b15045b20a203`

- 子类：reasoning；官方难度：None
- 当前 gold：**reasoning_planning**；Jev V1：**math**（置信度 0.96）
- 为什么可能属于 math：切割后三角形的个数，需要识别几何图形
- 为什么可能属于 reasoning_planning：LiveBench 把它归为 spatial 推理，考的是空间想象而不是公式推导，不需要计算或证明；按 taxonomy，空间推理属于 reasoning_planning
- 建议：**math**

题目全文：

```
Suppose I have a physical, solid, regular pentagon with vertices ABCDE, and I make two cuts through AC and BD. Of the resulting pieces, how many triangles are there? Think step by step, and then put your answer in **bold** as a single integer (for example, **0**). If you don't know, guess.
```

### `livebench_reasoning:f8e84ee53942b7e6881fd483a404f6d2c875e816fd79f07cf4181d5d0e3a5b31`

- 子类：reasoning；官方难度：None
- 当前 gold：**reasoning_planning**；Jev V1：**math**（置信度 1.00）
- 为什么可能属于 math：带约束的最大块数，是组合几何中的经典极值问题
- 为什么可能属于 reasoning_planning：LiveBench 把它归为 spatial 推理，考的是空间想象而不是公式推导，不需要计算或证明；按 taxonomy，空间推理属于 reasoning_planning
- 建议：**math**

题目全文：

```
Suppose I have a regular heptagon, and I can make four straight cuts. Each cut cannot pass through any of the vertices of the heptagon. Also, exactly three of the cuts must intersect at a single point within the heptagon. What is the maximum number of resulting pieces? Think step by step, and then put your answer in **bold** as a single integer (for example, **0**). If you don't know, guess.
```

## B. WritingBench（2 题）

### `writingbench:26`

- 子类：Academic & Engineering/Conclusion；官方难度：None
- 当前 gold：**writing_language**；Jev V1：**research_analysis**（置信度 0.98）
- 支持现有 gold（writing_language）：没有给定任何材料，靠已有知识写一篇总结分析文章；按 taxonomy，research_analysis 要求综合给定材料，所以更接近写作
- 支持改为其他类别：题目明确要求'分析'和'比较'，现行 Prompt 的 research_analysis 描述里有 'producing research-style analysis'，与 taxonomy 定义不一致
- 建议：**writing_language（低把握）**

题目全文：

```
Summarize the main experiences and lessons of artificial intelligence transitioning from the laboratory to industrial implementation in the past five years. Analyze from both the perspectives of technical researchers and engineering practitioners, comparing the differences and contradictions between academic research and engineering applications.
```

### `writingbench:425`

- 子类：Advertising & Marketing/Slogans；官方难度：None
- 当前 gold：**writing_language**；Jev V1：**reasoning_planning**（置信度 0.79）
- 支持现有 gold（writing_language）：WritingBench 把它归为广告语写作，产出主要是广告语
- 支持改为其他类别：题目同时要求'具体的推广策划方案'，有明确目标、周期、地区、受众等约束，这部分是 reasoning_planning
- 建议：**有歧义，建议单列不计入准确率**

题目全文：

```
Based on the requirements here and 1. Advertised Product
Guangdong Liangwei Beverage Company - Liangwei Beverage

2. Advertising Objectives
1) Establish Liangwei Beverage's product image and positioning
2) Attract customers to purchase through advertising placement
3) Communication impact progression: Unknown - Known - Understood - Convinced - Action

3. Advertising Period
November 20XX - May 20XX

4. Advertising Region
Nationwide (primarily urban areas)

5. Target Audience
All residential consumers, especially young people living away from home, help me design advertising slogans and specific promotional planning solutions that incorporate local characteristics and take a people-friendly approach
```

## C. LongBench v2 成功题中的错误（3 题）

### `longbench_v2:66ed2c87821e116aacb1f149`

- 子类：Table QA；官方难度：easy
- 当前 gold：**research_analysis**；Jev V1：**general_qa**（置信度 0.36）
- 支持 research_analysis：需要读懂论文中的表 1 并判断收入与受霸凌程度的关系能否成立，属于表格分析
- 支持 Jev 的判断：只涉及一张表，接近查表；Jev 判为 general_qa
- 建议：**research_analysis（低把握）**

题目全文（完整输入 60,873 字符，这里只列问题和选项；材料开头：.

<text>
Original Paper
Effects of Bullying on Anxiety, Depression, and Posttraumatic
Stress Disorder Among Sexual Minority Youths: Network Analysis
1School of Psychology, South China Normal Universi …）：

```
What is the correct answer to this question: From the table 1, with the increase of current annual income, people who is LGBT can suffer less from bullying?
Choices:
(A) From the table 1, we can conclude that all people of LGBT will suffer less from campus bullying with more annual income under 3565, but when the income exceeds this number, the victims of bullying increase.
(B) From the table 1, we can conclude that all people of LGBT will suffer less from campus bullying with more annual income.
(C) From the table 1, we can conclude that only sexual minority youths will suffer less from campus bullying with more annual income.
(D) Based on Table 1 in the provided document, we cannot conclude that people who identify as LGBT+ suffer less from bullying as their annual income increases.

Format your response as follows: "The correct answer is (insert answer here)".
```

### `longbench_v2:66f8c6b4bb02136c067c4480`

- 子类：Multi-news；官方难度：hard
- 当前 gold：**research_analysis**；Jev V1：**math**（置信度 0.69）
- 支持 research_analysis：要从多份人道主义报告里汇总三个时间段的死亡和受伤人数，再按天折算比较，属于多文档数据整合
- 支持 Jev 的判断：核心步骤是算术（除以天数、比较），Jev 判为 math
- 建议：**research_analysis**

题目全文（完整输入 59,812 字符，这里只列问题和选项；材料开头：.

<text>
30 Aug 2024
A vehicle of the World Food Programme shot at while approaching an Israeli checkpoint after escorting aid trucks in Gaza.
Photo by WFP
The Humanitarian Situation Update is issued …）：

```
What is the correct answer to this question: Among these three durations: 
duration A: 28 June 2024 to 29 July 2024
duration B: 30 July 2024 to 29 August 2024
duration C: 30 August 2024 to 22 September 2024
I wanna find out  which duration(month)  has the worst situation in terms of Palestinians deaths per day and injuries per day.
Choices:
(A) duration A has the largest number of deaths per day, duration C has the largest number of injuries per day.
(B) duration B has the largest number of deaths per day, duration B has the largest number of injuries per day.
(C) duration A has the largest number of deaths per day, duration A has the largest number of injuries per day.
(D) duration C has the largest number of deaths per day, duration B has the largest number of injuries per day.

Format your response as follows: "The correct answer is (insert answer here)".
```

### `longbench_v2:66fb5f73bb02136c067c7ae7`

- 子类：Multi-news；官方难度：hard
- 当前 gold：**research_analysis**；Jev V1：**general_qa**（置信度 0.41）
- 支持 research_analysis：要综合 AbbVie 半年内多篇新闻稿，判断哪些事件对战略和运营影响重大，是典型的多文档综合
- 支持 Jev 的判断：Jev 判为 general_qa；选项里的事实可逐条核对，但需要跨文档比对
- 建议：**research_analysis**

题目全文（完整输入 78,425 字符，这里只列问题和选项；材料开头：.

<text>
AbbVie News Center
AbbVie Completes Acquisition of Cerevel Therapeutics
Cerevel's clinical-stage assets complement AbbVie's emerging neuroscience pipeline and leading on-market brands in psy …）：

```
What is the correct answer to this question: Based on the corporate news released by AbbVie in the past six months, What events have happened with a significant impact on the company's strategy and operations?
Choices:
(A) The company has been continuously consolidating its ability to innovate sustainably by establishing strategic cooperation relationships. It has partnered with OSE Immunotherapeutics, Tentarix Biotherapeutics, Gilgamesh Pharmaceuticals, and other companies to develop products in the field of immunology, including specific biological drugs and neuroplastogens.
(B) Through continuous acquisition and restructuring strategies, the company has continuously expanded and enriched its product pipeline. Over the past six months, the company has completed three acquisitions to enhance its neuroscience pipeline, oncology pipeline, and immunology pipeline.
(C) The company has experienced several executive personnel changes and organizational adjustments. Effective July 1, 2024, Richard A. Gonzalez succeeded Robert A. Michael as the new CEO of the company; at the same time, Dr. Roopal Thakkar was appointed as the Executive Vice President, responsible for the therapeutic and aesthetic business segments, as well as Research and Development and Chief Scientific Officer.
(D) The company has received FDA approval for multiple drugs to treat a range of indications. For example, Elahere is used to treat adult cancer patients with folate receptor alpha (FRα) positive, platinum-resistant epithelial ovarian, fallopian tube, or primary peritoneal cancer, Epkinly is used to treat adult patients with relapsed or refractory (R/R) follicular lymphoma (FL), and Juvederm Voluma XC is used to improve moderate to severe temporal hollowing in adults over the age of 21.

Format your response as follows: "The correct answer is (insert answer here)".
```

## D. AutomationBench 在 7 类下的 gold（30 题，V2 运行前登记）

Stage 1 里这 30 题按 6 类判断，25 题归不进任何一类。V2 增加 workflow_operation 后，需要事先登记新的 gold。
判断依据：任务的核心目标是不是通过工具读取并改变外部系统状态来完成业务流程。execution_mode 全部是 agentic。

| 题目 | 领域 | Stage 1 判断 | 建议 7 类 gold | 说明 |
|---|---|---|---|---|
| `automationbench:finance:4038` | finance | uncovered / None | **workflow_operation** | 读取并更新 CRM、表格、邮件、Slack 等外部系统，按业务规则执行流程 |
| `automationbench:finance:4049` | finance | ambiguous / research_analysis | **workflow_operation** | 读取并更新 CRM、表格、邮件、Slack 等外部系统，按业务规则执行流程 |
| `automationbench:finance:4067` | finance | ambiguous / research_analysis | **workflow_operation** | 读取并更新 CRM、表格、邮件、Slack 等外部系统，按业务规则执行流程 |
| `automationbench:finance:4095` | finance | uncovered / None | **workflow_operation** | 读取并更新 CRM、表格、邮件、Slack 等外部系统，按业务规则执行流程 |
| `automationbench:hr:5028` | hr | ambiguous / writing_language | **workflow_operation** | 要逐个核对薪资带宽和审批例外，再在 Gmail 里建草稿，评分看流程是否合规；与 writing_language 有歧义 |
| `automationbench:hr:5088` | hr | uncovered / None | **workflow_operation** | 读取并更新 CRM、表格、邮件、Slack 等外部系统，按业务规则执行流程 |
| `automationbench:hr:5108` | hr | uncovered / None | **workflow_operation** | 读取并更新 CRM、表格、邮件、Slack 等外部系统，按业务规则执行流程 |
| `automationbench:hr:5124` | hr | uncovered / None | **workflow_operation** | 读取并更新 CRM、表格、邮件、Slack 等外部系统，按业务规则执行流程 |
| `automationbench:marketing:1033` | marketing | uncovered / None | **workflow_operation** | 读取并更新 CRM、表格、邮件、Slack 等外部系统，按业务规则执行流程 |
| `automationbench:marketing:1045` | marketing | clean / research_analysis | **research_analysis** | 核心是分析内容清单并给出优先级建议，写回或发送只是交付方式；与 workflow_operation 有歧义 |
| `automationbench:marketing:1128` | marketing | uncovered / None | **workflow_operation** | 读取并更新 CRM、表格、邮件、Slack 等外部系统，按业务规则执行流程 |
| `automationbench:marketing:1167` | marketing | uncovered / None | **workflow_operation** | 读取并更新 CRM、表格、邮件、Slack 等外部系统，按业务规则执行流程 |
| `automationbench:operations:1202` | operations | uncovered / None | **workflow_operation** | 读取并更新 CRM、表格、邮件、Slack 等外部系统，按业务规则执行流程 |
| `automationbench:operations:1219` | operations | uncovered / None | **workflow_operation** | 读取并更新 CRM、表格、邮件、Slack 等外部系统，按业务规则执行流程 |
| `automationbench:operations:1322` | operations | uncovered / None | **workflow_operation** | 读取并更新 CRM、表格、邮件、Slack 等外部系统，按业务规则执行流程 |
| `automationbench:operations:1354` | operations | ambiguous / research_analysis | **workflow_operation** | 读取并更新 CRM、表格、邮件、Slack 等外部系统，按业务规则执行流程 |
| `automationbench:sales:1112` | sales | uncovered / None | **workflow_operation** | 读取并更新 CRM、表格、邮件、Slack 等外部系统，按业务规则执行流程 |
| `automationbench:sales:3` | sales | uncovered / None | **workflow_operation** | 读取并更新 CRM、表格、邮件、Slack 等外部系统，按业务规则执行流程 |
| `automationbench:sales:528` | sales | uncovered / None | **workflow_operation** | 读取并更新 CRM、表格、邮件、Slack 等外部系统，按业务规则执行流程 |
| `automationbench:sales:838` | sales | uncovered / None | **workflow_operation** | 读取并更新 CRM、表格、邮件、Slack 等外部系统，按业务规则执行流程 |
| `automationbench:simple:3051` | simple | uncovered / None | **workflow_operation** | 读取并更新 CRM、表格、邮件、Slack 等外部系统，按业务规则执行流程 |
| `automationbench:simple:3093` | simple | uncovered / None | **workflow_operation** | 读取并更新 CRM、表格、邮件、Slack 等外部系统，按业务规则执行流程 |
| `automationbench:simple:3166` | simple | uncovered / None | **workflow_operation** | 读取并更新 CRM、表格、邮件、Slack 等外部系统，按业务规则执行流程 |
| `automationbench:simple:3169` | simple | uncovered / None | **workflow_operation** | 读取并更新 CRM、表格、邮件、Slack 等外部系统，按业务规则执行流程 |
| `automationbench:simple:3188` | simple | uncovered / None | **workflow_operation** | 读取并更新 CRM、表格、邮件、Slack 等外部系统，按业务规则执行流程 |
| `automationbench:simple:3200` | simple | uncovered / None | **workflow_operation** | 读取并更新 CRM、表格、邮件、Slack 等外部系统，按业务规则执行流程 |
| `automationbench:support:1426` | support | uncovered / None | **workflow_operation** | 读取并更新 CRM、表格、邮件、Slack 等外部系统，按业务规则执行流程 |
| `automationbench:support:1447` | support | uncovered / None | **workflow_operation** | 读取并更新 CRM、表格、邮件、Slack 等外部系统，按业务规则执行流程 |
| `automationbench:support:1472` | support | uncovered / None | **workflow_operation** | 读取并更新 CRM、表格、邮件、Slack 等外部系统，按业务规则执行流程 |
| `automationbench:support:1479` | support | uncovered / None | **workflow_operation** | 读取并更新 CRM、表格、邮件、Slack 等外部系统，按业务规则执行流程 |

## E. 不需要复核的

SimpleQA Verified 中 5 道被 Jev V1 判为 agentic 的题，gold 仍为 direct：题目只要求回答一个事实，没有要求操作任何外部环境。
