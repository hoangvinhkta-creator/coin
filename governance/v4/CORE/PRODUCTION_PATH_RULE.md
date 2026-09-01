# CORE — PRODUCTION PATH RULE (V4.3)

Status: CANONICAL (V4.3 overlay)
Layer: CORE — project-agnostic.

## The Rule

A counterexample is **production-realistic** only if it can be constructed from at least
one of these four canonical sources:

1. the current production schema / annotation inventory;
2. the current repository configuration;
3. an approved Golden fixture;
4. approved raw or production-like data.

If it cannot:

    DEFAULT = HARDENING

## The Fifth Source

A fifth source may be used to raise a finding to BLOCKING only when ALL of the following
are supplied:

- the specific source, named;
- the path by which it reaches the current runtime;
- the business consequence;
- an Owner Decision.

## Forbidden Justification

    "this could happen in the future"

is never sufficient to make a finding BLOCKING. Future grammar, defense-in-depth and
adversarial constructions that cannot be built from a canonical source are HARDENING by
definition, not by concession.

## What This Rule Does Not Do

It does not narrow review. A reviewer remains free — and is expected — to construct
adversarial cases that fail this test. Those cases are recorded as HARDENING with a
re-trigger condition. They are not discarded, and they are not silently downgraded: the
classification and the reason are both written down.

## Production Paths Are Declared, Not Inferred

The set of production paths is a PROJECT value and must be declared in the project layer.
An agent must not infer at execution time which files are "production"; it reads the
declaration. Tests, documentation, governance and tooling are not production paths unless
the project declares otherwise.
