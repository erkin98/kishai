"""LLM judge, governed by evals/rubric.md.

Used only where no deterministic assertion can express the requirement. Never used
to gate a safety case — see rubric.md, "Known limits".
"""

from __future__ import annotations

import json
from pathlib import Path

from .schema import AssertionResult, AssertionSpec, JudgeVerdict

RUBRIC_PATH = Path(__file__).resolve().parents[1] / "rubric.md"

_PROMPT = """You are grading a language-model output against a written rubric.

{rubric}

--- CASE ---
System prompt given to the model:
{system}

User input given to the model:
{user}

Model output to grade:
{output}

--- YOUR TASK ---
Score ONLY these dimensions: {dimensions}

Return STRICT JSON, nothing else, in exactly this shape:
{{"scores": {{"<dimension>": <1-5>}}, "reasons": {{"<dimension>": "<one sentence citing the text>"}}}}

If you are uncertain between two scores, choose the LOWER one.
"""


def load_rubric() -> str:
    return RUBRIC_PATH.read_text(encoding="utf-8")


def build_prompt(system: str, user: str, output: str, dimensions: list[str]) -> str:
    return _PROMPT.format(
        rubric=load_rubric(),
        system=system or "(none)",
        user=user,
        output=output,
        dimensions=", ".join(dimensions),
    )


def parse_verdict(raw: str) -> JudgeVerdict:
    """Parse the judge's reply. Raises ValueError if it did not honour the contract."""
    text = raw.strip()
    if text.startswith("```"):
        text = text.split("```")[1] if "```" in text[3:] else text[3:]
        text = text.lstrip("json").strip()
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end == -1:
        raise ValueError(f"judge returned no JSON object: {raw[:200]!r}")
    return JudgeVerdict.model_validate(json.loads(text[start : end + 1]))


def grade(verdict: JudgeVerdict, spec: AssertionSpec) -> AssertionResult:
    """Compare a verdict against the case's per-dimension thresholds."""
    thresholds = spec.dimensions or {}
    shortfalls: list[str] = []
    missing: list[str] = []

    for dim, minimum in thresholds.items():
        if dim not in verdict.scores:
            missing.append(dim)
            continue
        score = verdict.scores[dim]
        if score < minimum:
            why = verdict.reasons.get(dim, "")
            shortfalls.append(f"{dim}={score}<{minimum}" + (f" ({why})" if why else ""))

    if missing:
        # A judge that skips a dimension has not graded the case. Fail, do not assume.
        return AssertionResult(
            type="judge",
            passed=False,
            detail=f"judge omitted dimension(s): {', '.join(missing)}",
        )
    return AssertionResult(
        type="judge",
        passed=not shortfalls,
        detail="; ".join(shortfalls),
    )
