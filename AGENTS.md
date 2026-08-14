# AGENTS.md

This file is the working contract for AI coding agents in this repository.

## Project Purpose

`fresh-daugherty` reproduces the modelling methods and case study of
Daugherty (1991), *Credibility of Long Term Forest Planning: Dynamic
Inconsistency in Linear Programming Based Forest Planning Models* (PhD
thesis, UC Berkeley), as closely as possible using `ws3` — openly,
transparently, and reproducibly — and backs a short peer-reviewed paper.

The thesis proves that LP-based forest-planning models solved as open-loop
formulations admit dynamically inconsistent (non-credible) plans. The thesis
is effectively inaccessible (archival hard copy only); this project makes the
result accessible and citable.

The durable source of truth is typed data records, the ws3 model, explicit LP
formulations, sequential-replanning simulation records, and verification
evidence — not one-off script chains.

## Reuse Boundary

This package stays aligned with the FRESH ecosystem and must not re-implement
domain packages:

- Consume `ws3` (`ForestModel`, LP machinery, Model I/II even-flow,
  actions/transitions). ws3's Model II path is stubbed; Phase 2 implements it
  in ws3 (a ws3 feature branch + release), not in this repo.
- Cross-reference `fresh-fuchs` (tsa29mini test instance,
  `tests/test_dynamic_inconsistency.py`).
- Do not re-implement ws3.

## Current Repo State

`fresh-daugherty` is at Phase 0 (scaffold). Track the active phase in
`ROADMAP.md`. Layout:

- `README.md`: concise public overview and current status.
- `ROADMAP.md`: phase/task roadmap and issue tracker map.
- `planning/`: design notes — `v0.1.0a1-plan.md` is the master plan.
- `CHANGE_LOG.md`: append-only project narrative (reverse-chronological).
- `RELEASE_NOTES.md`: release history.
- `pyproject.toml`: package metadata and optional dependency groups.
- `src/fresh_daugherty/`: package modules.
- `tests/`: package-backed tests (synthetic/public-safe fixtures only).
- `docs/`: Sphinx documentation.
- `examples/`: public-safe example configs.
- `.github/workflows/`: CI, docs, and release-artifact checks.
- `tmp/`: ignored local working area.

## Workflow Specs And Generated Outputs

Model inputs, simulation records, generated reports, and scratch execution
logs are local working material unless the maintainer explicitly asks to
track a sanitized artifact.

Rules:

- Keep `tmp/`, `local/`, `data/private/`, and `outputs/` ignored.
- Do not commit private data, raw transcripts, local workflow outputs,
  credentials, machine-specific paths, or unpublished documents.
- **Do not commit the scanned thesis PDF** (`tmp/daugherty1991credibility.pdf`
  is an archival copy; it is not redistributable). Reference it by citation.
- Tracked examples and tests must use synthetic or public-safe fixtures.
- Record provenance for every interpreted data source, LP formulation,
  simulation run, environment, and validation result.
- Keep model-specific assumptions explicit; document every reconstruction
  assumption where the thesis data cannot be recovered from the scan.

## Working Principles

- Read `AGENTS.md`, `ROADMAP.md`, `CHANGE_LOG.md`, and
  `planning/v0.1.0a1-plan.md` before making project-shaping changes.
- Keep CLI commands thin wrappers over Python APIs.
- Parse inputs at the boundary into typed Pydantic records; keep core logic
  free of defensive re-validation.
- Emit explicit diagnostics for missing data, unsupported ws3 features,
  failed solves, uncertain provenance, and failed validation.
- Reproduce the thesis faithfully; where a deviation is unavoidable, record
  it with a reason.
- Keep public repo content clean of private, irrelevant, or unpublished
  references.

## Planning Workflow

This repo follows the UBC-FRESH phase/task/subtask workflow:

- `ROADMAP.md` is the current plan and issue tracker map;
  `planning/v0.1.0a1-plan.md` is the detailed master plan.
- One roadmap phase maps to one GitHub parent issue and one feature branch.
- One roadmap task maps to one child issue linked from the parent issue body.
- Use at most three issue levels: phase, task, implementation subtask.
- Record issue numbers beside roadmap phases and tasks once created.
- Keep `ROADMAP.md`, `CHANGE_LOG.md`, planning notes, issue bodies, and PR
  descriptions synchronized.
- Open a PR from the phase branch to `main` only after phase tasks, tests,
  docs, and closeout notes are complete or explicitly deferred.

## Strict Development Workflow

- One active roadmap phase corresponds to one GitHub parent issue and one
  feature branch; create the parent issue before starting the phase.
- Work child issues one at a time, usually in roadmap order.
- Before closing a child issue, update every issue-body checklist item to
  checked, or rewrite the issue body to make clear which items were
  superseded or are not applicable.
- Close each child issue only after its repo changes, documentation,
  issue-body checklist, and verification are complete.
- Open a PR from the phase branch to `main` when the parent issue's child
  issues are complete or explicitly deferred; close the parent issue only
  after the PR merges.

## GitHub Issue And Comment Formatting

Issue bodies and comments must be readable as rendered Markdown. Use short
section labels on their own lines, real GitHub task-list syntax (one item per
line, never inline pseudo-checklists), and backticks for branch names, file
paths, commands, and commit hashes. Write issue bodies so a new lab student,
external collaborator, or coding agent can implement, verify, and close the
task without reading the original chat transcript (parent: phase id, status,
branch, roadmap links, goal, scope, out-of-scope, architecture notes, child
task checklist, acceptance criteria, verification, closeout requirements;
child: task id, parent, status, planning links, goal, scope, out-of-scope,
subtasks, acceptance criteria, verification, artifacts, risks, completion
metadata).

## Verification

Default local checks:

```bash
python -m ruff check .
python -m pytest
sphinx-build -b html docs _build/html -W
python -m build
twine check dist/*
```

Default CI must not require private data, commercial GIS software, local
desktop applications, credentials, Gurobi licenses, or network downloads
beyond package installation.
