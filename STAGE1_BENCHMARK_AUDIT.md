# Stage 1 Benchmark 审计（Jev Auto Router 实验）

编写日期 2026-09-30。本文配套 `STAGE1_CLASSIFICATION_SET.jsonl`（230 行）。编写过程中没有调用任何模型 API、没有调用 Jev API，也没有登录服务器。所有数据都来自本机 `raw/`；本次新增的核实只访问了官方 GitHub 仓库（LiveBench、LiveCodeBench、THUDM/LongBench、hendrycks/math、openai/prm800k）和 arXiv。

## 0. 范围与复现

**暂定分类体系**
- task_type 共 6 类：`general_qa`、`writing_language`、`math`、`reasoning_planning`、`coding`、`research_analysis`。不再设 `workflow_operation` 和 `planning_design`。
- execution_mode 分两种：
  - `direct`：一次回答，或普通多轮对话，不会持久改变外部环境。
  - `agentic`：必须调用工具、执行命令、修改文件、SaaS 或环境，观察结果后再继续。任务复杂不等于 agentic。

**复现**

```
/root/bench/hle-venv/bin/python scripts/build_stage1.py      # 写出 STAGE1_CLASSIFICATION_SET.jsonl
/root/bench/hle-venv/bin/python scripts/validate_stage1.py   # 校验，含重建哈希比对
```

- 随机种子固定为 `20260929`。每次抽样都新建一个 `random.Random(20260929)`，抽样前先对样本池排序，输出按 `id` 排序，因此重建结果逐字节相同。
- 当前文件 sha256 前缀为 `8d8a69cd14824c87`。
- AutomationBench 的 task_name 和断言类型由 `scripts/automationbench_task_meta.py` 生成，需要用 AutomationBench 的 venv 运行，输出到 `raw/automationbench/task_meta.jsonl`。脚本只加载任务定义，不运行模型。
- 逐题判断写在 `scripts/stage1_ab_judgements.py`。

**字段约定**
- `official_difficulty` 只放官方难度字段归一化后的值：
  - LiveCodeBench：`easy`/`medium`/`hard`
  - MATH-500：`level_1`…`level_5`
  - LongBench v2：`easy`/`hard`
  - 其他一律为 null。
- `official_difficulty_raw` 逐字保留官方字段和难度因素，例如 LongBench 的 `length`，SimpleQA 的 `multi_step` 和 `requires_reasoning`，LiveBench 的 `hardness` 和 `level`。
- 没有任何难度是推测出来的。

**文件规模**：文件约 28 MB，其中 26.5M 字符来自 30 条 LongBench 的完整上下文（见 §2.6）。提交进 git 前请确认可以接受这个体积。

## 1. 总表

| task_type | 推荐 benchmark（本次用量） | 纯度 | 官方难度字段 | 模式 | 主要局限 |
|---|---|---|---|---|---|
| general_qa | SimpleQA Verified（30） | 很高 | 无难度字段。只有元数据标志 `multi_step`、`requires_reasoning`（保留在 raw） | direct | 全是长尾、难度高的事实题，没有“简单常识”题 |
| writing_language | WritingBench（30，30 个不同的 domain2） | 过滤后高 | 无 | direct | 没有翻译或改写类子域；5 条 query 超过 5K 字符 |
| math | MATH-500（20）+ LiveBench math（10） | 很高 | MATH-500 `level`（1–5）；LiveBench `hardness`（仅 olympiad，语义未公开） | direct | MATH 污染和饱和严重；LiveBench HF 快照停在 2025-04 |
| reasoning_planning | LiveBench reasoning（15，subtype=reasoning）+ PlanningBench（15，subtype=planning） | 高 | LiveBench `level`（仅 zebra，语义未公开）；PlanningBench 无 | direct | reasoning 只有 3 个模板化题族；PlanningBench 全是中文，且没有类别字段 |
| coding | LiveCodeBench code_generation_lite `test6.jsonl`（30） | 很高（范围窄） | `difficulty`（easy/medium/hard） | direct | 只有竞赛编程；test6 只含 leetcode 和 atcoder |
| research_analysis | LongBench v2 过滤池（30） | 中高（人工复核过） | `difficulty`（easy/hard）+ `length`（short/medium/long） | direct | 全是四选一选择题，上下文极长；池子只有 99 题 |
| （mode 集）coding + agentic | DeepSWE v1.1（20） | 100% coding | 无 | agentic | 首请求按 mini-swe-agent 重建（§3.1） |
| （mode 集）AutomationBench | 公开集 6 个域 × 4 + simple 6（30） | 见 §4：只有 1/30 是 clean | 无（simple 是域，不是难度） | agentic | 25/30 在 6 类中找不到对应（uncovered） |

计数：
- clean 集 180 条，每类 30，全部 direct。
- mode 集 50 条，全部 agentic。按 task_type 分：coding 20、research_analysis 4、writing_language 1、null 25。

## 2. 各类详细

### 2.1 general_qa — SimpleQA Verified

- **来源**：HF `google/simpleqa-verified`，文件 `simpleqa_verified.csv`，共 1000 行。`task_id` 取 `original_index`。
- **抽样**：
  - 先排除 `requires_reasoning=True` 的 37 题（这些题更接近 reasoning 边界），样本池剩 963 题。
  - 每个 `topic` 抽 3 题（共 10 个 topic），题内按 `answer_type` 轮转。
  - 结果：Place 9 / Date 6 / Number 5 / Person 5 / Other 5。`benchmark_subtype` 记为 `topic=…|answer_type=…`。
- **难度**：官方没有难度字段，所以 `official_difficulty=null`。`multi_step` 和 `requires_reasoning` 是官方元数据，逐字放进 raw，不是难度等级。
- **prompt**：原题照用。官方 autorater 设定就是直接发送题目。
- **局限**：题目都是前沿模型也常答错的长尾事实题，不能据此推断“简单问答”的表现。

### 2.2 writing_language — WritingBench

- **来源**：GitHub `X-PLUG/WritingBench` 的 `benchmark_query/benchmark_all.jsonl`，共 1000 行，字段 `index, domain1, domain2, lang, query, checklist`。
- **使用的子域**：只用 v1 审计认定的 32 个纯写作子域（`jev_common.WB_CLEAN`）：
  - 文案类：Slogans、Promotional Copy、Product Description、Brand Story、Social Media Content、Promotional Voiceover、Sales Letter、Personal Blog、Multimedia Script
  - 创作类：Poetry、Prose、Lyric Writing、Fan Fiction、Novel Manuscript、Screenplay、Video/Podcast Script、Greeting Message、Host Script
  - 学术章节写作：Abstract、Introduction、Conclusion、Acknowledgements、Contributions、Limitations
  - 公文和专业写作：Government Speech、Official Document、Legal Awareness Campaign、Party Membership Application、Business Correspondence
  - 纪要类：Meeting Minutes、Meeting Summary
- **排除的子域**：
  - 研究、财务、市场、数据分析类：Investment Analysis、Market Analysis/Research、Financial Reports、Sales Report、User Research、Risk Management、Regulatory Analysis、Literature Review、Test/Engineering Report 等
  - 规划和设计类：Event/Strategic Planning、Product Proposal、Curriculum Design、Lesson Plan、Game Design 等
- **额外排除**：
  - 启发式标记的 242 条“分析候选”
  - 长度超过 5K 字符、且首尾 600 字符含 analyze/evaluate/分析/评估 的 query
- **抽样**：过滤后样本池 250 条，按 domain2 轮转抽 30 条，恰好是 30 个不同子域。语言 zh 18 / en 12；5 条超过 5K 字符。
- **缺口**：WritingBench 没有翻译或改写（rewriting/translation）子域。Derivative Work 子域经抽查是混合型，其中 1 条（idx 799）其实是改编建议或规划，所以没有纳入。**翻译和改写在本集中没有覆盖。**
- **难度**：无。WritingBench 的 requirement 子集（style/format/length）是约束维度，不是难度。

### 2.3 math — MATH-500 + LiveBench math

- **MATH-500**（HF `HuggingFaceH4/MATH-500`，`test.jsonl`，500 行）：
  - 每个 `level` 1–5 抽 4 题（共 20 题），组内按 `subject` 轮转。
  - `official_difficulty=level_N`，raw 为 `{"level": N}`。
  - `task_id` 取 `unique_id`。
- **LiveBench math**（HF `livebench/math`，368 行）：
  - AMPS_Hard 4 / math_comp 3 / olympiad 3，组内按 `subtask` 轮转。
  - 原生字段 `category='math'`，所以 label_source=benchmark_native。
  - 3 条 olympiad 带 `hardness`，值分别为 0.5 / 1.0 / 0.1，保留在 raw，不做归一化（原因见 §2.8）。
  - 抽中的 math_comp 是 aime_i_2024、amc_12b_2023、updated_amc_12a_2023，没有“原题 + updated 孪生题”同时入选的情况。
- **两个源的选择理由**：任务要求优先使用带难度元数据的源，所以 MATH-500 占 2/3。LiveBench 用来补充较新、污染较少的题。

### 2.4 reasoning_planning — LiveBench reasoning（reasoning）+ PlanningBench（planning）

subtype 信息保留在 `benchmark_subtype` 字段：LiveBench 行为 `reasoning`，PlanningBench 行为 `planning`。LiveBench 的题族写在 notes 里（`task family = …`）。

- **LiveBench reasoning**（HF `livebench/reasoning`，200 行）：
  - HF 公开数据只有 3 个题族：zebra_puzzle、web_of_lies_v2、spatial。每族抽 5 题，组内按 `livebench_release_date` 轮转。
  - 3 条 zebra 带 `level`（17/16/13），保留在 raw。
  - changelog 里后来新增的 theory_of_mind、web_of_lies_v3、Logic with Navigation 等题族不在 HF 公开数据里。
- **PlanningBench**（HF `tencent/PlanningBench`，`data/PlanningBench-eval.jsonl`，467 行，全部中文）：
  - 用种子 `sample(15)` 抽出 idx 34、75、121、148、187、195、223、237、246、259、265、307、340、376、418。
  - 内容都是运营型规划：亲子出游路线、校招面试重排、仓储储位、复习排布、通勤、灌装线排产、机房联调、项目排期、校准排程、调课、上线窗口、排课、课表、维保派工、地震疏散。
  - 发布版本没有类别和难度字段。
- **合并后的边界**：v1 中 “reasoning vs planning_design” 这条边界在 6 类体系下已经不存在。设计类任务（系统或产品设计）依然没有公开 benchmark 覆盖，这点在新体系里同样是缺口，只是不再单列成一类。

### 2.5 coding — LiveCodeBench

- **数据**：
  - `raw/livecodebench/metadata_no_tests.jsonl` 已经有全部 1055 题的元数据（按版本文件：test 400、test2 111、test3 101、test4 101、test5 167、test6 175）。
  - 取最新的 release 文件 **`test6.jsonl`**，即 release_v6 的增量。每行的 notes 都记了版本文件名。
- **抽样**：
  - `difficulty` × `platform` 共 6 格，每格 5 题，组内按比赛月份轮转。
  - test6 只有 leetcode 和 atcoder，所以结果是 leetcode 15 / atcoder 15。
  - 抽中题目的比赛日期在 2025-01-04 至 2025-04-06 之间。
- **prompt**：按 lcb_runner 的 OpenAIChat 模板重建，即 `SYSTEM_MESSAGE_GENERIC` 加 `get_generic_question_template_answer`。模板取自 GitHub main，没有钉到具体 commit。
- **局限**：只覆盖算法竞赛题，没有 direct 模式的软件工程题。

### 2.6 research_analysis — LongBench v2 过滤池（逐条复核）

**第 1 步：复核规则**
- 候选子域为 Multi-Document QA 下的 Academic、Financial、Governmental、Multi-news，加上 Long Structured Data Understanding 下的 Table QA，共 129 题。
- 以下子域不纳入：
  - Legal：经审计是混合型，一部分是法律知识应用题。
  - Knowledge graph reasoning：属于 Wikidata 三元组检索。
  - Single-Doc QA、代码仓库、ICL、对话历史等其他域。

**第 2 步：复核 v1 的 26 条排除前缀**
- 逐条确认：每个前缀恰好匹配 1 道题，而且都落在候选子域内。`validate_stage1.py` 也会检查这一点。
- 这 26 条是单文档查找、单事实、抽取或计数、纯算术、表格查找等类型，理由逐条写在 `jev_common.LB_EXCLUDE_PREFIX`。

**第 3 步：Stage 1 新增排除**
- 读了每一道被抽中题的题干和选项，发现 4 条属于查找、抽取或简单计算，追加排除（写在 `build_stage1.LB_STAGE1_EXTRA_EXCLUDE`）：
  - `66f41108`（Financial）：两份报告之间单个百分点的差，属于简单算术查找。
  - `6701cda0`（Multi-news）：从新闻里抽取两条已经写明的原因，属于简单抽取。
  - `66f7f382`（Table QA）：在价格序列里找 1 分钟内最大波动，属于简单计算或查找。
  - `66fc0152`（Multi-news）：数清单中有几种药用于神经疾病，属于抽取和计数。
- 每追加一条排除，都会重抽并复核新入选的题。最终池子 99 题（Academic 44、Governmental 20、Multi-news 15、Financial 11、Table QA 9）。

**第 4 步：抽样与结果**
- 每个 sub_domain 抽 6 题，组内按 `difficulty`×`length` 轮转。
- 结果：easy 13 / hard 17；short 8 / medium 14 / long 8。
- 30 条都是跨文档比较、综合、证据整合，或多条件的表格分析。例如：
  - ICE 与 CME 规则手册的对比
  - Apple 与 Samsung 两年的收入依赖度对比
  - 新加坡与马来西亚海关法处罚的差异
  - AUSTRAC 两份年报的对比
  - 多篇新闻综合判断“最可靠的结论”
  - 按艺人分组求最低评分
  - 计算资产负债比后取最大值

**待复核的边界题**
- `66f8c6b4`：多篇新闻中三个时段的日均伤亡计算，含算术。
- `66f3ac0b`：按比率取最大值。
- `66ed2c87`：解读单张表格的趋势。

这三条保留下来，但如果人工抽查，建议从它们开始。

**prompt 构造**
- 使用官方 `prompts/0shot.txt`，填入**完整上下文，不截断**。
- 官方 `pred.py` 会按模型 tokenizer 做首尾截断到 `max_len`（`config/model2maxlen.json`：gpt-4o 等为 120000 token，claude-3.5-sonnet 为 200000）。这个截断依赖具体模型，所以不在数据里预先做。
- 本机没有 tiktoken，所以没有生成“按 gpt-4o 截断”的版本。
- 最长的一条（`66ec17e4`）约 7.2M 字符。
- 线上 `autoroute.build_state` 只取消息开头的 1500 或 4000 字符，所以线上 Jev 实际上看不到题干（v1 已记录）。

### 2.7 各 benchmark 使用或排除的子集汇总

| Benchmark | 使用 | 排除及原因 |
|---|---|---|
| SimpleQA Verified | `requires_reasoning=False` | 37 条 requires_reasoning（偏 reasoning） |
| WritingBench | 32 个纯写作子域 | 分析、报告、规划、设计类子域；启发式分析候选；超过 5K 字符的分析类 query |
| MATH-500 | 全部 5 个 level | — |
| LiveBench math | 3 个 task | —（没有同时抽到孪生题） |
| LiveBench reasoning | 3 个题族（HF 仅有这 3 个） | changelog 中较新的题族不在 HF 上 |
| PlanningBench | 全部 467 题作为样本池 | — |
| LiveCodeBench | test6（v6 增量） | test–test5：选最新版本以降低污染 |
| LongBench v2 | 4 个 MDQA 子域 + Table QA，去掉 30 条 | Legal、KG reasoning、其他域；26 + 4 条查找、抽取、算术题 |
| DeepSWE | 113 个任务按语言轮转 | — |
| AutomationBench | 6 个公开域各 4 题 + simple 6 题 | — |

### 2.8 难度字段核实（2026-09-30 复查）

| Benchmark | 字段 | 取值 | 核实依据 | 本集处理 |
|---|---|---|---|---|
| LiveCodeBench | `difficulty` | easy/medium/hard | ① 官方 HF loading script `code_generation_lite.py` 的 features 定义了 `"difficulty": datasets.Value("string")`；② HF README 写明 “every problem is tagged with its difficulty level”；③ GitHub `lcb_runner/evaluation/compute_scores.py` 按 easy/medium/hard 分组统计（2026-09-30 clone 的 main） | 归一化为原值 |
| MATH-500 | `level` | 整数 1–5 | 字段在 HF `test.jsonl` 中存在，数据核实过（L1 43 / L2 90 / L3 105 / L4 128 / L5 134）。“1–5 是难度等级”的定义出自 MATH 论文（arXiv 2103.03874）。HF 卡片、prm800k README、hendrycks/math README 都没有写这个定义；论文 PDF 在本机无法解析文本 → **定义为 UNVERIFIED（本机）** | `level_N` |
| LongBench v2 | `difficulty`、`length` | easy/hard；short/medium/long | HF 卡片 README 的字段说明：`"difficulty": "The difficulty level of the task, either 'easy' or 'hard'"`、`"length": "…'short', 'medium', or 'long'"`（已核实）。hard 的定义出自论文，沿用 v1 笔记 | `difficulty` 归一化；`length` 放 raw |
| LiveBench math | `hardness` | float，只在 olympiad 行有值 | 只出现在 HF 卡片的 `dataset_info.features` 里。LiveBench GitHub 代码（main）完全没有引用 `hardness`，scorer 不用它，也没有文档说明刻度 | 只放 raw，不归一化 |
| LiveBench reasoning | `level` | int，只在 zebra 行有值 | 同上：只在 HF schema 中出现，官方代码不引用，含义未公开（推测是谜题规模，但**未核实**） | 只放 raw |
| SimpleQA Verified | `multi_step`、`requires_reasoning` | bool | HF csv 字段 | 放 raw；不是难度 |
| WritingBench / PlanningBench / DeepSWE | — | — | 发布数据里没有难度字段 | null |
| AutomationBench | —（`simple` 是 domain） | — | README：simple = “foundational single- and two-step tasks”，不计入官方分数 | simple 行的 raw 为 `{"domain":"simple"}`，其余为 null |

## 3. Mode 集（agentic）

### 3.1 DeepSWE（20 条）

- **来源**：本机 `/root/bench/deep-swe/tasks`（datacurve/deep-swe-1-1，共 113 个任务）。只用了 `instruction.md` 和 `task.toml` 的元数据。
- **抽样**：按 `language` 轮转。结果 js 4 / py 4 / ts 4 / rust 4 / go 4；类别为 feature_request 18、enhancement 1、bugfix 1。
- **标签**：coding + agentic，rule_mapping，clean。
- **首请求重建**：用的是 mini-swe-agent 的 `mini.yaml`，Pier 也是这样调用：
  - system：“You are a helpful assistant that can interact with a computer.”
  - user：instance_template 包裹 instruction。
  - tools：只有一个 `bash`。
- **重建的局限**：
  - `<system_information>` 里的 uname 字段是占位符。
  - DeepSWE 排行榜实际用的 mini-swe-agent 版本、step 和 cost 限制都没有公开，**UNVERIFIED**。

### 3.2 AutomationBench（30 条）

- **来源**：本机 AutomationBench v1.0.6。
- **抽样**：sales、marketing、operations、support、finance、hr 每个域 4 题，外加 simple 6 题。
- **首请求**：
  - 用 CLI 默认的 toolset `api`，工具为 `api_search`、`api_fetch`、`base64_encode`。
  - system 是 runner 统一的 `SYSTEM_PROMPT`。
- **重建的局限**：
  - 初始世界状态不在 prompt 里，agent 要自己用工具去发现。
  - `api` 工具集不透露任务领域；换成 `limited_zapier` 时，工具名会直接暴露领域，例如 `salesforce_*`。
  - 官方排行榜用的是私有集，而且“有意更难”。
- **标签**：每题都读过 prompt、task_name 和终态断言类型后逐题判断，label_source=item_judgement。

## 4. AutomationBench 覆盖分析

### 4.1 判定规则

判定规则也写在 `scripts/stage1_ab_judgements.py` 文件头：
- **clean**：6 类中有一类能说清这个任务是什么，工具只用来取输入或交付结果。此时 gap=false。
- **ambiguous**：6 类中有一类能覆盖任务的认知核心（例如计算加报告，或一段写作），但判分还取决于业务流程执行（改记录、按规则路由、政策陷阱）。此时 task_type 取最接近的一类，gap=true。
- **uncovered**：任务本质是“执行业务流程 / 改变外部系统状态”（同步、报名、排期、更新记录、按流程通知）。此时 task_type=null，gap=true。

### 4.2 结果（30 条）

| 域 | clean | ambiguous | uncovered |
|---|---|---|---|
| sales | 0 | 0 | 4 |
| marketing | 1 | 0 | 3 |
| operations | 0 | 1 | 3 |
| support | 0 | 0 | 4 |
| finance | 0 | 2 | 2 |
| hr | 0 | 1 | 3 |
| simple | 0 | 0 | 6 |
| **合计** | **1** | **4** | **25** |

逐题结果：

| task_id | task_name | fit | task_type |
|---|---|---|---|
| finance:4038 | finance.wave_product_catalog | uncovered | null |
| finance:4049 | finance.monday_project_billing | ambiguous | research_analysis |
| finance:4067 | finance.profit_margin_analysis | ambiguous | research_analysis |
| finance:4095 | finance.xero_expense_claim_review | uncovered | null |
| hr:5028 | hr.offer_letter_generation | ambiguous | writing_language |
| hr:5088 | hr.compliance_training_enrollment | uncovered | null |
| hr:5108 | hr.exit_interview_scheduling | uncovered | null |
| hr:5124 | hr.mandatory_meeting_scheduling | uncovered | null |
| marketing:1033 | marketing.event_registration_sync | uncovered | null |
| marketing:1045 | marketing.content_gap_analysis | clean | research_analysis |
| marketing:1128 | marketing.guest_post_outreach | uncovered | null |
| marketing:1167 | marketing.event_sponsorship_screen | uncovered | null |
| operations:1202 | operations.trello_basecamp_compliance | uncovered | null |
| operations:1219 | operations.monday_calendar_emergency_drill | uncovered | null |
| operations:1322 | operations.sensor_monitoring_alert | uncovered | null |
| operations:1354 | operations.utility_cost_allocation | ambiguous | research_analysis |
| sales:1112 | sales.event_followup_outreach | uncovered | null |
| sales:3 | sales.create_contact_for_account | uncovered | null |
| sales:528 | sales.five_level_conditional | uncovered | null |
| sales:838 | sales.zoom_customer_health | uncovered | null |
| simple:3051 | simple.buffer_twitter_product_launch | uncovered | null |
| simple:3093 | simple.sheets_budget_expense | uncovered | null |
| simple:3166 | simple.close_deal_sf_slack | uncovered | null |
| simple:3169 | simple.feature_launch_slack | uncovered | null |
| simple:3188 | simple.subscriber_welcome_email | uncovered | null |
| simple:3200 | simple.partnership_hubspot_zoom | uncovered | null |
| support:1426 | support.zoho_calendar_callbacks | uncovered | null |
| support:1447 | support.zoho_desk_ticket_categorization | uncovered | null |
| support:1472 | support.hiver_slack_digest | uncovered | null |
| support:1479 | support.helpcrunch_engagement_scoring | uncovered | null |

### 4.3 例子

- **clean**：`marketing.content_gap_analysis` 的任务是“Analyze our content inventory and recommend priorities…”。工具只用来读表格、Slack 和收件箱里的指引，结论通过邮件交付。它就是 agentic 的 research_analysis。
- **ambiguous**：
  - `finance.monday_project_billing`（对账）和 `finance.profit_margin_analysis`（毛利计算）：核心是“按给定公式计算，然后用邮件报告”。research_analysis 只能说清一部分，本质是固定的财务例行流程。
  - `operations.utility_cost_allocation`：按比例分摊成本（可看作 research_analysis 或 math），同时要写表格、发邮件、发 Slack。
  - `hr.offer_letter_generation`：写 offer 草稿（writing_language），但判分主要看给谁起草、是否查了薪资带和例外审批。
- **uncovered**：
  - 同步报名到 CRM 和邮件列表（`marketing.event_registration_sync`）
  - 员工培训报名并更新台账（`hr.compliance_training_enrollment`）
  - 预约回访并更新工单（`support.zoho_calendar_callbacks`）
  - 线索按五级决策表处理后建任务（`sales.five_level_conditional`）：条件链有推理的味道，但本质是照流程写 CRM
  - simple 全部 6 条：一两步的 CRUD 或通知

## 5. 关于是否恢复 workflow_operation 的证据（只列证据，不做决定）

**支持“6 类不够”的证据**
- 在逐题判断的 30 条 AB 任务中，25 条（83%）在 6 类里找不到合适归属，其中 6 个公开域占 19/24，simple 占 6/6。只有 1 条是 clean。
- 对 AB 全部 800 题的终态断言类型做了粗略统计，脚本是一次性分析，不入库。口径：看“正向”断言，即排除 `_not_`、`not_exists`、`not_changed` 这类；只要有一条不是 gmail/slack 的，就算“写外部记录”。
  - 611 题要求写 CRM、表格、日历、工单等外部记录：sales 88、marketing 51、operations 91、support 99、finance 46、hr 60、simple 176。
  - 其余 189 题的正向断言只有发邮件或发 Slack 消息，但这仍然是外部动作。
  - 也就是说，所有题的判分都基于外部状态，而不是回答文本。
- 在 ambiguous 的 4 条里，6 类只能覆盖认知核心（计算报告、写作），覆盖不了“按业务规则执行、避开政策陷阱”这部分。判分断言里大量出现 `*_not_sent_to`、`*_not_exists`、`*_not_changed` 这类“不该做”的检查。
- task_name 里带 analysis、report、recap、digest、review、audit、reconcil 等字样的题（全集 91/800），是最可能落进 research_analysis 的一批，但它们的交付仍然是写外部系统或发送消息。

**支持“不需要恢复”的证据，以及需要注意的地方**
- execution_mode=agentic 已经能把这些任务和 direct 任务区分开。如果路由只需要知道“要不要选工具能力强的模型”，uncovered 这一类在 execution_mode 维度上是能识别的，只是 task_type 为 null。
- 部分 AB 任务（1 clean + 4 ambiguous = 5/30）可以用“agentic + research_analysis/writing_language”来表达。
- 样本只有 30 条，而且都来自 AutomationBench 这一个 benchmark，全部是 Zapier 风格的 SaaS 业务流程。其他 agentic 来源里有没有同类任务（例如 Terminal-Bench 4.0 的 Operations/Claims/Logistics），本次没有覆盖。
- 逐题判断由一人完成，没有做第二人复核。

## 6. 未核实项（UNVERIFIED）与已知局限

- MATH `level` 的“1–5 难度”定义出自论文，本机无法解析 PDF 文本来核对。字段本身在数据中已核实。
- LiveBench `hardness` 和 `level` 的语义官方没有文档，所以只放 raw。
- LiveCodeBench prompt 模板取自 GitHub main，没有钉到 commit。test6 本地元数据行数（175）与官方 v6 增量（1055−880）一致，但没有和 HF 后续 revision 做内容哈希比对。
- DeepSWE 排行榜的 mini-swe-agent 配置没有公开。AB 首请求用 CLI 默认的 `api` 工具集，实际生产流量的工具集可能不同。
- LongBench prompt 未截断；按模型截断的版本需要对应 tokenizer，本机没有 tiktoken。
- AutomationBench 的逐题判断没有做人工复核。LongBench 的纯度过滤也是我个人的判断，建议抽查 §2.6 列出的 3 条边界题。
- 没有覆盖的能力：翻译和改写、系统或产品设计、direct 模式的软件工程、英文 planning。
