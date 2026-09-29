"""Hand-picked boundary items (all label_source=human_review_required).

Every entry is a real item from the downloaded benchmarks.  recommended_gold is the
builder's own item-by-item judgement against the frozen V1 definitions
(prompts/jev_prompt_v1.json) and MUST be reviewed by a human before use as gold.
Selection rules where a random draw was used (seed 20260929) are documented in
DATASET_CONSTRUCTION.md; the resulting ids are frozen here so every build script can
exclude them from the clean datasets.

Tuple: (pair, bench_key, source_id, candidate_labels, recommended_gold, confidence, why_ambiguous)
"""

MR = "math vs reasoning"
GR = "general_qa vs research_analysis"
PW = "planning_design vs workflow_operation"
WR = "writing_language vs research_analysis"
RP = "reasoning vs planning_design"
CP = "coding vs planning_design"

BOUNDARY_PICKS = [
    # ---------------- math vs reasoning (LiveBench math puzzle-like + LiveBench reasoning spatial with counting/geometry)
    (MR, "livebench_math", "19241950caa11abbd7605583764dae33694742389a8b602cb553bc8276c63e55", ["math", "reasoning"], "reasoning", "low",
     "SMC truth-teller/liar puzzle filed under LiveBench math: the core is propositional logic, but it is a math-competition multiple-choice item."),
    (MR, "livebench_math", "75c1c68d2a38e7013b562fd74dd91a1d2b8d8e83303fdd6f7dc55686487101e6", ["math", "reasoning"], "math", "medium",
     "AIME take-1-or-4 token game: stated as a two-player game (reasoning-like) but solved by combinatorial game theory / modular counting."),
    (MR, "livebench_math", "1e7ae0275d5ca3174cea993d2a99a47b6e073542d389ed64d6d010018ced31a8", ["math", "reasoning"], "reasoning", "low",
     "AMC 'find the covered square' guessing game: adversarial search/strategy argument more than calculation; still a math-competition item."),
    (MR, "livebench_math", "c93744a0f460f32c8513fc6b475c76b57629df4a7ac83796a941dc5074ca87f6", ["math", "reasoning"], "math", "medium",
     "Round-robin tournament word problem: phrased as a puzzle about players, but solved with algebra and binomial counting."),
    (MR, "livebench_math", "01540b9b0b068942c8adeec17f825f0a9a3b9f52a1f61704bfebbb4c406064a7", ["math", "reasoning"], "math", "medium",
     "Set/Venn word puzzle about a class: short logical case analysis vs arithmetic with inclusion-exclusion."),
    (MR, "livebench_reasoning", "4f78225af2661b5b2f22f126fba54723cdbd02e16a8f89fe024f9f21fd54248b", ["reasoning", "math"], "math", "low",
     "LiveBench 'spatial' (reasoning) item asking the maximum number of pieces from 3 cuts of a dodecagon with constraints: a combinatorial-geometry counting question."),
    (MR, "livebench_reasoning", "a0383235b91e3e448468d0764fedb901f39a8c7855b214ba364e6956722c89cf", ["reasoning", "math"], "math", "low",
     "Spatial item: maximum pieces from 5 cuts of a nonagon with 3 parallel cuts - line-arrangement counting (math) presented as spatial reasoning."),
    (MR, "livebench_reasoning", "484f9d95e130b527cf40c85b560fc70edf30efc56fd57750ad78ee81f64deb47", ["reasoning", "math"], "reasoning", "low",
     "Spatial item with sphere radii and tangency counting: geometric configuration reasoning vs solid geometry."),
    (MR, "livebench_reasoning", "27eb08badf45383af3d99130de55ffe01e5723504d6d5fca8f9a7f672aad7e82", ["reasoning", "math"], "reasoning", "low",
     "Spatial item: shape formed by tangent points of spheres of given radii - 3D geometry vs spatial visualisation."),
    (MR, "livebench_reasoning", "115ee3f4cecb92009f145dd6ec96e9d05ce0b255f8a8a4d8bb686253be96aafc", ["reasoning", "math"], "reasoning", "medium",
     "Spatial item: counting pieces after plane cuts of a cube - spatial visualisation with solid-geometry flavour."),

    # ---------------- general_qa vs research_analysis (LongBench v2 items excluded from the research_analysis pool)
    (GR, "longbench_v2", "66f6b623bb02136c067c2646", ["general_qa", "research_analysis"], "general_qa", "medium",
     "Multi-Document QA (Multi-news) item that is a single-fact lookup ('primary cause of death per initial investigation') over many pasted articles."),
    (GR, "longbench_v2", "66fa6867bb02136c067c6b3b", ["general_qa", "research_analysis"], "general_qa", "medium",
     "Multi-news item: extract a drug's indication from one press release among many - information extraction over provided materials."),
    (GR, "longbench_v2", "66fd4f54bb02136c067c9987", ["general_qa", "research_analysis"], "general_qa", "medium",
     "Multi-news item: indication lookup from one press release - extraction, though the benchmark files it under multi-document QA."),
    (GR, "longbench_v2", "66fbab85bb02136c067c81dc", ["general_qa", "research_analysis"], "research_analysis", "low",
     "'Which one is noted in all the five passages?' - requires cross-document comparison but the answer is a lookup."),
    (GR, "longbench_v2", "66ec088c821e116aacb194d9", ["general_qa", "research_analysis"], "general_qa", "medium",
     "Table QA item 'What is MAIC?' - definition lookup inside a long structured document."),
    (GR, "longbench_v2", "66f2abc5821e116aacb2aab7", ["general_qa", "research_analysis"], "general_qa", "medium",
     "Table QA gene lookup with two conditions over a long table - extraction vs data analysis."),
    (GR, "longbench_v2", "66f590fa821e116aacb33f35", ["general_qa", "research_analysis"], "general_qa", "low",
     "Multi-Document (Academic) item asking a single paper's feature (GLM-130B inference) - conceptual QA vs literature synthesis."),
    (GR, "longbench_v2", "66f2ad89821e116aacb2ac92", ["general_qa", "research_analysis"], "general_qa", "low",
     "Academic multi-doc item: count the neural models used in two systems - lookup across two papers."),
    (GR, "longbench_v2", "67237d8ebb02136c067d6c06", ["general_qa", "research_analysis", "reasoning"], "general_qa", "medium",
     "Knowledge-graph reasoning item: Wikidata-style lookup (Irish counties by plate/ISO code) over a huge pasted KG."),
    (GR, "longbench_v2", "672494e5bb02136c067d7697", ["general_qa", "research_analysis"], "general_qa", "medium",
     "Knowledge-graph item: 'Which lawyer was educated at Phillips Exeter Academy?' - factual lookup, long provided context."),

    # ---------------- planning_design vs workflow_operation (AutomationBench planning-flavoured tasks + TB tasks)
    (PW, "automationbench", "marketing:1084", ["planning_design", "workflow_operation"], "workflow_operation", "medium",
     "'Plan next month's editorial calendar' from a backlog with variety constraints, but the deliverable is writing rows/records via tools."),
    (PW, "automationbench", "marketing:1102", ["planning_design", "workflow_operation"], "workflow_operation", "medium",
     "'Plan next week's social content calendar' following platform guidelines and adding scheduled posts - planning content executed as tool operations."),
    (PW, "automationbench", "sales:815", ["planning_design", "workflow_operation"], "workflow_operation", "medium",
     "Review team capacity vs limits and 'handle overages' - reallocation decision plus notifications."),
    (PW, "automationbench", "support:1585", ["planning_design", "workflow_operation", "research_analysis"], "workflow_operation", "low",
     "'Analyze ticket load for capacity planning' and redistribute tickets - capacity planning with ticket-system writes."),
    (PW, "automationbench", "hr:5130", ["planning_design", "workflow_operation"], "workflow_operation", "low",
     "'Q2 headcount plan finalized' for a board meeting - plan compilation delivered via SaaS tools."),
    (PW, "automationbench", "hr:5095", ["planning_design", "workflow_operation"], "workflow_operation", "medium",
     "Validate break-schedule requests against shift schedule/policies and update the schedule sheet - scheduling vs record operation."),
    (PW, "automationbench", "operations:1217", ["planning_design", "workflow_operation"], "workflow_operation", "medium",
     "Schedule a floor-plan signoff respecting move-plan policies, create Asana task/calendar entries."),
    (PW, "terminal_bench_4", "production-planning", ["planning_design", "workflow_operation", "coding"], "planning_design", "low",
     "TB4 Operations/Supply chain: produce a production plan using a provided gateway tool and config - planning content inside an operational system."),
    (PW, "terminal_bench_2", "constraints-scheduling", ["planning_design", "workflow_operation", "reasoning"], "planning_design", "low",
     "TB2 personal-assistant: find a meeting slot under calendar constraints and write the result as a file - scheduling vs calendar operation."),
    (PW, "terminal_bench_4", "ctr-optimization", ["planning_design", "workflow_operation"], "workflow_operation", "low",
     "TB4 Operations/Marketing: manage a live ad campaign over a simulated 48h - budget/bidding strategy vs operating the campaign system."),

    # ---------------- writing_language vs research_analysis (WritingBench analysis-flavoured subdomains)
    (WR, "writingbench", "91", ["writing_language", "research_analysis"], "research_analysis", "medium",
     "Investment Analysis: write an analysis of Kweichow Moutai from 5 years of supplied financial figures - report writing whose substance is analysis."),
    (WR, "writingbench", "103", ["writing_language", "research_analysis"], "research_analysis", "medium",
     "Market Analysis: semiconductor market report from supplied 2023 sales data."),
    (WR, "writingbench", "96", ["writing_language", "research_analysis"], "research_analysis", "medium",
     "Investment Analysis (zh): deep investment report from two years of pasted Gree annual reports (24K chars)."),
    (WR, "writingbench", "64", ["writing_language", "research_analysis"], "research_analysis", "low",
     "Financial Reports: Tencent Q1 2024 'business analysis briefing' for fund managers from supplied key figures - briefing (writing) vs segment analysis."),
    (WR, "writingbench", "967", ["writing_language", "research_analysis"], "writing_language", "low",
     "Financial Reports: write a press release for financial media from uploaded data, including 'detailed analysis' of indicators - PR copy vs analysis."),
    (WR, "writingbench", "672", ["writing_language", "research_analysis"], "writing_language", "medium",
     "Sales Report: revise an attached monthly vehicle sales report to a template (rewriting) that contains competitor market data."),
    (WR, "writingbench", "56", ["writing_language", "research_analysis"], "research_analysis", "medium",
     "User Research: customer churn analysis report from a pasted churn table."),
    (WR, "writingbench", "21", ["writing_language", "research_analysis"], "research_analysis", "low",
     "Literature Review (zh): write the related-work section from pasted reference papers (29K chars) - academic writing vs literature synthesis."),
    (WR, "writingbench", "486", ["writing_language", "research_analysis"], "research_analysis", "low",
     "Literature Review: quantum computing in cryptography review with specified aspects - survey writing vs research synthesis."),
    (WR, "writingbench", "151", ["writing_language", "research_analysis"], "research_analysis", "medium",
     "Regulatory Analysis: comparative analysis of Labor Law vs Labor Contract Law from a worker-protection perspective."),

    # ---------------- reasoning vs planning_design (PlanningBench items with a stated unique solution + NATURAL PLAN)
    (RP, "planningbench", "310", ["planning_design", "reasoning"], "planning_design", "low",
     "Maintenance re-scheduling with 'only one solution satisfies all conditions' - constraint satisfaction with a determinate answer, delivered as an operational plan."),
    (RP, "planningbench", "176", ["planning_design", "reasoning"], "planning_design", "low",
     "Training timetable change; prompt says a unique feasible schedule exists and asks to name conflicting hard rules if infeasible."),
    (RP, "planningbench", "394", ["planning_design", "reasoning"], "planning_design", "low",
     "Emergency water distribution with explicit tie-break rules 'to guarantee uniqueness' - rule-following allocation puzzle vs dispatch plan."),
    (RP, "planningbench", "429", ["planning_design", "reasoning"], "planning_design", "medium",
     "Exam and invigilation timetable under room/staff constraints with instructions to prove infeasibility if needed."),
    (RP, "planningbench", "225", ["planning_design", "reasoning"], "planning_design", "medium",
     "Team-building rotation: choose 3 activities and assign teams/rooms/leaders maximising a score with lexicographic tie-breaks."),
    (RP, "natural_plan", "calendar_scheduling_example_450", ["reasoning", "planning_design"], "reasoning", "low",
     "NATURAL PLAN calendar scheduling (7 people): find the one slot satisfying all busy intervals - pure constraint solving framed as scheduling."),
    (RP, "natural_plan", "calendar_scheduling_example_576", ["reasoning", "planning_design"], "reasoning", "low",
     "NATURAL PLAN calendar scheduling (2 people): interval intersection with a preference - constraint solving vs meeting planning."),
    (RP, "natural_plan", "meeting_planning_example_450", ["reasoning", "planning_design"], "planning_design", "low",
     "NATURAL PLAN meeting planning: maximise friends met given travel times and availability windows - optimisation/planning vs search puzzle."),
    (RP, "natural_plan", "meeting_planning_example_576", ["reasoning", "planning_design"], "planning_design", "low",
     "NATURAL PLAN meeting planning (6 friends) with travel matrix - itinerary optimisation."),
    (RP, "natural_plan", "trip_planning_example_263", ["reasoning", "planning_design"], "reasoning", "low",
     "NATURAL PLAN trip planning: order 4 cities with fixed stay lengths, a dated workshop and direct-flight constraints - a determinate constraint puzzle."),

    # ---------------- coding vs planning_design (TB tasks + WritingBench technical design docs)
    (CP, "terminal_bench_4", "photonic-waveguide-routing", ["coding", "planning_design"], "coding", "low",
     "Route photonic waveguides from a layout spec and write waypoint JSON - algorithmic routing/design problem solved by writing code in a sandbox."),
    (CP, "terminal_bench_4", "freight-dispatch-shift", ["coding", "planning_design", "workflow_operation"], "coding", "medium",
     "Build a stateful dispatch CLI for a construction-materials shift packet - software implementing dispatch planning rules."),
    (CP, "terminal_bench_4", "distributed-dedup", ["coding", "planning_design"], "coding", "medium",
     "Implement a distributed near-duplicate dedup pipeline on Spark - system design choices inside a coding task."),
    (CP, "terminal_bench_4", "live-database-cutover", ["coding", "planning_design", "workflow_operation"], "coding", "low",
     "Migrate a live app from MySQL to PostgreSQL - migration planning/cutover design vs code and ops changes."),
    (CP, "terminal_bench_2", "llm-inference-batching-scheduler", ["coding", "planning_design"], "coding", "medium",
     "Implement a shape-aware LLM inference batching scheduler - scheduling-policy design expressed as code."),
    (CP, "terminal_bench_4", "cargo-flight-dispatch", ["coding", "planning_design"], "coding", "medium",
     "Fix a flight-dispatch planner producing wrong fuel estimates - debugging planning software."),
    (CP, "terminal_bench_4", "wdm-design", ["coding", "planning_design", "research_analysis"], "planning_design", "low",
     "Design a 2D silicon-photonics demultiplexer (device design via simulation code)."),
    (CP, "writingbench", "492", ["coding", "planning_design", "writing_language"], "planning_design", "medium",
     "Technical Documentation: 20-30 page database performance optimisation plan (sharding strategy, index design) with SQL snippets."),
    (CP, "writingbench", "656", ["coding", "planning_design", "writing_language"], "planning_design", "low",
     "Technical Documentation (zh): recommender-system tech-sharing doc covering architecture, data flow, monitoring and key code/API examples."),
    (CP, "writingbench", "278", ["coding", "writing_language", "planning_design"], "coding", "low",
     "Technical Documentation (zh): write a standard PyTorch ViT training-pipeline technical document (code-heavy docs)."),
]


def boundary_ids():
    return {f"{b}:{s}" for (_, b, s, *_rest) in BOUNDARY_PICKS}
