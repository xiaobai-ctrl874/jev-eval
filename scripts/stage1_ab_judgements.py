"""Item-by-item judgements for the 30 AutomationBench tasks sampled by build_stage1.py.

Written by reading each task's user prompt, task_name and final-state assertion types
(raw/automationbench/task_meta.jsonl).  No model was used.  Rules applied:
  clean     - one of the 6 task_types captures what the task is; tool use only gathers inputs /
              delivers the result.  taxonomy_gap = False.
  ambiguous - one of the 6 captures the cognitive core (e.g. a computation-and-report or a piece of
              writing), but the graded outcome also depends on business-procedure execution
              (updating records, routing, policy traps).  task_type = the best partial fit,
              taxonomy_gap = True.
  uncovered - the task essentially is "execute a business workflow / change external system state"
              (sync, enroll, schedule, update records, notify per procedure).  task_type = None,
              taxonomy_gap = True.
"""

_WF = ("The task is essentially executing a business workflow that changes external SaaS state ({what}); "
       "none of the 6 task_types describes that. {extra}")


def _unc(what, extra=""):
    return {"task_type": None, "fit": "uncovered", "gap": True,
            "reason": _WF.format(what=what, extra=extra).strip(), "why": "uncovered: " + what + "."}


AB_JUDGEMENTS = {
    # ---------------- finance
    "finance:4049": {
        "task_type": "research_analysis", "fit": "ambiguous", "gap": True,
        "reason": ("Core is a rule-defined reconciliation over two sheets (earned = billable hours x rate vs invoiced) "
                   "delivered as an emailed discrepancy report; research_analysis fits only partly because it is a "
                   "routine finance-ops procedure with skip rules and verbatim-value constraints, not open analysis. "
                   "No class for 'data operation / business procedure'."),
        "why": "compute-and-report reconciliation; only state change is sending the report email."},
    "finance:4067": {
        "task_type": "research_analysis", "fit": "ambiguous", "gap": True,
        "reason": ("Core is a formula-given margin computation vs targets, emailed as an 'analysis'; closest to "
                   "research_analysis (structured-data analysis) but the reasoning is a fixed row-level calculation "
                   "with filtering rules, i.e. a finance reporting procedure; math is an alternative reading."),
        "why": "compute GM% per row, compare to targets, email; only state change is the email."},
    "finance:4095": _unc("approve/return expense claims by a two-condition rule, update Status in the sheet, "
                         "email payroll and notify each employee",
                         "The rule check is trivial; the graded work is record updates and notifications."),
    "finance:4038": _unc("apply new prices to the Wave product catalog, archive discontinued products, confirm by email"),
    # ---------------- hr
    "hr:5028": {
        "task_type": "writing_language", "fit": "ambiguous", "gap": True,
        "reason": ("Deliverable is offer-letter email drafts (writing_language), but grading is about which "
                   "candidates get drafts, band checks and recent exceptions (procedure compliance) and the drafts are "
                   "created in Gmail; writing quality is secondary. No workflow class to capture the rest."),
        "why": "draft offer letters after cross-referencing bands/approvals; drafts are external state."},
    "hr:5124": _unc("send all-hands invites to the right roster, post an announcement, handle conflicting 1:1s "
                    "(with an exemption / do-not-reschedule trap)",
                    "It is scheduling execution, not constructing a plan, so reasoning_planning does not fit."),
    "hr:5108": _unc("schedule exit interviews per the standard process and notify parties; includes a data-privacy "
                    "trap (do not forward the roster to an external address)"),
    "hr:5088": _unc("enroll employees into compliance sessions, email each, update the tracker"),
    # ---------------- marketing
    "marketing:1167": _unc("screen sponsorship rows against the approval policy, set Status only for approved rows, "
                           "email finance the approved total",
                           "The policy check is the reasoning part, but the graded outcome is sheet cells and emails."),
    "marketing:1045": {
        "task_type": "research_analysis", "fit": "clean", "gap": False, "reason": None,
        "why": ("'Analyze our content inventory and recommend priorities' -> research_analysis; tools are used to read "
                "the sheet/Slack/inbox guidelines and to deliver the recommendation by email (agentic research_analysis).")},
    "marketing:1033": _unc("sync conference registrations into HubSpot and a Mailchimp list following batch notes"),
    "marketing:1128": _unc("run a guest-post outreach campaign: filter the target list by contact recency/pending "
                           "status and send pitches",
                           "Pitch writing (writing_language) is a secondary component; the graded outcome is who gets emailed."),
    # ---------------- operations
    "operations:1322": _unc("daily sensor check: filter online sensors below threshold under updated alert rules, "
                            "email facilities and post a Slack summary",
                            "The filtering is trivial analysis; it is a monitoring/alerting procedure."),
    "operations:1219": _unc("put the HQ drill on the ops calendar, update the Monday board item, conditionally alert Slack"),
    "operations:1354": {
        "task_type": "research_analysis", "fit": "ambiguous", "gap": True,
        "reason": ("Core is a proportional cost-allocation computation from bills and floor plans (research_analysis "
                   "or math), but the task also writes results into the allocation sheet, emails finance and posts to "
                   "Slack, i.e. an accounting procedure with state changes; neither class captures that."),
        "why": "allocation computation + sheet update + email + Slack."},
    "operations:1202": _unc("pick the most urgent vendor document, update a Trello card (due date, label) and add a "
                            "Basecamp todo"),
    # ---------------- sales
    "sales:528": _unc("run a lead through a five-level qualification decision table and create the right Salesforce "
                      "follow-up task",
                      "The conditional chain is reasoning-like, but it is following a documented business procedure "
                      "to a CRM write, not solving a reasoning/planning problem."),
    "sales:1112": _unc("follow up webinar attendees: create/update CRM leads and send personalized thank-you emails "
                       "to engaged attendees only"),
    "sales:838": _unc("quarterly customer health check: score accounts by policy, update Salesforce, alert #cs-alerts, "
                      "create tasks",
                      "Scoring is a partial research_analysis component; the graded outcome is CRM fields and alerts."),
    "sales:3": _unc("process stakeholder notification emails into Salesforce contacts per onboarding procedure"),
    # ---------------- support
    "support:1447": _unc("categorize Zoho Desk tickets by keyword rules, comment on each, notify department leads, post "
                         "a breakdown to Slack",
                         "Rule-based categorization is a lookup, not one of the 6 classes."),
    "support:1426": _unc("book callback events for on-hold tickets avoiding exclusions and double-booking, update "
                         "tickets, post a Slack summary"),
    "support:1472": _unc("produce the daily support digest from a template: categorize Hiver emails, notify "
                         "recipients, post to Slack, log a sheet row",
                         "The digest is a templated count summary; writing_language/research_analysis are only minor parts."),
    "support:1479": _unc("score HelpCrunch engagement by a model sheet, tag customers, create events, alert the "
                         "growth team, post a dashboard",
                         "Scoring is a partial research_analysis component; the graded outcome is tags/events/messages."),
    # ---------------- simple
    "simple:3051": _unc("schedule a Buffer post with given content"),
    "simple:3169": _unc("post a Slack announcement and create an Asana task"),
    "simple:3166": _unc("set an opportunity stage in Salesforce and post to Slack"),
    "simple:3188": _unc("read an email, create a HubSpot contact, send a welcome email"),
    "simple:3093": _unc("append a given expense row to a Google Sheet"),
    "simple:3200": _unc("read an email, create a HubSpot deal and a Zoom meeting"),
}
