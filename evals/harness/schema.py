"""Case and result models for the eval harness."""

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, model_validator


class AssertionSpec(BaseModel):
    """One assertion attached to a case."""

    type: str
    value: Any = None
    ignore_case: bool = False
    dimensions: dict[str, int] | None = None  # judge assertions only

    @model_validator(mode="after")
    def _check_shape(self) -> AssertionSpec:
        if self.type == "judge":
            if not self.dimensions:
                raise ValueError("judge assertion requires 'dimensions'")
        elif self.type not in _VALUELESS and self.value is None:
            raise ValueError(f"assertion '{self.type}' requires a 'value'")
        return self


_VALUELESS = {"is_json"}


class Case(BaseModel):
    """A single golden-set case."""

    id: str
    description: str = ""
    system: str = ""
    input: str
    assert_: list[AssertionSpec] = Field(default_factory=list, alias="assert")

    model_config = {"populate_by_name": True}

    @property
    def uses_judge(self) -> bool:
        return any(a.type == "judge" for a in self.assert_)


class Suite(BaseModel):
    """A named collection of cases with its own gate."""

    suite: str
    threshold: float = 0.8
    judge_allowed: bool = True
    cases: list[Case]

    @model_validator(mode="after")
    def _enforce_judge_policy(self) -> Suite:
        if not self.judge_allowed:
            offenders = [c.id for c in self.cases if c.uses_judge]
            if offenders:
                raise ValueError(
                    f"suite '{self.suite}' forbids judge assertions but these cases use one: "
                    + ", ".join(offenders)
                )
        return self


class Status(str, Enum):
    PASS = "pass"
    FAIL = "fail"
    ERROR = "error"  # harness/model failure, not a model-quality failure


class AssertionResult(BaseModel):
    type: str
    passed: bool
    detail: str = ""


class CaseResult(BaseModel):
    case_id: str
    status: Status
    output: str = ""
    assertions: list[AssertionResult] = Field(default_factory=list)

    @property
    def failed_details(self) -> list[str]:
        return [f"{a.type}: {a.detail}" for a in self.assertions if not a.passed]


class SuiteResult(BaseModel):
    suite: str
    threshold: float
    results: list[CaseResult]

    @property
    def total(self) -> int:
        return len(self.results)

    @property
    def passed(self) -> int:
        return sum(1 for r in self.results if r.status is Status.PASS)

    @property
    def errored(self) -> int:
        return sum(1 for r in self.results if r.status is Status.ERROR)

    @property
    def pass_rate(self) -> float:
        return self.passed / self.total if self.total else 0.0

    @property
    def gate_passed(self) -> bool:
        # An ERROR never counts as a pass. A harness that reports green because the
        # model was unreachable is worse than one that reports red.
        return self.errored == 0 and self.pass_rate >= self.threshold


class JudgeVerdict(BaseModel):
    """Strict JSON contract the judge must return."""

    scores: dict[str, int]
    reasons: dict[str, str] = Field(default_factory=dict)
