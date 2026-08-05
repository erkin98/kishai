"""Eval runner: loads suites, produces outputs, applies assertions, gates on thresholds.

Three modes:
  live    — call the model for real
  record  — call the model and save each output to evals/recordings/
  replay  — read recorded outputs; no model needed  (CI default)

CI defaults to replay because a gate that needs a GPU and a network is a gate that
gets disabled. Recordings are committed, so a regression in the *harness* or the
*assertions* is caught deterministically on every PR. Model drift is caught by the
scheduled live run.
"""

from __future__ import annotations

import asyncio
import json
import os
from pathlib import Path
from typing import Literal

import yaml

from . import assertions as det
from . import judge as judge_mod
from .schema import (
    AssertionResult,
    Case,
    CaseResult,
    Status,
    Suite,
    SuiteResult,
)

Mode = Literal["live", "record", "replay"]

# A 9B model on a long generation can exceed 3 minutes. The first live run errored
# three cases on a 180s timeout — an ERROR never counts as a pass, so the gate went
# red rather than silently green. Overridable for slower hardware.
_TIMEOUT_S = int(os.environ.get("EVAL_TIMEOUT_S", "900"))

# Reasoning models (qwen3.x, deepseek-r1) emit chain-of-thought into a separate
# `thinking` field. Observed on a live run: ~6.7k chars of reasoning exhausted the
# default context and `content` came back EMPTY, which the harness then scored as a
# quality failure. Give the answer room, and pin temperature to 0 for reproducibility.
_GEN_OPTIONS = {
    "temperature": 0,
    "num_ctx": int(os.environ.get("EVAL_NUM_CTX", "8192")),
    "num_predict": int(os.environ.get("EVAL_NUM_PREDICT", "4096")),
}

EVALS_DIR = Path(__file__).resolve().parents[1]
CASES_DIR = EVALS_DIR / "cases"
RECORDINGS_DIR = EVALS_DIR / "recordings"
BASELINE_PATH = EVALS_DIR / "baseline.json"


# ---------------------------------------------------------------- loading


def load_suite(path: Path) -> Suite:
    return Suite.model_validate(yaml.safe_load(path.read_text(encoding="utf-8")))


def load_all_suites() -> list[Suite]:
    return [load_suite(p) for p in sorted(CASES_DIR.glob("*.yaml"))]


# ---------------------------------------------------------------- model access


def _recording_path(suite: str, case_id: str) -> Path:
    return RECORDINGS_DIR / suite / f"{case_id}.txt"


async def _generate(
    case: Case,
    suite: str,
    mode: Mode,
    model: str,
    client,
) -> str:
    """Produce the model output for a case, honouring the mode."""
    if mode == "replay":
        path = _recording_path(suite, case.id)
        if not path.exists():
            raise FileNotFoundError(
                f"no recording for {case.id}; run `just eval-record` to create it"
            )
        return path.read_text(encoding="utf-8")

    messages = []
    if case.system:
        messages.append({"role": "system", "content": case.system})
    messages.append({"role": "user", "content": case.input})

    response = await client.chat(
        model=model, messages=messages, stream=False, options=_GEN_OPTIONS
    )
    output = _extract_content(response)

    # An empty completion is an infrastructure failure, not a quality failure.
    # Found on the second live run: qwen3.5:9b returned empty content for one case,
    # the harness recorded a 0-byte file, and the assertions then reported it as the
    # model answering badly. Misattributing an outage as a bad model is how a harness
    # loses trust. Raise so it surfaces as ERROR, and never persist an empty recording.
    if not output.strip():
        raise RuntimeError(
            "model returned empty content (no output to evaluate) — "
            "infrastructure or generation failure, not a quality signal"
        )

    if mode == "record":
        path = _recording_path(suite, case.id)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(output, encoding="utf-8")

    return output


def _extract_content(response) -> str:
    """Ollama returns {'message': {'content': ...}}; tolerate object or dict."""
    if isinstance(response, dict):
        return response.get("message", {}).get("content", "")
    message = getattr(response, "message", None)
    return getattr(message, "content", "") if message is not None else str(response)


# ---------------------------------------------------------------- evaluation


async def _judge_case(case: Case, spec, output: str, model: str, client) -> AssertionResult:
    dimensions = list((spec.dimensions or {}).keys())
    prompt = judge_mod.build_prompt(case.system, case.input, output, dimensions)
    try:
        response = await client.chat(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            stream=False,
            options=_GEN_OPTIONS,
        )
        verdict = judge_mod.parse_verdict(_extract_content(response))
    except Exception as exc:  # judge unavailable or off-contract
        return AssertionResult(type="judge", passed=False, detail=f"judge failed: {exc}")
    return judge_mod.grade(verdict, spec)


async def run_case(
    case: Case,
    suite: Suite,
    mode: Mode,
    model: str,
    judge_model: str,
    client,
) -> CaseResult:
    try:
        output = await _generate(case, suite.suite, mode, model, client)
    except Exception as exc:
        return CaseResult(
            case_id=case.id,
            status=Status.ERROR,
            assertions=[AssertionResult(type="generate", passed=False, detail=str(exc))],
        )

    results: list[AssertionResult] = []
    for spec in case.assert_:
        if spec.type == "judge":
            if mode == "replay":
                # Judging in replay would call a model, defeating determinism.
                results.append(
                    AssertionResult(type="judge", passed=True, detail="skipped in replay mode")
                )
            else:
                results.append(await _judge_case(case, spec, output, judge_model, client))
        elif det.is_deterministic(spec.type):
            results.append(det.run(output, spec))
        else:
            results.append(
                AssertionResult(
                    type=spec.type,
                    passed=False,
                    detail=f"unknown assertion type (known: {det.known_types()})",
                )
            )

    status = Status.PASS if all(r.passed for r in results) else Status.FAIL
    return CaseResult(case_id=case.id, status=status, output=output, assertions=results)


async def run_suite(suite: Suite, mode: Mode, model: str, judge_model: str, client) -> SuiteResult:
    results = [await run_case(c, suite, mode, model, judge_model, client) for c in suite.cases]
    return SuiteResult(suite=suite.suite, threshold=suite.threshold, results=results)


class _OllamaHTTP:
    """Minimal stdlib fallback client.

    The harness needs exactly one capability: `chat(model, messages, ...) -> response`.
    Preferring the app's own LLMService (dogfooding) but falling back to this keeps the
    eval suite runnable without installing the app's runtime — which matters because a
    harness that cannot run is a harness nobody runs.
    """

    def __init__(self, host: str = "http://localhost:11434") -> None:
        self.host = host.rstrip("/")

    async def chat(self, model: str, messages: list[dict], stream: bool = False, **kw):
        import json as _json
        import urllib.request

        payload = {
            "model": model,
            "messages": messages,
            "stream": False,
            **({"options": kw["options"]} if "options" in kw else {}),
        }

        def _post():
            req = urllib.request.Request(
                f"{self.host}/api/chat",
                data=_json.dumps(payload).encode(),
                headers={"Content-Type": "application/json"},
            )
            with urllib.request.urlopen(req, timeout=_TIMEOUT_S) as resp:
                return _json.loads(resp.read())

        return await asyncio.to_thread(_post)


def build_client(host: str = "http://localhost:11434"):
    """Use the app's LLMService when its deps are installed; otherwise stdlib HTTP."""
    try:
        from backend.app.services.llm_service import LLMService

        return LLMService(host=host).client
    except ImportError:
        return _OllamaHTTP(host=host)


async def run_all(
    mode: Mode = "replay",
    model: str = "llama3.2",
    judge_model: str | None = None,
    host: str = "http://localhost:11434",
    client=None,
) -> list[SuiteResult]:
    suites = load_all_suites()
    if mode != "replay" and client is None:
        client = build_client(host)
    return [await run_suite(s, mode, model, judge_model or model, client) for s in suites]


# ---------------------------------------------------------------- regression gate


def load_baseline() -> dict[str, float]:
    if not BASELINE_PATH.exists():
        return {}
    return json.loads(BASELINE_PATH.read_text(encoding="utf-8")).get("pass_rates", {})


def write_baseline(results: list[SuiteResult]) -> None:
    BASELINE_PATH.write_text(
        json.dumps(
            {"pass_rates": {r.suite: round(r.pass_rate, 4) for r in results}},
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def regressions(results: list[SuiteResult], tolerance: float = 0.0) -> list[str]:
    """Suites whose pass rate dropped below the committed baseline."""
    baseline = load_baseline()
    out = []
    for r in results:
        prior = baseline.get(r.suite)
        if prior is not None and r.pass_rate < prior - tolerance:
            out.append(f"{r.suite}: {r.pass_rate:.0%} < baseline {prior:.0%}")
    return out


def gate(results: list[SuiteResult]) -> tuple[bool, list[str]]:
    """The CI decision. Returns (ok, reasons_for_failure)."""
    reasons: list[str] = []
    for r in results:
        if r.errored:
            reasons.append(f"{r.suite}: {r.errored} case(s) errored")
        if r.pass_rate < r.threshold:
            reasons.append(f"{r.suite}: {r.pass_rate:.0%} below threshold {r.threshold:.0%}")
    reasons.extend(regressions(results))
    return not reasons, reasons


def summarise(results: list[SuiteResult]) -> str:
    lines = []
    for r in results:
        mark = "PASS" if r.gate_passed else "FAIL"
        lines.append(
            f"[{mark}] {r.suite:12s} {r.passed}/{r.total} "
            f"({r.pass_rate:.0%}, threshold {r.threshold:.0%})"
        )
        for cr in r.results:
            if cr.status is not Status.PASS:
                lines.append(f"       - {cr.case_id} [{cr.status.value}]")
                for d in cr.failed_details:
                    lines.append(f"           {d}")
    return "\n".join(lines)


def _main() -> int:
    import argparse

    p = argparse.ArgumentParser(prog="evals", description="Run the eval suites.")
    p.add_argument("--mode", choices=["live", "record", "replay"], default="replay")
    p.add_argument("--model", default="llama3.2")
    p.add_argument("--judge-model", default=None)
    p.add_argument("--host", default="http://localhost:11434")
    p.add_argument(
        "--update-baseline",
        action="store_true",
        help="overwrite baseline.json with this run (review the diff before committing)",
    )
    args = p.parse_args()

    results = asyncio.run(run_all(args.mode, args.model, args.judge_model, args.host))
    print(summarise(results))

    if args.update_baseline:
        write_baseline(results)
        print(f"\nbaseline written to {BASELINE_PATH}")
        return 0

    ok, reasons = gate(results)
    if not ok:
        print("\nGATE FAILED:")
        for r in reasons:
            print(f"  - {r}")
        return 1
    print("\nGATE PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
