## workflow_operation: AutomationBench (local v1.0.6)

1. **What it measures**: Agents executing realistic business workflows in a simulated environment of 47 SaaS tools (CRM, Gmail, Slack, Calendar, Sheets, ticketing, accounting, HRIS...). Each task = trigger prompt + pre-populated world state; graded by assertions on the FINAL world state (e.g. `salesforce_field_equals`, `gmail_message_sent_to_with_body_contains`, `slack_message_not_in_channel`). Metrics: `partial_credit` and strict `task_completed_correctly` (official pass rate = mean of strict over the 600 non-simple tasks). Official leaderboard uses a held-out private set; the repo is the public set.
2. **Data format**: Tasks are Python dicts in `automationbench/domains/<domain>/tasks.py` (huge files, e.g. sales/tasks.py ~32k lines), assembled into a HF `datasets.Dataset` by `get_<domain>_dataset()`. Row fields: `example_id`, `prompt` (list of messages: exactly `[system, user]` for all 800 tasks), `answer` (""), `info` = {`zapier_tools` (per-task tool name list), `initial_state` (world state JSON), `assertions`, `task_name` (moved from `task` at dataset build time, e.g. `sales.multi_hop_lookup`, `simple.email_sf_contact_phone_update`)}. `apply_noise()` injects deterministic distractor records into initial_state (seed = example_id); it does not change the prompt.
   - Counts (verified by loading all loaders locally): simple 200, sales 100, marketing 100, operations 100, support 100, finance 100, hr 100 → 800 total (600 scored). sales/tasks.py has 106 `"task":` literals but only 100 are included in the dataset list.
   - User prompt length (chars, median/max): simple 185/368, sales 282/714, marketing 437/744, operations 729/1254, support 434/1168, finance 463/744, hr 406/745. Median `zapier_tools` per task: simple 2, domains 8–12.
3. **Native category labels**: domain (7 values above) and `task_name` (`<domain>.<slug>`, unique per task). No finer taxonomy field.
4. **Native difficulty labels**: none per task. Only implicit: `simple` domain = "foundational single- and two-step tasks", excluded from score (README). Private set is "purposely harder" (not released).
5. **Direct vs agentic**: agentic (multi-turn tool use, default `--max-steps 50`; system prompt mentions ~50 tool-using turns).
6. **Purity for workflow_operation**: HIGH. All tasks are graded on external state changes (emails sent, CRM fields updated, sheet rows written, Slack posts). Checked assertion types: only 3/800 tasks have exclusively negative ("not sent / not exists") assertions (1 sales, 2 simple) — i.e. the correct action is to NOT act (policy trap). Many domain tasks embed reasoning sub-steps (FX conversion, weighted scoring, policy lookups in emails/sheets), but the output is always an operation, so they remain workflow_operation positives.
7. **Items belonging to another task_type**: none cleanly. Caveat: some tasks are "report/recap" style (e.g. `sales.historical_win_loss_recap`, finance reporting) where the substance is data synthesis, but the deliverable is still posting/sending via tools → keep as workflow_operation; optionally tag as secondary research_analysis.
8. **Recommendation**: **FULL** 600 public domain tasks (stratified by domain if sampling), plus `simple` 200 as a separate easy/"standard"-candidate slice (not a benchmark-defined capability label — do not map to capability_need automatically).
9. **License / gating / size**: MIT (Copyright 2026 Zapier, Inc.). Not gated. Local repo; reconstructed first-request dumps: api 1.2 MB, limited_zapier 8.7 MB, zapier 1.2 MB.
10. **Sources**: https://github.com/zapier/AutomationBench ; paper https://arxiv.org/abs/2604.18934 ; https://zapier.com/benchmarks ; local /root/bench/AutomationBench (pyproject version 1.0.6).

**How the first request is built (verified in code, no model run)**:
- `scripts/eval.py` → `get_combined_dataset(domains)` → `AutomationBenchEnv(dataset, rubric, max_turns, toolset, search_top_k)` (verifiers `StatefulToolEnv`). CLI default `--toolset api` (note: the Python function default is "zapier", but argparse default is "api").
- messages = task `prompt` as-is: `system` = one shared `SYSTEM_PROMPT` (identical across all 800 tasks: "You are a workflow automation agent. Execute the requested tasks using the available tools. Do not ask clarifying questions ... budget of ~50 tool-using turns ... list only items you acted on ..."), `user` = the task text. No initial state is shown in the prompt — the agent must discover it via tools.
- tools depend on toolset (`runner.py` `__init__` + `setup_state`):
  - `api` (default): 3 generic tools for every task: `api_search(query, top_k)`, `api_fetch(method, url, params, body)`, `base64_encode(text)` → tools reveal nothing about the task domain.
  - `limited_zapier`: only the task's `info.zapier_tools` (from a registry of 549 Zapier-style tools, e.g. `salesforce_find_records`, `gmail_send_email`).
  - `zapier`: 2 meta-tools `search_tools` / `execute_tool`.
- Script: `/root/bench/jev_eval/scripts/automationbench_first_request.py [api|limited_zapier|zapier]` (run with `/root/bench/AutomationBench/.venv/bin/python`) → `/root/bench/jev_eval/raw/automationbench/first_requests_<toolset>.jsonl` (domain, example_id, messages, tools, zapier_tools_listed). Note `task` field is None in the dumps because the task name lives in `info.task_name`; add it if needed.

---

## Agentic sources (execution_mode only)

### DeepSWE (local /root/bench/deep-swe)
1. **Measures**: frontier coding agents on original, long-horizon SWE tasks (feature implementation in real OSS repos), program-based verifiers in a separate pristine container.
2. **Format**: Harbor task format. `tasks/` has 117 entries = **113 task dirs** + `dataset.toml`, `manifest.json`, `manifest.schema.json`, `README.md` (so "117 dirs" is actually 113 tasks + 4 files). Each task: `task.toml` (metadata: task_id, display_title, display_description, category, language, repository_url, base_commit_hash; docker_image; agent timeout 10800 s, no-network), `instruction.md` (= the prompt the agent sees; 571–5,484 chars, median ~2.2k), `environment/`, `tests/`, `solution/`. Dataset name `datacurve/deep-swe-1-1` (v1.1).
3. **Categories**: `category`: feature_request 106, enhancement 3, bugfix 4. `language`: go 34, python 34, typescript 35, javascript 5, rust 5.
4. **Difficulty**: none.
5. **agentic** (mini-swe-agent in sandbox, hours-long).
6. **Purity**: 100% coding (for task_type), 100% agentic.
7. Other task_types: none.
8. **Recommendation**: FULL (113) as agentic+coding positives.
9. License: Apache-2.0 for Datacurve contributions; upstream repos under their own permissive licenses (PROVENANCE.md). Docker images on public.ecr.aws (not needed for classification).
10. Sources: https://github.com/datacurve-ai/deep-swe ; https://deepswe.datacurve.ai/ ; Pier https://github.com/datacurve-ai/pier

**First request (mini-swe-agent via Pier)** — verified in local Pier 0.3.1 source (`pier/agents/installed/mini_swe_agent.py`): command is `mini-swe-agent --yolo --model=<m> --task=<instruction.md text> --output=... -c mini.yaml [-c agent.cost_limit=0] [...] --exit-immediately`. So the config is mini-swe-agent's built-in **`mini.yaml`** (tool-calling mode), `--yolo` (no confirm), Pier default cost_limit=0 (no limit). The task text passes through `render_instruction` (only changes it if a prompt_template_path is configured; none by default) and MCP info is appended only if MCP servers are configured.
- `mini.yaml` (local mini-swe-agent 2.4.6; matches official https://github.com/SWE-agent/mini-swe-agent/blob/main/src/minisweagent/config/mini.yaml — checked system_template + head of instance_template, step_limit 0, cost_limit 3., mode confirm):
  - system: `You are a helpful assistant that can interact with a computer.`
  - user (instance_template): `Please solve this issue: {{task}}` + "You can execute bash commands and edit files..." + Recommended Workflow (6 steps, submit with `echo COMPLETE_TASK_AND_SUBMIT_FINAL_OUTPUT`) + Command Execution Rules + `<system_information>{{system}} {{release}} {{version}} {{machine}}</system_information>` + useful command examples.
  - tools: single `bash` tool `{"command": string}` (`minisweagent/models/utils/actions_toolcall.py` BASH_TOOL).
  - The older text-based `default.yaml` (```mswea_bash_command``` blocks, no tools) is NOT what Pier uses.
- DeepSWE README only says "All leaderboard scores were produced with Pier running mini-swe-agent on Modal"; exact mini-swe-agent version / cost limit / step limit for the leaderboard is **UNVERIFIED** (not documented).
- Script: `/root/bench/jev_eval/scripts/miniswe_first_request.py` (run with `/root/bench/.msa/bin/python`) → `/root/bench/jev_eval/raw/agentic_first_requests/{deepswe,tb4,tb2}_miniswe_first_requests.jsonl` (113 / 66 / 89 rows). uname fields are placeholders (they come from the task container at runtime).

### Terminal-Bench 4.0 (local /root/bench/tb4/terminal-bench-4.0.0)
1. **Measures**: agents completing hard, realistic tasks in a terminal (continuous benchmark, tagged releases).
2. **Format**: Harbor format, `tasks/<id>/{task.toml, instruction.md, environment/, tests/, solution/}`; 66 task dirs + `dataset.toml` (header comment says "terminal-bench/terminal-bench-3", dataset name `terminal-bench/terminal-bench`). `archive/` holds 2 removed tasks (erp-procurement-planning, gpt2-codegolf). Instruction = `instruction.md` (starts with a harbor-canary HTML comment); median ~1.6k chars, max 6.5k.
3. **Categories**: `category`: Software 18, Science 14, ML 11, Operations 9, Hardware 5, Security 5, Media 4; plus `subcategory` (29 values, e.g. Systems, Inference, Frontend, Chemistry, CAD, Claims, Biology, Algorithms, Logistics, Math, Finance, Compliance, Marketing...) and `tags`, `expert_time_estimate_hours`.
4. **Difficulty**: no discrete difficulty field; 6 tasks have free-text `difficulty_explanation`; `expert_time_estimate_hours` numeric.
5. agentic.
6. **Purity**: execution_mode agentic 100%. task_type is mixed — most are coding/terminal engineering, but some are domain workflows/analysis (e.g. Claims auditing, freight dispatch planning, utility billing via legacy GUI, genomics variant cataloguing, Math subcategory). Use only as agentic signal, or label task_type per item manually.
7. Other task_types: Science/*, Operations/Claims/Logistics/Compliance/Finance/Marketing, Math subcategory → research_analysis / planning_design / workflow_operation / math candidates (needs per-item review).
8. **Recommendation**: FULL for execution_mode=agentic; FILTERED (manual per-item task_type) if used for task_type.
9. License Apache-2.0 (GitHub API). Releases: v3.0.0 2026-07-23, v4.0.0 2026-08-26 (GitHub API); v4.0.0 = 74 v3 tasks − 8 removed = 66 (release notes, via fetch).
10. Sources: https://github.com/harbor-framework/terminal-bench ; https://github.com/harbor-framework/terminal-bench/releases ; https://hub.harborframework.com/datasets/terminal-bench/terminal-bench ; https://www.tbench.ai/

### Terminal-Bench 2.0 (local /root/bench/tb2/terminal-bench)
1. Measures: same family, 2.0 release.
2. Format: 89 task dirs directly under the folder (no tasks/ subdir), each `task.toml` + `instruction.md` + environment/tests/solution. Official repo harbor-framework/terminal-bench-2 (laude-institute/terminal-bench-2 redirects) has 89 task dirs (GitHub API) — matches local.
3. Categories (`category`): software-engineering 26, system-administration 9, security 8, scientific-computing 8, data-science 8, file-operations 5, debugging 5, model-training 4, mathematics 4, data-processing 4, machine-learning 3, video-processing, personal-assistant, optimization, games, data-querying (1 each). Plus tags, expert/junior time estimates.
4. **Difficulty**: `difficulty` = easy 4 / medium 55 / hard 30.
5. agentic. 6–7. Mostly coding/sysadmin; `mathematics` (4), `data-science`/`scientific-computing` partly research_analysis/math; `personal-assistant` (1) workflow-like.
8. Recommendation: FULL for execution_mode=agentic; filtered per item for task_type.
9. Apache-2.0 (per repo page). 10. https://github.com/harbor-framework/terminal-bench-2 ; run: `harbor run --dataset terminal-bench@2.0`.

**First request for TB**: depends on agent. With mini-swe-agent via Harbor (`harbor/agents/installed/mini_swe_agent.py`: `mini-swe-agent --yolo ... --task=<instruction> -c mini ...`) it is the same mini.yaml system/instance template + bash tool as above, `{{task}}` = instruction.md. The TB reference agent Terminus-2 instead uses its own template (`harbor/agents/terminus_2/templates/terminus-json-plain.txt`: "You are an AI assistant tasked with solving command-line tasks in a Linux environment..." with JSON analysis/plan/commands, no native tools).
