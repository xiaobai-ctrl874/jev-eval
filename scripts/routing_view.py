"""What the decision model (Jev) is shown for the FIRST routing call of a task.

Two logical objects, never mixed:

* the buyer's original request — forwarded to the served model untouched;
* the routing view built here — read-only copies, sent only to Jev.

Nothing in this module mutates `messages` or `tools`.

Two modes (`build_routing_view`):

* ``full`` — the estimated Jev input (the whole request text + compact tools +
  the fixed question prompt) fits `limit` (30,000 tokens by default, measured
  Jev ceiling ≈ 33.5K). Jev reads every message in full: no clipping, no
  summary, no sampling.
* ``compact_view`` — it does not fit. Built by code, no extra model call:
  the task instruction (kept whole), a short system goal, the compact
  environment, objective metadata and — only when the task depends on supplied
  material and no tool environment is offered — the chunks of that material
  most relevant to the instruction (BM25, lexical), until `view_target`.

Tools are never sent as JSON schema: name + category + one-sentence
description, or, for a large catalog, the categories with their tool counts.

Routing is sticky (one call per task), so this runs once per task; a growing
conversation is not this module's concern.
"""
from __future__ import annotations

import json
import math
import re
from collections import Counter

JEV_SAFE_INPUT_LIMIT = 30_000      # tokens; measured Jev maximum ≈ 33,559 (2026-09-30)
VIEW_TARGET = 12_000               # compact_view budget (tokens), well under the limit
TOOL_BUDGET = 3_000                # compact tool list larger than this is aggregated by category
INSTRUCTION_MAX = 3_000            # a text part/segment larger than this is material, not instruction
SYSTEM_GOAL_CHARS = 400
CHUNK_TOKENS = 400

_CJK = re.compile(r"[　-〿぀-ヿ㐀-䶿一-鿿가-힯＀-￯]")


def estimate_tokens(obj) -> int:
    """Conservative token estimate without the decision model's tokenizer:
    CJK characters ≈ 1.1 tokens each, digits 1 token each (tokenizers split
    numbers per digit), other text ≈ 1 token per 2.5 characters. Calibrated on
    the Stage 1 requests and the routing-view tests (see JEV_ROUTING_VIEW_TEST.md)."""
    s = obj if isinstance(obj, str) else json.dumps(obj, ensure_ascii=False)
    cjk = len(_CJK.findall(s))
    digits = sum(ch.isdigit() for ch in s)
    return round(cjk * 1.1 + digits + (len(s) - cjk - digits) / 2.5)


# ---- tools -----------------------------------------------------------------------

_CATEGORY_RULES = (
    (("bash", "shell", "exec", "terminal", "run_command", "command"), "command_execution"),
    (("git", "github", "gitlab", "repo", "pull_request"), "repository_operations"),
    (("file", "read", "write", "edit", "str_replace", "ls", "glob", "grep", "directory"), "file_operations"),
    (("browser", "web", "fetch_url", "search_web", "navigate", "http"), "web_browsing"),
    (("sheet", "excel", "airtable", "table"), "spreadsheet_operations"),
    (("calendar", "event", "meeting"), "calendar_operations"),
    (("slack", "teams", "discord", "gmail", "email", "mail", "sms", "message"), "messaging"),
    (("salesforce", "hubspot", "crm", "pipedrive", "zoho", "lead", "deal", "opportunit"), "crm_operations"),
    (("jira", "asana", "trello", "linear", "ticket", "zendesk", "freshdesk", "issue"), "ticketing_project"),
    (("stripe", "quickbooks", "xero", "invoice", "payment"), "finance_operations"),
    (("sql", "database", "db_", "query"), "database"),
    (("api_search", "api_fetch", "search_tools", "api"), "api_access"),
)


def _tool_fields(t) -> tuple[str, str]:
    if not isinstance(t, dict):
        return (str(t), "") if t else ("", "")
    f = t.get("function") if isinstance(t.get("function"), dict) else t
    return str(f.get("name") or ""), str(f.get("description") or "")


def tool_category(name: str) -> str:
    n = name.lower()
    for keys, cat in _CATEGORY_RULES:
        if any(k in n for k in keys):
            return cat
    return (n.split("_")[0] or "other") + "_operations"


def _first_sentence(desc: str, limit: int = 160) -> str:
    s = desc.strip().split("\n")[0]
    s = re.split(r"(?<=[.!?。])\s", s, maxsplit=1)[0]
    return s[:limit]


def compact_tools(tools) -> list[dict]:
    out = []
    for t in tools or ():
        name, desc = _tool_fields(t)
        if name:
            out.append({"name": name, "category": tool_category(name), "description": _first_sentence(desc)})
    return out


def tool_environment(tools) -> tuple[object, str]:
    """(representation, kind): the compact list, or {category: count} when that
    list would exceed TOOL_BUDGET. kind is 'none' | 'compact' | 'aggregated'."""
    comp = compact_tools(tools)
    if not comp:
        return None, "none"
    if estimate_tokens(comp) <= TOOL_BUDGET:
        return comp, "compact"
    return dict(sorted(Counter(c["category"] for c in comp).items())), "aggregated"


# ---- message text ----------------------------------------------------------------

def _parts(content) -> tuple[list[str], int]:
    """(text parts, non-text part count) of one message's content."""
    if isinstance(content, str):
        return [content], 0
    if isinstance(content, list):
        texts, other = [], 0
        for p in content:
            if isinstance(p, dict) and p.get("type") == "text":
                texts.append(p.get("text") or "")
            elif p is not None:
                other += 1
        return texts, other
    return ([] if content is None else [str(content)]), 0


def _full_messages(messages) -> tuple[list[dict], int]:
    out, media = [], 0
    for m in messages or ():
        if not isinstance(m, dict):
            continue
        texts, other = _parts(m.get("content"))
        media += other
        msg = {"role": m.get("role"), "content": "\n".join(texts)}
        if other:
            msg["non_text_parts"] = other
        out.append(msg)
    return out, media


_BLOCK = re.compile(r"<(?P<tag>[A-Za-z][\w-]{0,30})(?:\s[^>]*)?>(?P<body>.*?)</(?P=tag)>|```.*?```", re.S)


def _split_instruction(text: str) -> tuple[str, list[str], str]:
    """Separate the task instruction from supplied material inside ONE user
    message. Returns (instruction, material blocks, how)."""
    if estimate_tokens(text) <= INSTRUCTION_MAX:
        return text, [], "whole_message"
    blocks, kept, pos = [], [], 0
    for m in _BLOCK.finditer(text):
        body = m.group("body") if m.group("tag") else m.group(0)
        if estimate_tokens(body) > INSTRUCTION_MAX:
            kept.append(text[pos:m.start()])
            kept.append(f"[attached material {len(blocks) + 1} omitted: ~{estimate_tokens(body)} tokens]")
            blocks.append(body)
            pos = m.end()
    kept.append(text[pos:])
    instr = "".join(kept).strip()
    if blocks and estimate_tokens(instr) <= INSTRUCTION_MAX:
        return instr, blocks, "delimited_blocks"
    # No structure separates instruction from material: keep the beginning and
    # the end (where a request states its task) and treat the rest as material.
    head, tail = _slice_tokens(text, 1000, from_end=False), _slice_tokens(text, 2000, from_end=True)
    middle = text[len(head):len(text) - len(tail)]
    instr = head + f"\n[... ~{estimate_tokens(middle)} tokens of material omitted ...]\n" + tail
    return instr, [middle], "unstructured_head_tail"


def _slice_tokens(text: str, budget: int, *, from_end: bool) -> str:
    # at most 2.5 characters per estimated token, so the answer is never longer than this
    lo, hi = 0, min(len(text), int(budget * 2.5) + 1)
    while hi - lo > 32:                       # longest prefix/suffix within budget
        mid = (lo + hi) // 2
        piece = text[len(text) - mid:] if from_end else text[:mid]
        if estimate_tokens(piece) <= budget:
            lo = mid
        else:
            hi = mid
    return text[len(text) - lo:] if from_end else text[:lo]


# ---- lexical retrieval -------------------------------------------------------------

_WORD = re.compile(r"[a-z0-9]+|[㐀-䶿一-鿿]")


def _terms(s: str) -> list[str]:
    return _WORD.findall(s.lower())


def _chunks(text: str, size: int = CHUNK_TOKENS) -> list[str]:
    """~size-token chunks, cut at a newline when one is near the end. Works on
    offsets (no copying of the remaining text), so it is linear in len(text)."""
    out, pos, n = [], 0, len(text)
    window = int(size * 2.5) + 1
    while pos < n:
        piece = _slice_tokens(text[pos:pos + window], size, from_end=False) or text[pos:pos + 1]
        cut = piece.rfind("\n")
        if cut > len(piece) // 2:
            piece = piece[:cut + 1]
        out.append(piece)
        pos += len(piece)
    return out


def bm25_top(query: str, chunks: list[str], budget: int, k1: float = 1.5, b: float = 0.75) -> list[int]:
    """Indices of the most query-relevant chunks whose total size fits `budget`,
    returned in document order."""
    q = set(_terms(query))
    if not chunks or not q:
        return []
    docs = [Counter(_terms(c)) for c in chunks]
    n, avg = len(docs), (sum(sum(d.values()) for d in docs) / max(1, len(docs))) or 1.0
    df = Counter(t for d in docs for t in q if t in d)
    scores = []
    for i, d in enumerate(docs):
        dl, s = sum(d.values()), 0.0
        for t in q:
            if t in d:
                idf = math.log(1 + (n - df[t] + 0.5) / (df[t] + 0.5))
                s += idf * d[t] * (k1 + 1) / (d[t] + k1 * (1 - b + b * dl / avg))
        scores.append((s, i))
    picked, used = [], 0
    for s, i in sorted(scores, key=lambda x: (-x[0], x[1])):
        if s <= 0:
            break
        size = estimate_tokens(chunks[i])
        if used + size > budget:
            continue
        picked.append(i); used += size
    return sorted(picked)


# ---- the view ----------------------------------------------------------------------

def build_routing_view(messages: list, tools=None, *, prompt_tokens: int = 0,
                       limit: int = JEV_SAFE_INPUT_LIMIT, view_target: int = VIEW_TARGET) -> tuple[dict, dict]:
    """(state for Jev, info for the log). Never mutates its arguments."""
    env, tool_repr = tool_environment(tools)
    full_msgs, media = _full_messages(messages)
    n_tools = len(compact_tools(tools))
    full_state = {"messages": full_msgs}
    if env is not None:
        full_state["tools" if tool_repr == "compact" else "tool_categories"] = env
    original = estimate_tokens(full_msgs)
    est_full = estimate_tokens(full_state) + prompt_tokens
    info = {"routing_mode": "full", "original_estimated_tokens": original, "jev_estimated_tokens": est_full,
            "tools_original_count": n_tools, "tool_representation": tool_repr,
            "retrieval_used": False, "retrieved_chunk_count": 0}
    if est_full <= limit:
        return full_state, info

    # compact_view
    system = next((m["content"] for m in full_msgs if m["role"] in ("system", "developer")), "")
    users = [m["content"] for m in full_msgs if m["role"] == "user"]
    current = users[-1] if users else ""
    instruction, material, how = _split_instruction(current)
    other_turns = [m["content"] for m in full_msgs if m["role"] not in ("system", "developer")][:-1] if users else []
    material = material + [t for t in other_turns if t.strip()]
    state = {"task_instruction": instruction}
    if system:
        state["system_goal"] = _first_sentence(system, SYSTEM_GOAL_CHARS)
    if env is not None:
        state["environment_tools" if tool_repr == "compact" else "environment_tool_categories"] = env
    meta = {"original_input_tokens": original, "conversation_turns": len(users) + sum(m["role"] == "assistant" for m in full_msgs),
            "modality": "text" + ("+media" if media else "")}
    if how == "delimited_blocks":
        meta["attachments_present"] = True
        meta["attachment_count"] = len(material) - len(other_turns)
    if media:
        meta["non_text_parts"] = media
    if n_tools:
        meta["tool_count"] = n_tools
    state["context_metadata"] = meta
    info.update({"routing_mode": "compact_view", "instruction_source": how})
    # Retrieval only when the task works on supplied material and no tool
    # environment is offered: an agentic request is classified from its task and
    # environment, not from the repository it ships.
    if material and env is None:
        room = view_target - estimate_tokens(state) - prompt_tokens
        chunks = [c for blob in material for c in _chunks(blob)]
        idx = bm25_top(instruction, chunks, max(0, room))
        if idx:
            state["relevant_context"] = [chunks[i] for i in idx]
            info.update({"retrieval_used": True, "retrieved_chunk_count": len(idx)})
    info["jev_estimated_tokens"] = estimate_tokens(state) + prompt_tokens
    return state, info
