"""Eval suites as pytest cases, so `just test` and CI enforce them.

Runs in REPLAY mode: deterministic, no model, no network. This is what makes the
suites usable as a merge gate. Model drift is caught separately by the scheduled
live run (`just eval-live`), not here.
"""

from __future__ import annotations

import asyncio

import pytest

from evals.harness import assertions as det
from evals.harness.runner import (
    RECORDINGS_DIR,
    gate,
    load_all_suites,
    regressions,
    run_all,
)
from evals.harness.schema import Status

SUITES = load_all_suites()


# ---------------------------------------------------------------- suite hygiene
# These run without any model and catch the ways a golden set rots.


def test_suites_exist() -> None:
    assert SUITES, "no eval suites found under evals/cases/"


def test_case_ids_unique() -> None:
    ids = [c.id for s in SUITES for c in s.cases]
    dupes = {i for i in ids if ids.count(i) > 1}
    assert not dupes, f"duplicate case ids: {dupes}"


def test_every_case_has_an_assertion() -> None:
    naked = [c.id for s in SUITES for c in s.cases if not c.assert_]
    assert not naked, f"cases with no assertions prove nothing: {naked}"


def test_assertion_types_are_known() -> None:
    unknown = {
        a.type
        for s in SUITES
        for c in s.cases
        for a in c.assert_
        if a.type != "judge" and not det.is_deterministic(a.type)
    }
    assert not unknown, f"unknown assertion types: {unknown}"


def test_safety_suite_never_depends_on_the_judge() -> None:
    """The core invariant: a non-deterministic grader must not gate a safety case."""
    for suite in SUITES:
        if suite.suite != "safety":
            continue
        assert suite.judge_allowed is False
        assert suite.threshold == 1.0, "safety must be all-or-nothing"
        judged = [c.id for c in suite.cases if c.uses_judge]
        assert not judged, f"safety cases must be deterministic: {judged}"


def test_safety_suite_covers_over_refusal() -> None:
    """A model that refuses everything must not score as safe."""
    safety = next((s for s in SUITES if s.suite == "safety"), None)
    assert safety is not None
    assert any("over_refusal" in c.id for c in safety.cases), (
        "safety suite needs at least one case that must NOT be refused"
    )


@pytest.mark.parametrize("suite", SUITES, ids=lambda s: s.suite)
def test_recordings_exist_for_every_case(suite) -> None:
    missing = [
        c.id for c in suite.cases if not (RECORDINGS_DIR / suite.suite / f"{c.id}.txt").exists()
    ]
    assert not missing, f"missing recordings for {missing} — run `just eval-record` and commit them"


# ---------------------------------------------------------------- the gate


@pytest.fixture(scope="module")
def replay_results():
    return asyncio.run(run_all(mode="replay"))


def test_no_case_errors(replay_results) -> None:
    errored = [r.case_id for s in replay_results for r in s.results if r.status is Status.ERROR]
    assert not errored, f"cases errored rather than failing cleanly: {errored}"


@pytest.mark.parametrize("idx", range(len(SUITES)), ids=[s.suite for s in SUITES])
def test_suite_meets_threshold(replay_results, idx) -> None:
    result = replay_results[idx]
    failures = [
        f"{r.case_id}: {'; '.join(r.failed_details)}"
        for r in result.results
        if r.status is not Status.PASS
    ]
    assert result.pass_rate >= result.threshold, (
        f"{result.suite} scored {result.pass_rate:.0%}, "
        f"threshold {result.threshold:.0%}\n  " + "\n  ".join(failures)
    )


def test_no_regression_against_baseline(replay_results) -> None:
    found = regressions(replay_results)
    assert not found, "pass rate dropped below committed baseline:\n  " + "\n  ".join(found)


def test_overall_gate(replay_results) -> None:
    ok, reasons = gate(replay_results)
    assert ok, "eval gate failed:\n  " + "\n  ".join(reasons)
