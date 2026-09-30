# 现有模型结果清单（Existing Results Inventory）

## 0. 说明

| 项 | 内容 |
|---|---|
| 编写日期 | 2026-09-30 |
| 范围 | 只盘点本机（东京机）上已有的模型运行结果：它们是什么、覆盖哪些题、用什么参数跑的、记录了哪些字段、现在还能拿来做什么。**不比较模型优劣，不提路由策略建议。** |
| 检查过的来源 | `/root/bench/proxy/log/*.jsonl`；`/root/bench/report/`（`hle/`、`ab/`、`*.json`、`*.log`、SMOKE/STATUS/WORK_SUMMARY 等文档）；`/root/bench/jobs/`、`/root/bench/server_jobs/`；`/root/h3_work/auto/`（9/23 路由实验）；`/root/FUSION_METHODS_AND_DATA.md`（与 `/root/bench/report/FUSION_METHODS_AND_DATA.md` 逐字节相同）；记忆文件 `jev-benchmark-smoke.md`、`auto-model-routing.md`、`benchmark-rigor-rule.md` |
| 核实方式 | 行数、题数、字段、模型、参数都用 `/root/bench/hle-venv/bin/python` 实际读文件统计。没能在本机核实的内容标 **UNVERIFIED**。编写过程中没有调用任何模型 API、Jev API，也没有登录服务器 |
| 时间口径 | 代理日志 `ts` 按本机时区（CST）换算；Pier `result.json` 里的时间是 UTC；文件时间取 mtime |
| 密钥 | 文件里的 API key、token 一律没有抄进本文 |

### 0.1 作废规则

> **2026-09-29 之前产生的 benchmark 结果，全部不能作为成绩使用。**（用户 9/29 的决定，见 `WORK_SUMMARY_2026-09-29.md` §0 和记忆 `benchmark-rigor-rule.md`：含 DeepSWE b0v4 中原先认为有效的 4 题、HLE、AB 样本；以后拿不准是否干净的结果一律作废重跑，不做“影响不大”的判断。）

下面列出的每一个结果集都早于 2026-09-29，所以**全部作废**。各节会写明已知的具体原因。能继续用的只有非成绩部分：题目 ID 列表、harness 配置、成本和时延的粗略参考、Jev 分类记录（可作为分类器评测的数据点）。

### 0.2 结果集总表

本机共盘点 **17 个结果集**（R01–R17）。另有 4 类不算结果集的材料（第 8 节），以及只保存在服务器上的结果（第 5 节，本机没有，只列路径）。

| ID | 结果集 | Benchmark | 模型 | 题数（实数） | 日期 | Jev 分类 | 状态 |
|---|---|---|---|---|---|---|---|
| R01 | AB smoke（单题 + 3 题） | AutomationBench 公开集 | kimi-k3 | 1 + 3 次运行，3 道不同题 | 09-27 | 无 | 作废 |
| R02 | DeepSWE smoke（东京） | DeepSWE v1.1 | kimi-k3 | 2 | 09-27 | 无 | 作废 |
| R03 | HLE sample-ds | HLE text-only | deepseek-v4.1-flash | 请求 20，存下预测 15，判卷 14 | 09-28 | 无 | 作废 |
| R04 | HLE sample-k3 | HLE text-only | kimi-k3 | 请求 100，存下预测 88，判卷 88 | 09-28 | 无 | 作废 |
| R05 | HLE judge 选型测试（ds / k3） | HLE（判卷环节） | 判卷：deepseek-v4.1-flash / kimi-k3（关思考） | 各 15 | 09-28 | 无 | 作废 |
| R06 | HLE pinned-k3（全量，中断） | HLE text-only | kimi-k3 | 预测 154，判卷 0 | 09-28 | 无 | 作废 |
| R07 | HLE pinned-ds（全量，中断） | HLE text-only | deepseek-v4.1-flash | 本机无预测文件，只有代理日志 48 + 2 行 | 09-28 | 无 | 作废 |
| R08 | AB sample-ds | AutomationBench 公开集 | deepseek-v4.1-flash | 30 | 09-28 | 无 | 作废 |
| R09 | AB pinned-k3（全量，中断） | AutomationBench 公开集 | kimi-k3 | 进度 101/570 组，**没有逐题结果文件** | 09-28 | 无 | 作废 |
| R10 | AB pinned-ds（全量，两次中止） | AutomationBench 公开集 | deepseek-v4.1-flash | 进度 2/570 组，没有结果文件 | 09-28 | 无 | 作废 |
| R11 | DeepSWE test-ds（服务器结果的本机副本） | DeepSWE v1.1 | deepseek-v4.1-flash | 1 | 09-28 | 无 | 作废 |
| R12 | 9/23 代码，二档 auto vs kimi（`final/`） | HumanEval+ / MBPP+ | kimi-k3；auto→ds/kimi | 542 × 2 组 | 09-23 | 旧版档位分类 | 作废 |
| R13 | 9/23 代码，三档 auto + kimi + ds（`code_all/`） | HumanEval+ / MBPP+ | kimi-k3、deepseek-v4.1-flash；auto→ds/glm-5.3-flash/kimi | 542 × 3 组 | 09-23 | 旧版档位分类 | 作废 |
| R14 | 9/23 数学，二档（`math1/`） | GSM8K + MATH-500 | kimi-k3；auto→ds/kimi | 300 × 2 组 | 09-23 | 旧版档位分类 | 作废 |
| R15 | 9/23 数学，三档 + ds（`math_all/`） | GSM8K + MATH-500 | kimi-k3、deepseek-v4.1-flash；auto→ds/glm-5.3-flash/kimi | 300 × 3 组 | 09-23 | 旧版档位分类 | 作废 |
| R16 | 9/23 中间轮次与已被取代的轮次 | 同上 | 同上 | 见 §6.3 | 09-23 | 部分有 | 作废 |
| R17 | TrajectoryRL 组合实验文档 | HumanEval+/MBPP+、Agentic-14/26/35 | 多模型 | 仅文档，本机无原始数据 | 09-13 至 09-18（文档所述） | 无 | 外部文档，按规则同样不能当成绩 |

东京代理日志合计扣费 **$66.92**（14 个 jsonl 的 `charged_micro` 求和，与 WORK_SUMMARY §6 一致）。

---

## 1. 通用字段说明

### 1.1 东京代理日志 `/root/bench/proxy/log/*.jsonl`

所有文件都由 `engy_proxy.py` 写出，每行一个请求，字段一致：

- 标识：`ts`、`run`、`req_id`、`conversation_key`、`engy_request_id`、`miner`
- 模型：`requested_model`、`selected_model`、`upstream_model`
- 参数：`reasoning_effort`、`max_tokens`、`injected`（代理注入的默认参数）、`stream`、`tools`、`n_messages`
- 结果：`status`、`finish_reason`、`attempts`、`error_body`（部分文件有）
- token：`prompt_tokens`、`completion_tokens`、`cached_tokens`、`reasoning_tokens`
- 成本：`charged_micro`（Engy 实际扣费，单位百万分之一美元；只有 200 的请求有值）
- 时延：`t_upstream_ms`（每行都有）
- 路由：`decision`（auto 时有 task_type / execution_mode / capability_need / 置信度 / rule / source）；`selftest.jsonl` 另有 `jev_usage`

| 文件 | 行数 | 会话数 | 时间（CST） | 模型 | effort | max_tokens | status 分布 | finish=length | 扣费 | decision 非空 |
|---|---:|---:|---|---|---|---|---|---:|---:|---:|
| ab-pinned-ds.aborted-conc30.jsonl | 362 | 30 | 09-28 14:43–14:50 | deepseek-v4.1-flash | max | 不传 | 200×327，429×35 | 0 | $0.102 | 0 |
| ab-pinned-ds.jsonl | 154 | 19 | 09-28 14:46–15:06 | deepseek-v4.1-flash | max | 不传 | 200×146，429×7，400×1 | 1 | $0.069 | 0 |
| ab-pinned-k3.jsonl | 3,062 | 136 | 09-28 14:43–15:06 | kimi-k3 | max | 不传 | 200×3062 | 0 | $31.858 | 0 |
| ab-sample-ds.jsonl | 765 | 30 | 09-28 12:24–15:05 | deepseek-v4.1-flash | max | 不传 | 200×761，400×3，429×1 | 0 | $0.834 | 0 |
| hle-pinned-ds.aborted-w20.jsonl | 2 | 2 | 09-28 14:43 | deepseek-v4.1-flash | max（注入） | 32768 | 200×2 | 0 | $0.000 | 0 |
| hle-pinned-ds.jsonl | 48 | 36 | 09-28 14:43–15:04 | deepseek-v4.1-flash | max（注入） | 32768 | 200×43，429×5 | 18 | $0.083 | 0 |
| hle-pinned-k3.jsonl | 172 | 172 | 09-28 14:43–14:52 | kimi-k3 | max（注入） | 32768 | 200×172 | 34 | $24.719 | 0 |
| hle-sample-ds.jsonl | 48 | 20 | 09-28 13:27–13:58 | deepseek-v4.1-flash | 前 20 行无 effort，后 28 行 max | 16384 | 200×48 | 19 | $0.033 | 0 |
| hle-sample-ds-judge.jsonl | 35 | 35 | 09-28 13:32–14:07 | glm-5.3（判卷） | 20 行无，15 行 low | 4096 | 200×35 | 12 | $0.220 | 0 |
| hle-sample-k3.jsonl | 100 | 100 | 09-28 14:10–14:18 | kimi-k3 | max（注入） | 16384 | 200×100 | 29 | $8.761 | 0 |
| hle-sample-k3-judge.jsonl | 88 | 88 | 09-28 14:21 | kimi-k3（判卷，`thinking=false`） | 不传 | 4096 | 200×88 | 0 | $0.205 | 0 |
| judge-ds.jsonl | 15 | 15 | 09-28 14:09 | deepseek-v4.1-flash（判卷） | 不传 | 4096 | 200×15 | 0 | $0.000（<$0.001） | 0 |
| judge-k3.jsonl | 15 | 15 | 09-28 14:09 | kimi-k3（判卷，`thinking=false`） | 不传 | 4096 | 200×15 | 0 | $0.030 | 0 |
| selftest.jsonl | 5 | 4 | 09-28 12:21 | 请求 auto×3、deepseek×2，实际全走 deepseek-v4.1-flash | 1 行 max | 32 / 40 | 200×5 | 1 | ≈$0 | **3** |

- 所有 pinned 和 sample 运行的 `decision` 都是空的：**东京日志里没有 Jev 三维分类**，只有 `selftest.jsonl` 的 3 行（代理自测，不是 benchmark）。
- `*.proxy.out` 只有启动行和 FastAPI 的弃用警告；启动行记录了 run 名、`policy=bench-v0`、`jev=on`、候选模型列表。

### 1.2 其他 harness 的字段

| Harness | 成本字段 | 时延字段 | 备注 |
|---|---|---|---|
| HLE 官方脚本（`hle_<model>.json`） | 无成本；`usage.{prompt,completion,total}_tokens`、`completion_tokens_details.reasoning_tokens`、`prompt_tokens_details.cached_tokens` | 无 | 判卷后的文件多一个 `judge_response`（含 `correct`） |
| AutomationBench runner（`--export-json`） | `summary.total_cost`、逐题 `cost`（按 `--input-cost/--output-cost` 全价计算，**不打缓存折扣**）；逐题 input/output/cached/uncached/reasoning token | `meta.duration_seconds`、逐题 `model_time_s`、`tool_time_s` | runner 的 `reasoning_tokens` 恒为 0（SMOKE 报告 §3 已说明） |
| Pier / mini-swe-agent（`result.json`） | `agent_result.cost_usd` **为 null**；`n_input_tokens`、`n_cache_tokens`、`n_output_tokens`、`peak_context_tokens` 有值 | `started_at` / `finished_at`，以及各阶段时间戳 | Pier 固定 `MSWEA_COST_TRACKING=ignore_errors` |
| 9/23 实验脚本（`log.jsonl`） | `charged_micro`（网关账单字段）；数学另有 `cost_usd`；auto 行 `route.jev_cost_usd`，代码实验另有 `route.jev_input_tokens` | `latency_s`，数学另有 `total_latency_s`；auto 行 `route.latency_ms`、`route_latency_s` | 每行都有 `usage` |

---

## 2. HLE（`/root/bench/report/hle/`、`hle_*.log`、代理日志 `hle-*`）

共同条件：数据集是 `/root/bench/hle/data/test-00000-of-00001.parquet`，2,158 题 text-only（已核对行数）；harness 是 CAIS 官方 `hle-repo/hle_eval/run_model_predictions.py` 和 `run_judge_results.py`，通过 `run_hle.sh` 经代理调用；reasoning_effort 由代理注入（官方脚本本身不发）。官方脚本里 temperature 一行被注释掉了，`--temperature 0` 实际不会发出（已读代码第 36 行确认）。代理日志不记 temperature。

| 项 | R03 sample-ds | R04 sample-k3 | R05 judge 选型测试 | R06 pinned-k3 | R07 pinned-ds |
|---|---|---|---|---|---|
| 目录 | `hle/sample-ds/` | `hle/sample-k3/` | `hle/judge-test-ds/`、`hle/judge-test-k3/` | `hle/pinned-k3/` | `hle/pinned-ds/`（空目录） |
| 题目覆盖 | 数据集前 20 题；存下预测 15 个（已核对均属前 20），判卷 14 个 | 数据集前 100 题；存下预测 88 个（均属前 100），判卷 88 个 | R03 的 15 个预测，由两个判卷模型各判一遍（`verdicts.json` 各 15 条） | 预测 154 个（均在 2,158 题内，不是按前 N 顺序）；`judged_*.json` 为空 `{}` | 本机没有预测文件；代理日志 48 行（36 个会话）+ 中止文件 2 行 |
| 被测模型 | deepseek-v4.1-flash | kimi-k3 | 被判的是 deepseek-v4.1-flash 的回答 | kimi-k3 | deepseek-v4.1-flash |
| 模型版本 | UNVERIFIED（Engy 未公布量化/版本；日志只有 `miner` ID） | 同左 | 同左 | 同左 | 同左 |
| reasoning effort | 前 20 次请求（13:27–13:28）**没有 effort**，13:35 起 28 次为 max | max | 判卷：ds 不传；k3 注入 `thinking=false` | max | max |
| 输出上限 | 16,384（自设） | 16,384（自设） | 判卷 4,096（官方判卷脚本写死） | 32,768（自设） | 32,768（自设） |
| 截断（finish=length） | 19/48 次 | 29/100 次 | 0 | 34/172 次 | 18/43 次（200 响应） |
| 判卷 | glm-5.3（20 次不带 effort，其中 11 次撞 4096 上限；再 15 次 low） | kimi-k3 关思考 | ds / k3 关思考 | 未判卷 | 未判卷 |
| 判卷结果（文件实数） | correct yes 2 / no 12 | yes 43 / no 45 | 两个判卷模型都是 yes 2 / no 13 | — | — |
| 官方汇总脚本 | 在 `calib_err` 处 IndexError 崩溃（题数太少），日志里没有官方 accuracy 输出 | 同左崩溃 | — | 同左崩溃（0 条预测） | 日志只有进度 |
| 成本字段 | 预测文件：只有 token；代理：`charged_micro` 48/48 有值，$0.033；判卷 $0.220 | 代理 100/100，$8.761；判卷 $0.205 | 代理 $0.000 / $0.030 | 代理 172/172，$24.719 | 代理 43/48，$0.083 |
| 时延字段 | 代理 `t_upstream_ms`，中位 250.8 s | 中位 90.3 s | 中位 3.5 s / 1.2 s | 中位 123.6 s | 中位 1,063 s |
| Jev 分类 | 无 | 无 | 无 | 无 | 无 |
| 日期 | 09-28 13:27–14:08 | 09-28 14:10–14:22 | 09-28 14:09 | 09-28 14:43–14:59 | 09-28 14:43–15:39 |

**作废原因（除 9/29 规则外，已知的具体问题）**

- **自设输出上限导致截断**：官方做法是不设上限（README 建议用模型可用的最大值）。这几次运行自设了 16K 或 32K。WORK_SUMMARY §4.1 记录的截断比例：kimi-k3 约 20%，deepseek 约 42%。按文件实数：R04 29%，R06 34/172≈20%，R07 18/43≈42%，R03 19/48。`run_hle.sh` 已于 9/29 改为默认不传 `max_completion_tokens`。
- **判卷模型与官方不一致**：官方是 o3-mini-2025-01-31，这里用的是 kimi-k3 关思考或 glm-5.3（`OFFICIAL_ALIGNMENT_2026-09-29.md` §二）。
- **缺题**：R03 20 题只存下 15 个（STATUS 记为 5 题超过官方 600 s 超时）；R04 100 题只有 88 个预测，但代理 100 次请求都返回 200，缺失原因 UNVERIFIED（可能是客户端 600 s 超时）。
- R03 前 20 次请求没带 reasoning_effort，同一题集的运行里参数不一致。
- R06：代理进程被误杀，全量中断，$24.72 没有产生判卷结果（WORK_SUMMARY §4.1）。
- R07：先以 20 worker 启动后中止，再以 12 worker 重启，有 5 次 429；每题要几分钟，只跑了极少数题（WORK_SUMMARY：6/2158）。
- HLE 只有 text-only 2,158 题，不是官方的 2,500 题全集（OFFICIAL_ALIGNMENT §二）。

**还能用什么**

- 题目 ID：R04 的 88 个、R06 的 154 个 HLE ID，可以用作抽样核对（注意 R06 不是按顺序抽的）。
- 粗略参考：每题 token 数、时延、截断率，可说明“16K/32K 上限不够”以及 DS 在 max 档很慢。
- 判卷选型的观察（R05：ds 和 k3 关思考在 15 题上判定一致；glm-5.3 在 4096 上限下会截断），只能作参考，因为正式口径应该换成 o3-mini。
- 不能用：任何正确率数字。

---

## 3. AutomationBench（`/root/bench/report/ab*`、代理日志 `ab-*`）

共同条件：AutomationBench 仓库 commit `4a8e106`，`benchmark_version` 1.0.6（JSON `meta` 中已核对）；官方 runner `auto-bench`；`--api chat_completions --reasoning-effort max --max-steps 50`；toolset `api`；**公开题集**（榜单用的是私有集，两者不能直接比较，见 OFFICIAL_ALIGNMENT §三）；`--num-examples N` 取数据集前 N 题；计分方式是全部断言通过才算 pass，另外报部分得分 `avg_score`。

| 项 | R01 smoke（09-27） | R08 sample-ds | R09 pinned-k3 | R10 pinned-ds |
|---|---|---|---|---|
| 文件 | `ab_single.json/.log`、`ab_smoke3.json/.log`、`ab_rows.md` | `ab/ab-sample-ds.json/.log`；代理 `ab-sample-ds.jsonl` | `ab/ab-pinned-k3.log`；代理 `ab-pinned-k3.jsonl` | `ab/ab-pinned-ds.log`；代理 `ab-pinned-ds.jsonl`、`ab-pinned-ds.aborted-conc30.jsonl` |
| 题目覆盖 | 单题 `sales.multi_hop_lookup`；3 题 `sales.multi_hop_lookup`、`negative_selection`、`recency_selection`（同一题跑了两次） | 前 30 题，全是 sales 领域（名单在 JSON `tasks[].name` 里）；`aborted_tasks` 3 个：`apply_project_label`、`slack_deal_notification`、`linkedin_connection_outreach` | 计划 600 次 rollout / 570 组；日志停在 101/570；**本机没有导出 JSON，不知道具体跑了哪些题**；代理日志有 136 个会话 | 第一次（并发 30）30 个会话后中止；第二次 2/570 组后 `RuntimeError: Event loop is closed` |
| 模型 | kimi-k3 | deepseek-v4.1-flash | kimi-k3 | deepseek-v4.1-flash |
| effort / 输出上限 | max / runner 默认 | max / 不传 | max / 不传 | max / 不传 |
| 调用路径 | **直连 Engy，不经代理** | 经代理 | 经代理，并发 10 | 经代理，并发 30 → 8 |
| 结果（文件实数） | 单题 0.667 不通过；3 题 avg 0.694，pass 1/3 | avg 0.695，pass 16/30 | 只有进度条上的累计值 reward 0.620、pass_rate 0.262 | 进度条 2 组 |
| 成本字段 | runner `cost` 有值（全价口径：$0.315；3 题 $0.769）；没有 `charged_micro` | runner `total_cost` $1.627（全价）；代理 `charged_micro` 760/765 有值，$0.834 | 代理 3062/3062 有值，$31.858；runner 没有输出 | 代理 $0.069 + $0.102 |
| 时延字段 | `duration_seconds`、`model_time_s`、`tool_time_s` | 同左（总时长 9,685 s）；代理中位 42.4 s/次 | 代理中位 3.1 s/次 | 代理中位 27.3 s / 22.3 s |
| Jev 分类 | 无 | 无 | 无 | 无 |
| 日期 | 09-27 16:57 / 17:10 | 09-28 12:24–15:06 | 09-28 14:43–15:07 | 09-28 14:43–15:36 |

**作废原因**

- 都早于 9/29。
- 公开题集和 AA 榜单的私有集不可比。
- R01：不经代理，只有 runner 的全价成本；同一题两次得分 0.67 和 0.33，单次方差大。
- R08：3 个 aborted 题仍计入汇总；代理日志有 400×3、429×1。按“任何失败整题重跑”的口径，这些题不干净。
- R09：方案改为只跑 Auto 后停掉，只完成 101 组，没有逐题结果（WORK_SUMMARY：“未完成，仅供参考”）。
- R10：第一次因并发 30 出现 35 次 429 而中止；第二次崩溃。

**还能用什么**

- R08 的 30 个题名和逐题 token、步数、时延、runner 成本，可以作为 DS 在 max 档的成本和时延粗略参考。R08 同时有 runner 成本和代理 `charged_micro`，可以用来看全价口径和实扣之间的差距。
- R09 的代理日志（3,062 次请求）可作为 kimi-k3 单次调用 token/扣费/时延分布的参考，但不能对应到具体题目（日志只有 `conversation_key` 哈希，没有题名）。
- `run_ab.sh` 的参数（单价、`--no-ensure-complete`、`--max-steps 50`）可以复用。

---

## 4. DeepSWE（本机）

| 项 | R02 东京 smoke（09-27） | R11 deepswe-test-ds（服务器结果副本） |
|---|---|---|
| 目录 | `/root/bench/jobs/single-bandit/`、`/root/bench/jobs/dataset-seed0/`；日志 `report/deepswe_single.log`、`report/deepswe_dataset.log` | `/root/bench/server_jobs/deepswe-test-ds/`、`server_jobs/deepswe-test-ds.jsonl`（服务器代理日志副本） |
| 题目 | `bandit-incremental-cache-control`、`dasel-html-document-format`（`--sample-seed 0` 抽到），各 1 个 trial | `bandit-incremental-cache-control`，1 个 trial |
| 模型 / effort | kimi-k3，`reasoning_effort=max`，**另外显式传了 `temperature=1.0`、`top_p=1.0`** | deepseek-v4.1-flash，max，不传采样参数 |
| Harness | Pier 0.3.1（harbor 0.23.0）+ mini-swe-agent 2.4.6，`model_class=litellm`；DeepSWE commit `0b9fabb`（SMOKE 报告） | 自定义 agent `engy_agents:MiniSweAgentCN`（安装层换国内镜像），经服务器代理 `/run/deepswe-test-ds` |
| 资源 | `override_memory_mb=4096`（官方 8 GB） | 未覆盖（官方规格） |
| 判分 | 官方 verifier：两题 reward 1（f2p 88/88、146/146） | reward 0（f2p 0/88，p2p 275/275）；`NonZeroAgentExitCodeError` |
| 成本字段 | `cost_usd` null；token 有值（bandit in 3,528,159 / cache 3,473,920 / out 56,250）；直连 Engy，无 `charged_micro` | `cost_usd` null；代理副本 132/142 行有 `charged_micro`，$0.206 |
| 时延字段 | `started_at/finished_at`：约 20.2 min、18.4 min | 04:49–06:39 UTC（约 1 h 49 min）；代理 `t_upstream_ms` |
| 其他 | 步数 57 / 80，峰值上下文 94,761 / 81,027 | 132 步，峰值上下文 259,009；代理 400×10（上下文超 DS 容量） |
| Jev 分类 | 无 | 无（`decision` 全空） |

**作废原因**：都早于 9/29。R02 用了 4 GB 内存，还显式传了采样参数，和方案 v3“只传 reasoning_effort”不一致；OFFICIAL_ALIGNMENT §四写明“9/27 东京 4 GB 的试跑已作废”。R11 跑在沈阳生产服务器上，安装层换了镜像，而且当时服务器出网不稳。

**还能用什么**：Pier / agent 的配置（`config.json`，引用时注意去掉 key）；每题 token 规模（350–1,900 万输入 token，98% 左右命中缓存），可作成本估算的粗略参考；DS 在 bandit 题上触发容量 400，可作为 Long-context Route 的一个真实案例。

---

## 5. 只在服务器上的结果（本机没有，未核实）

以下内容**不在本机**，本次没有登录服务器，全部 **UNVERIFIED**。信息来自 `WORK_SUMMARY_2026-09-29.md` 和 `STATUS_2026-09-28.md`：

| 结果 | WORK_SUMMARY / STATUS 的描述 | 服务器路径（原文） |
|---|---|---|
| DeepSWE Auto batch 0：b0、b0r、b0v2（两次）、b0v3、b0v4、bredo | 19 题；前 4 轮和 bredo 作废（apt/PyPI 失败、Jev 超时/fallback、Docker 地址池耗尽、连接超时、重跑继承 sticky）；b0v4 中原先认为有效的 4 题也已被 9/29 规则作废，另有 8 题作废、7 题未跑完；b0v4 的 15 个对话**有 Jev 三维分类**（全部是 coding + agentic；13 个走 ds，2 个走 glm-5.3） | job：`~/bench/jobs/`（作废目录带 `.invalid-*` 后缀）；代理日志：`~/bench/proxy/log/`；重跑清单：`~/bench/redo_tasks.txt` |
| DeepSWE GLM 全量（未授权启动） | $16.49，110 题构建失败，没有有效数据 | `~/bench/jobs/` |
| DeepSWE 服务器 bandit 复跑（09-27） | reward 1，18.8 min，104 步 | SMOKE 报告写的是 `jobs/cn-single-bandit` |
| TB2 smoke（regex-log，Terminus-2 + kimi-k3） | reward 1，$0.08 | `~/bench/tb2/`、`~/bench/tb2_jobs/`（STATUS §8） |

WORK_SUMMARY §9 的原文：“代理日志 | 东京 `/root/bench/proxy/log/`，服务器 `~/bench/proxy/log/`”；“DeepSWE job 产物 | 服务器 `~/bench/jobs/`，作废的目录名带 `.invalid-*` 后缀”。服务器代理日志合计扣费 $33.23（WORK_SUMMARY §6）。
按铁律，沈阳是生产环境；如果要取回这些日志，需要用户另行决定怎么取。

---

## 6. 9/23 路由对比实验（`/root/h3_work/auto/`）

共同条件：`exp_run.py`（代码）和 `exp_math.py`（数学）直接请求 Engy 网关，每题每组一次，`temperature 0`，同一个系统提示，**不传 reasoning_effort**（按模型默认；kimi-k3 行都有 reasoning_tokens，deepseek 行都是 0，glm-5.3-flash 部分有）。代码题 `max_tokens` 默认 2048；三档实验里 glm-5.3-flash 的输出达到 6000，说明 glm 用了更高的上限（文档说“glm 思考模式，输出上限 6000”；具体怎么设的 UNVERIFIED）。数学题 `max_tokens 6000`。代码题判分用本机 EvalPlus（plus 口径，另报 base）；数学题用 boxed 答案精确匹配。

**Jev 分类是旧版档位分类，不是现在的三维分类**：auto 行的 `route` 字段有 `tier`（simple/normal/complex）、`confidence`、`probabilities`、`source`（全部为 jev）、`latency_ms`、`jev_cost_usd`、`table`，代码实验另有 `jev_input_tokens`。没有 task_type / execution_mode。

### 6.1 主结果集

| 项 | R12 `final/`（代码二档） | R13 `code_all/`（代码三档 + ds） | R14 `math1/`（数学二档） | R15 `math_all/`（数学三档 + ds） |
|---|---|---|---|---|
| 题目 | HumanEval+ 164 + MBPP+ 378 = 542（唯一 task_id 542） | 同左 542 | GSM8K 150 + MATH-500 150 = 300 | 同左 300 |
| `log.jsonl` 行数 | 1,084（kimi 542、auto 542） | 1,626（kimi、auto、deepseek 各 542） | 600（kimi 300、auto 300）；另有 `log.before_regrade.jsonl` | 900（三组各 300） |
| auto 的实际去向 | ds 513、kimi 29 | glm-5.3-flash 409、ds 130、kimi 3 | ds 166、kimi 134 | ds 166、kimi 130、glm-5.3-flash 4 |
| 来源拼接（`cmp` 已核对） | kimi = `run1/`，auto = `run2/` | kimi = `code3/`，auto = `code4/`，ds = `code_ds/` | 单次运行 | kimi + auto = `math3/`，ds = `math_ds/`（REPORT 数值一致） |
| 截断（finish=length） | kimi 10，auto→kimi 4 | kimi 12，auto→glm 21 | UNVERIFIED（未统计） | kimi 4，auto→kimi 2，ds 2 |
| 失败请求 | 0（ok 全为 True） | 0 | 0 | 0 |
| 成本字段 | `charged_micro` 全部有值，合计 $2.389 | 全部有值，$2.412 | 全部有值，$2.695 | 全部有值，$2.587 |
| 时延字段 | `latency_s` 全部有值 | 同左 | `latency_s`、`total_latency_s` | 同左 |
| 判分文件 | `*_eval_results.json`（EvalPlus，date 字段 2026-09-23） | 同左 | 在 `log.jsonl` 里（`correct`、`pred`、`gt`，经过 regrade） | 在 `log.jsonl` 里 |
| 日期（mtime） | 09-23 17:46–17:50 | 09-23 19:55–19:59 | 09-23 18:20 | 09-23 20:08 |

### 6.2 作废原因

- 早于 9/29。
- 协议和现在的 benchmark 方案不同：不传 reasoning_effort、temperature 0、自设 max_tokens（2048 / 6000，有截断）；每组只跑一次（文档自己写了同模型两次相差 2–4 个点）。
- 路由方案是旧的二档 / 三档（simple/normal/complex），和现在的 Jev 三维分类 + Policy v0 不是一回事。
- 各组不是完全同一时间窗口（ds 组单独补跑；code_all 由三次运行拼接）。

### 6.3 R16：中间轮次和已被取代的轮次

| 目录 | 行数 | 内容 | 状态 |
|---|---:|---|---|
| `smoke/` | 12 | kimi 6 + auto 6（含 padded 评测文件） | 冒烟测试 |
| `run1/` | 1,084 | kimi + auto 二档 | kimi 部分被 `final/` 复用 |
| `run2/` | 542 | auto 二档重跑 | 被 `final/` 复用 |
| `trial2/` | 空目录（`trial2.log` 有 141 行进度） | — | 未完成 |
| `math_smoke/` | 16 | 数学冒烟 | — |
| `math3/` | 600 | 数学三档 kimi + auto | 被 `math_all/` 复用 |
| `math_ds/` | 300 | 数学 ds 单组 | 被 `math_all/` 复用 |
| `code3/` | 1,084 | 代码三档 kimi + auto；auto→glm 有 63 次 length（glm 输出上限 2048） | **auto 部分作废**（JEV_AUTO_ROUTING_SUMMARY：“glm 因此作废过一轮”）；kimi 部分被 `code_all/` 复用 |
| `code4/` | 542 | 代码三档 auto 重跑（glm 上限提高） | 被 `code_all/` 复用 |
| `code_final/` | 1,084 | code3 kimi + code4 auto 的合并 | 被 `code_all/` 取代 |
| `code_ds/` | 542 | 代码 ds 单组 | 被 `code_all/` 复用 |

### 6.4 还能用什么

- 842 道题（542 代码 + 300 数学）的逐题旧版 Jev 档位判断：`tier`、`confidence`、`probabilities`。二档和三档各有一份，而且同一批题判过不止一次（run1/run2、math1/math3），可以看 Jev 判断的稳定性。这些数据可以作为分类器评测的数据点，但标签体系和现在的 task_type / execution_mode / capability_need 不同，需要映射后才能用。
- Jev 单次调用的成本和时延（约 0.2 s、约 $0.00002–0.00003），可作为粗略参考。
- 题目 ID 列表和 EvalPlus 判分流程（`exp_report.py`）。

---

## 7. R17：TrajectoryRL 组合实验文档（`/root/FUSION_METHODS_AND_DATA.md`）

只记录文档本身写了什么，不做延伸。

| 项 | 文档所述 |
|---|---|
| 作者 / 时间 | TrajectoryRL，2026-09-13 至 09-18，在 engy.ai 的开源模型目录上测量 |
| 题集 | HumanEval+ 164、MBPP+ 378（EvalPlus plus 隐藏测试）；Agentic-14（SPEC-19 rotation）、Agentic-26（SPEC-25）、Agentic-35（sandbox-agent 4.0.23 全集），三个 agentic 集相互嵌套，不独立 |
| Harness | `eval_pack.py`、`sandbox_harness.py`；sandbox-agent 镜像 4.0.23；agent 运行时 Hermes 0.20.5；每集 600 s 时限；判卷在新容器中进行，不用 LLM 判卷 |
| 模型 | deepseek-v4.1-flash、qwen3.8-27b、glm-5.3-flash、glm-5.2、glm-5.3、kimi-k3（表 2 列了冻结单价，含 cache read 价） |
| Reasoning | 表 4 区分 deepseek 和 qwen 的“no reasoning / reasoning”；其他模型的 effort 未写明 |
| 计分 | 代码题按通过率；agentic 按每场景隐藏测试通过比例求和（满分 14/26/35）；区分 Oracle 和 selection-rule score |
| 成本 | 按 provider token 数 × 表 2 单价计算，缓存读取按 cache 价；文档写了缓存命中 97.0–99.9% |
| 试次 | 多数行是单次运行；只有 in-context 组合实验有 3 次配对 |
| 总花费 | 约 $450（7 批） |
| 原始数据 | 文档 §7 提到的 `route_proxy.py`、`council_sn11_run.py`、`council_cross.py`、`eval_pack.py`，**本机全盘搜索都没有找到**，逐请求 JSONL 也不在本机 |
| Jev 分类 | 无（文档没有涉及 Jev） |

作废 / 复用：这是外部团队的文档，早于 9/29，按规则同样不能当成绩。本机只有文档，没有原始数据，无法复核。可以作为背景参考：题集定义、单价表，以及文档自己列出的威胁效度说明（噪声下限、600 s 预算偏向低延迟模型等）。9/23 实验的 REPORT 引用了它的 542 题基线数字。

---

## 8. 不算结果集的材料（顺带列出）

| 材料 | 内容 | 说明 |
|---|---|---|
| `report/deepswe_v1.1_trials.json` | DeepSWE 官方榜单逐 trial 数据，31,617 行（`n_trials` 字段与行数一致）；字段含 model、reasoning_effort、reward、tokens、cost_usd、peak context 等 | 外部官方数据，不是我们的结果；用于校准分析 |
| `report/deepswe_leaderboard_v1.1_snapshot.json` | 榜单汇总 70 条 | 同上 |
| `/root/bench/dswlb/raw/jobs/20260606-deep-swe-leaderboard-all-4x/` | HF `datacurve/deep-swe-leaderboard` 原始产物，`config.json` 12,204 个 | 同上 |
| `report/ctx_test/`（09-29 16:36–16:42） | 上下文容量探测，7 行：deepseek-v4-flash-0731 在输出上限很小时，280,621 / 541,458 / 833,499 / 1,042,101 输入 token 都返回 200，目标约 106 万时 400；deepseek-v4.1-flash 280,621 返回 200 | 容量探针，不是 benchmark 成绩；它是 9/29 当天做的，不在“9/29 之前”的范围内，但本来就不计分。可以作为容量参考 |
| `proxy/log/selftest.jsonl` | 代理自测 5 行，其中 3 行是 auto，有三维分类（workflow_operation/agentic/standard，sticky 命中一次；reasoning/direct/standard） | 链路自测，不是 benchmark。可作为 Jev 三维分类的零星数据点 |
| `tb4/audit.json`、`report/TB2_ENV_CHECK_2026-09-28.md` | TB4 审计、TB2 环境检查 | 没有模型成绩（TB2 smoke 在服务器上，见第 5 节） |
| `/root/bench/jev_eval/`（datasets、raw、splits、review） | Jev 分类评测集的构建材料（README：“本仓库不跑任何被测模型”） | 不是模型结果 |

---

## 9. 可复用内容汇总

| 类别 | 可以复用 | 来源 | 限制 |
|---|---|---|---|
| 题目 ID 列表 | HLE 88 个（R04，前 100 题的子集）、154 个（R06）；AB 前 30 题名（R08）；DeepSWE 2 题（R02/R11）；HumanEval+/MBPP+ 542、GSM8K/MATH-500 300 | 对应结果文件 | 只是 ID，没有有效分数 |
| Harness 配置 | `run_hle.sh`（9/29 已改为不传输出上限）、`run_ab.sh`、Pier `config.json`、`exp_run.py`/`exp_math.py` | 各目录 | 引用时去掉 key；9/27 的 DeepSWE 配置含 4 GB 内存和采样参数，不能照搬 |
| 成本 / 时延粗略参考 | 代理 `charged_micro` 与 `t_upstream_ms`（14 个文件）；AB runner 全价成本和代理实扣的对照（R08）；DeepSWE 每题 token 规模；9/23 的每题成本和时延 | 第 1、3、4、6 节 | 只能看量级；参数和现在的方案不一致 |
| Jev 分类数据点 | 9/23 旧版档位判断 842 题（二档、三档各一份，部分题有重复判断）；selftest 3 行三维分类 | 第 6、8 节 | 旧版标签体系不同；b0v4 的三维分类只在服务器上 |
| 截断 / 容量观察 | HLE 在 16K/32K 上限下的截断率；DS 在 DeepSWE 上的容量 400；ctx_test 的输入上限 | 第 2、4、8 节 | 定性参考 |

## 10. UNVERIFIED 清单

1. 第 5 节全部服务器结果（DeepSWE Auto 各轮、GLM 全量、服务器 bandit 复跑、TB2 smoke）以及服务器代理日志：本机没有，未核实。
2. 各模型在 Engy 上的具体版本和量化方式：日志只有 `miner` ID，没有版本信息。
3. R04 为什么 100 次请求都返回 200，但只存下 88 个预测（推测是客户端 600 s 超时）。
4. R09 实际跑到了哪些题：没有导出 JSON，代理日志里没有题名。
5. 9/23 三档实验中 glm-5.3-flash 输出上限是怎么设到 6000 的（从日志最大输出 6000 推断）；R14 的截断数没有统计。
6. R17 文档里的所有数字：本机没有原始数据，无法复核。
7. HLE 运行实际有没有发出 temperature：代理日志不记这个字段；根据官方代码判断没有发出。
