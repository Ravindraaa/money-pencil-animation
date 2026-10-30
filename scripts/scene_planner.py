"""Rule-based semantic storyboard planner for The Money Stickman.

No external API, model key, or network call is required. Each narration beat is
classified and enriched with drawable entities, labels, and emphasis values.
"""
from __future__ import annotations

import re
from typing import Any

RULES = [
    ("risk", r"risk|guarantee|uncertain|market|volatil|fee|tax|inflation|loss|downside", ["warning", "chart", "shield"]),
    ("growth", r"compound|growth|return|interest|million|future value|\$[\d,]+", ["chart", "coins", "calendar"]),
    ("investing", r"invest|stock|share|portfolio|fund|retirement|broker", ["person", "coins", "portfolio"]),
    ("housing", r"house|home|rent|mortgage|property|down payment", ["house", "wallet", "calendar"]),
    ("budget", r"budget|spend|expense|save|saving|cut back|habit|coffee|purchase|buy", ["wallet", "coins", "calendar"]),
    ("goal", r"goal|future|plan|afford|freedom|target|dream", ["target", "person", "coins"]),
]

ENTITY_RULES = [
    ("coffee", r"coffee|café|cafe"),
    ("cash", r"\$\s?[\d,]+|dollar|cash|money"),
    ("calendar", r"week|weekday|month|year|daily|every day"),
    ("chart", r"growth|return|compound|market|invest|stock"),
    ("house", r"house|home|rent|mortgage|property"),
    ("card", r"credit card|card|debt|loan|emi"),
    ("wallet", r"budget|spend|expense|save|saving|wallet"),
    ("warning", r"risk|not guaranteed|uncertain|fee|tax|inflation|loss"),
    ("target", r"goal|target|future|plan"),
]

def plan_segment(text: str, index: int = 0) -> dict[str, Any]:
    source = text.strip()
    lower = source.lower()
    scene_type = "explainer"
    for candidate, pattern, _ in RULES:
        if re.search(pattern, lower):
            scene_type = candidate
            break

    entities = [name for name, pattern in ENTITY_RULES if re.search(pattern, lower)]
    if not entities:
        entities = ["person", "idea"]
    # Keep a compact visual vocabulary per beat; order follows library priority.
    entities = entities[:4]

    amounts = re.findall(r"\$\s?[\d,]+(?:\.\d+)?|\b\d+(?:\.\d+)?%", source)
    numbers = re.findall(r"\b\d+(?:\.\d+)?\b", source)
    emphasis = amounts[:3] or numbers[:3]

    if scene_type == "risk":
        headline = "WHAT COULD CHANGE?"
    elif scene_type == "growth":
        headline = "TIME + CONSISTENCY"
    elif scene_type == "investing":
        headline = "PUT MONEY TO WORK"
    elif scene_type == "debt":
        headline = "UNDERSTAND THE COST"
    elif scene_type == "housing":
        headline = "PLAN THE BIG COSTS"
    elif scene_type == "budget":
        headline = "FOLLOW THE MONEY"
    elif scene_type == "goal":
        headline = "MOVE TOWARD YOUR GOAL"
    else:
        headline = "THE MONEY IDEA"

    return {
        "segment_index": index,
        "scene_type": scene_type,
        "headline": headline,
        "entities": entities,
        "emphasis": emphasis,
        "source_text": source,
    }

def build_storyboard(segments: list[str]) -> dict[str, Any]:
    if not segments or not all(isinstance(s, str) and s.strip() for s in segments):
        raise ValueError("segments must contain non-empty narration strings")
    return {
        "version": 1,
        "planner": "local-rules-v1",
        "scene_count": len(segments),
        "scenes": [plan_segment(text, i) for i, text in enumerate(segments)],
    }
