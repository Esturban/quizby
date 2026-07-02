# AGENTS.md

Work style: telegraph; noun-phrases ok; drop grammar; min tokens.

## Core
- `CLAUDE.md` + `GEMINI.md` point here. This file is primary; read it first.
- Local repo instructions win.
- `@.wolf/OPENWOLF.md` optional; local-only if present.
- Skills = workflows. This file = hard rules only.
- Token efficiency: query a local code-graph/memory layer (CodeGraph, codebase-memory-mcp, or `.wolf`) before grep/read-heavy exploration; offload broad exploration to subagents; keep decision-bearing edits single-threaded.

## Defaults
- Simplicity first. No speculative features.
- Surgical changes. Touch only what the task needs.
- Bugs: add regression test when it fits.
- Verify before ship/PR: run the adapter `## Verify` command if present; green required, red blocks.
- Failure => feature: when the agent repeats a mistake, add a tool / validator / lint or ast-grep rule / hook — not a prompt tweak.
- Loops: set an explicit stop condition + iteration/cost cap; on limit, halt and report — don't spin.
- Use repo package manager/runtime. No swaps without approval.
- Read repo docs before coding. Update docs/changelog for user-visible changes.
- Secrets: env vars only if already exported. Never hardcode.

## Done-gate (no "done" on intent — only on evidence)
- Not done until acceptance criteria met AND shown. Saying done without proof = not done.
- Acceptance source: `.acceptance` (one check per line) if present, else the task / PRD / spec criteria.
- Survives context loss: re-read the acceptance source after `/clear` or a crash. Never trust remembered progress — verify against the file.
- Each check must pass: command exits 0, or criterion demonstrably true. One unmet => not done; report which + why, then halt.
- Don't move the goalposts to pass. Unmeetable / wrong criterion => surface to the user; never silently drop it.

## Git flow (traceable; next agent picks it up cold)
- Branch off the default branch: `feat|fix|chore/<slug>`. Never commit straight to main.
- Atomic, phased commits — one logical change each; Conventional Commits.
- Verify green (adapter `## Verify`) before each commit; red = don't commit.
- Push / open PR only when the user asks. No amend / rebase / force / destructive ops unless asked.
- Never include AI attribution or `Co-Authored-By`.
- Traceable by default: commit message says *why*; leave the tree clean at each checkpoint.
- Handoff: end a session with a one-line status (done / next) so the next agent resumes without re-deriving context.

## Routing
- Complex feature / unclear scope => `planner`
- Architecture => `architect`
- Feature / bug fix => `tdd-guide`
- Code changed => `code-reviewer`
- Pre-merge / anti-pattern audit => `anti-patterns-auditor`
- Python review => `python-reviewer`
- Security-sensitive => `security-reviewer`
- Build/type errors => `build-error-resolver`
- Browser-critical flows => `e2e-runner`

## Models
- simple (grep, format, boilerplate) => `claude-haiku-4-5`
- default (implementation, debug, refactor) => `claude-sonnet-4-6`
- complex (architecture, security, 5+ files) => `claude-opus-4-8`

## Skills
- TDD => `/tdd`
- Review => `/review`
- Investigate => `/investigate`
- Ship/deploy/PR => `/ship`

## Stack
- Python. Deps + scripts via repo manager (uv / poetry / pip).
- Tests: pytest. Lint/format: ruff. Types: mypy if configured.
- Run tests before ship. TDD for new behavior.

## Verify
- Gate (run before ship/PR): `ruff check . && ruff format --check . && pytest -q` (+ `mypy .` if types configured).
- Wire the same command into pre-commit + CI — that is the deterministic gate, not the model.

## Model routing
Route by task type (policy: rules/_meta.yaml). Pick the cheapest tier that fits.
- default -> sonnet
- security -> opus
- review -> sonnet
- test -> sonnet
- deploy -> sonnet
- architecture -> opus
- refactor -> haiku
- hooks -> haiku
- laravel -> sonnet
- nextjs -> sonnet
- python -> sonnet
- web -> sonnet
- performance -> sonnet
