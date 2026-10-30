"""Topic-agnostic, deterministic storyboard planner for Money Stickman."""
from __future__ import annotations
import re
from typing import Any

RULES = [
    ("risk", r"risk|guarantee|uncertain|market|volatil|fee|tax|inflation|loss|downside|could fall"),
    ("debt", r"debt|credit card|loan|interest rate|apr|borrow|mortgage payment"),
    ("housing", r"house|home|rent|mortgage|property|down payment"),
    ("growth", r"compound|growth|return|interest|future value|\$[\d,]+"),
    ("investing", r"invest|stock|share|portfolio|fund|retirement|broker"),
    ("budget", r"budget|spend|expense|save|saving|cut back|habit|purchase|buy|cost"),
    ("goal", r"goal|future|plan|afford|freedom|target|dream|priority"),
]
ENTITY_RULES = [
    ("coffee", r"coffee|café|cafe"), ("house", r"house|home|rent|mortgage|property"),
    ("card", r"credit card|card|debt|loan|emi"), ("chart", r"growth|return|compound|market|invest|stock"),
    ("calendar", r"week|weekday|month|year|daily|every day"), ("warning", r"risk|not guaranteed|uncertain|fee|tax|inflation|loss"),
    ("wallet", r"budget|spend|expense|save|saving|wallet"), ("cash", r"\$\s?[\d,]+|dollar|cash|money"),
    ("target", r"goal|target|future|plan"),
]
HEADLINES = {
    "risk":"CHECK THE DOWNSIDE", "debt":"UNDERSTAND THE COST", "housing":"PLAN THE BIG COSTS",
    "growth":"TIME CAN CHANGE THE MATH", "investing":"PUT MONEY TO WORK",
    "budget":"FOLLOW THE MONEY", "goal":"MOVE TOWARD YOUR GOAL", "explainer":"THE MONEY IDEA",
}
def plan_segment(text: str, index: int = 0) -> dict[str, Any]:
    source=text.strip()
    if not source: raise ValueError("Narration beats cannot be empty")
    lower=source.lower()
    scene_type=next((kind for kind,pattern in RULES if re.search(pattern,lower)), "explainer")
    entities=[name for name,pattern in ENTITY_RULES if re.search(pattern,lower)][:4] or ["person","idea"]
    amounts=re.findall(r"\$\s?[\d,]+(?:\.\d+)?|\b\d+(?:\.\d+)?%",source)
    emphasis=amounts[:3] or re.findall(r"\b\d+(?:\.\d+)?\b",source)[:3]
    return {"segment_index":index,"scene_type":scene_type,"headline":HEADLINES[scene_type],
            "entities":entities,"emphasis":emphasis,"source_text":source}
def build_storyboard(segments: list[str]) -> dict[str, Any]:
    if not segments or not all(isinstance(s,str) and s.strip() for s in segments):
        raise ValueError("segments must contain non-empty narration strings")
    scenes=[plan_segment(s,i) for i,s in enumerate(segments)]
    return {"version":2,"planner":"local-rules-v2","scene_count":len(scenes),"scenes":scenes}
