"""Deterministic assertions.

The rubric requires that anything checkable without a model IS checked without a model.
Every assertion here is pure, synchronous, and reproducible. The judge lives elsewhere.
"""

from __future__ import annotations

import json
import re
from collections.abc import Callable

from jsonschema import ValidationError
from jsonschema import validate as _js_validate

from .schema import AssertionResult, AssertionSpec

# Registry of deterministic checks: name -> (output, spec) -> (passed, detail)
Check = Callable[[str, AssertionSpec], "tuple[bool, str]"]
_CHECKS: dict[str, Check] = {}


def check(name: str) -> Callable[[Check], Check]:
    def deco(fn: Check) -> Check:
        _CHECKS[name] = fn
        return fn

    return deco


def _norm(text: str, spec: AssertionSpec) -> str:
    return text.lower() if spec.ignore_case else text


def _needles(spec: AssertionSpec) -> list[str]:
    v = spec.value
    return [str(x) for x in v] if isinstance(v, list) else [str(v)]


@check("contains")
def _contains(output: str, spec: AssertionSpec) -> tuple[bool, str]:
    needle = _norm(str(spec.value), spec)
    ok = needle in _norm(output, spec)
    return ok, "" if ok else f"expected to find {spec.value!r}"


@check("not_contains")
def _not_contains(output: str, spec: AssertionSpec) -> tuple[bool, str]:
    needle = _norm(str(spec.value), spec)
    found = needle in _norm(output, spec)
    return not found, f"forbidden string present: {spec.value!r}" if found else ""


@check("contains_any")
def _contains_any(output: str, spec: AssertionSpec) -> tuple[bool, str]:
    hay = _norm(output, spec)
    ok = any(_norm(n, spec) in hay for n in _needles(spec))
    return ok, "" if ok else f"none of {_needles(spec)!r} present"


@check("not_contains_any")
def _not_contains_any(output: str, spec: AssertionSpec) -> tuple[bool, str]:
    hay = _norm(output, spec)
    hits = [n for n in _needles(spec) if _norm(n, spec) in hay]
    return not hits, f"forbidden strings present: {hits!r}" if hits else ""


@check("regex")
def _regex(output: str, spec: AssertionSpec) -> tuple[bool, str]:
    flags = re.IGNORECASE if spec.ignore_case else 0
    ok = re.search(str(spec.value), output, flags) is not None
    return ok, "" if ok else f"pattern did not match: {spec.value!r}"


@check("not_regex")
def _not_regex(output: str, spec: AssertionSpec) -> tuple[bool, str]:
    flags = re.IGNORECASE if spec.ignore_case else 0
    m = re.search(str(spec.value), output, flags)
    return m is None, f"forbidden pattern matched {m.group(0)!r}" if m else ""


@check("is_json")
def _is_json(output: str, spec: AssertionSpec) -> tuple[bool, str]:
    try:
        json.loads(_strip_fences(output))
    except (json.JSONDecodeError, ValueError) as exc:
        return False, f"not valid JSON: {exc}"
    return True, ""


@check("json_schema")
def _json_schema(output: str, spec: AssertionSpec) -> tuple[bool, str]:
    try:
        payload = json.loads(_strip_fences(output))
    except (json.JSONDecodeError, ValueError) as exc:
        return False, f"not valid JSON: {exc}"
    try:
        _js_validate(instance=payload, schema=spec.value)
    except ValidationError as exc:
        return False, f"schema violation: {exc.message}"
    return True, ""


@check("min_length")
def _min_length(output: str, spec: AssertionSpec) -> tuple[bool, str]:
    n = len(output.strip())
    ok = n >= int(spec.value)
    return ok, "" if ok else f"length {n} < {spec.value}"


@check("max_tokens")
def _max_tokens(output: str, spec: AssertionSpec) -> tuple[bool, str]:
    # Deliberate approximation: ~1.3 tokens per whitespace word. This is a guardrail
    # against runaway output, not a billing meter. Named approximate so nobody
    # mistakes it for a real tokenizer.
    approx = int(len(output.split()) * 1.3)
    ok = approx <= int(spec.value)
    return ok, "" if ok else f"~{approx} tokens > {spec.value}"


@check("max_sentences")
def _max_sentences(output: str, spec: AssertionSpec) -> tuple[bool, str]:
    sentences = [s for s in re.split(r"[.!?]+(?:\s|$)", output.strip()) if s.strip()]
    ok = len(sentences) <= int(spec.value)
    return ok, "" if ok else f"{len(sentences)} sentences > {spec.value}"


def _strip_fences(text: str) -> str:
    """Models wrap JSON in markdown fences despite instructions. Tolerate it."""
    t = text.strip()
    if t.startswith("```"):
        t = re.sub(r"^```[a-zA-Z]*\s*", "", t)
        t = re.sub(r"\s*```$", "", t)
    return t.strip()


def is_deterministic(assertion_type: str) -> bool:
    return assertion_type in _CHECKS


def run(output: str, spec: AssertionSpec) -> AssertionResult:
    """Run one deterministic assertion. Raises KeyError for unknown types."""
    fn = _CHECKS[spec.type]
    passed, detail = fn(output, spec)
    return AssertionResult(type=spec.type, passed=passed, detail=detail)


def known_types() -> list[str]:
    return sorted(_CHECKS)
