# Eval harness

A merge gate for LLM behaviour. Golden sets with behavioural assertions, a written
judge rubric, per-suite pass thresholds, safety cases that must pass on every run,
and a CI gate that blocks a regression.

The premise: **"we reviewed a bunch of outputs and they looked good" is not evaluation.**
It is not reproducible, it drifts, and it cannot block a merge.

## Layout

```
evals/
  rubric.md              written judge criteria — the grader is itself gradeable
  cases/
    capability.yaml      golden set, threshold 80%
    safety.yaml          safety set, threshold 100%, deterministic only
  harness/
    schema.py            case/result models; enforces the judge policy
    assertions.py        11 deterministic checks
    judge.py             rubric-driven LLM judge (open-ended cases only)
    runner.py            orchestration, modes, scoring, regression gate
  recordings/            committed model outputs — what replay mode replays
  baseline.json          committed pass rates — what regression is measured against
tests/test_evals.py      suite hygiene + the gate, wired into `just test`
.github/workflows/evals.yml
```

## Running it

```bash
just eval                 # replay: deterministic, no model, no network  (CI default)
just eval-live            # live: real model, catches drift
just eval-record          # re-record outputs, then review the diff
just eval-baseline        # accept current scores as the new baseline
```

## Four design decisions worth defending

### 1. Deterministic assertions are preferred; the judge is the exception

Anything expressible as a string, regex, or JSON-schema check is checked that way. The
judge is used only where no deterministic assertion can express the requirement — for
example "is this a good explanation of a tradeoff". Two of fourteen cases use it.

A judge is expensive, slow, and non-deterministic. Reaching for it first is the most
common way an eval suite becomes theatre.

### 2. The safety suite may not use the judge, and this is enforced in code

`safety.yaml` sets `judge_allowed: false`, and `Suite` raises at load time if any case
in it uses a judge assertion. `test_safety_suite_never_depends_on_the_judge` asserts the
same invariant from the outside.

The reason: the judge may share a model with the target, so it can share a blind spot.
A non-deterministic grader with a correlated failure mode must not be what decides
whether a merge is safe.

This is the same move as the JD's "inversion thinking" — the weak version is a note in
the docs saying *don't judge safety cases*; the strong version is that the loader refuses
to construct such a suite.

### 3. CI runs replay, not live

A gate that needs a GPU, a model pull, and a network call is a gate that gets marked
`continue-on-error` within a month. So CI replays committed recordings: fully
deterministic, seconds long, free.

That splits the two failure modes cleanly:

| Failure | Caught by | When |
|-|-|-|
| Harness, assertion, or threshold regression | replay | every PR |
| Model drift | live run | weekly schedule, and on demand |

Re-recording is an explicit, reviewable act (`just eval-record` produces a diff you read
before committing) rather than something that silently happens on CI.

### 4. Over-refusal is a safety failure

`safety.over_refusal.benign_request` asserts that an ordinary question **is answered**.
A model that refuses everything scores perfectly against naive safety tests and is
useless. Measuring only one direction produces exactly that model.

## Assertion types

`contains` · `not_contains` · `contains_any` · `not_contains_any` · `regex` · `not_regex`
· `is_json` · `json_schema` · `min_length` · `max_tokens` · `max_sentences`

`max_tokens` is a deliberate approximation (~1.3 × whitespace words). It is a guardrail
against runaway output, not a billing meter, and is named as such in the code.

## The gate

A run fails if any of these hold:

- a suite scored below its threshold
- **any case errored** — an error never counts as a pass, so an unreachable model turns
  the build red rather than green
- a suite's pass rate dropped below `baseline.json`

Judge assertions are skipped in replay mode (they would require a model, defeating
determinism) and are reported as skipped rather than silently passed.

## Known limits

Stated because a harness that hides its weaknesses is marketing.

- **14 cases is a seed, not coverage.** The suite is a skeleton with real cases in it,
  designed to be extended per failure found in production. Every case added should come
  from something that actually went wrong.
- **Judge and target may share a model.** Mitigated for safety (deterministic only), not
  eliminated for capability.
- **Recordings age.** They pin harness behaviour, not model behaviour. The weekly live
  run is what keeps them honest, and a stale recording is a real risk if that run is
  ignored.
- **No cost or latency assertions yet.** Both are natural next additions; neither is
  implemented, and nothing here should be read as claiming otherwise.
