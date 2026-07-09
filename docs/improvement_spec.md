# Quizby Improvement Spec

Last updated: 2026-03-08

## Goal

Improve the repository in the next implementation pass by fixing the highest-value correctness and safety issues first, then adding enough validation and documentation to keep future changes grounded.

## Problem Statement

The current repo is small and understandable, but several issues reduce confidence:

- Flask configuration is defined in the root `config.py` file but is not actually loaded into `app.config`.
- The default source-material viewer points to a missing PDF asset.
- LLM output is rendered into the DOM without sanitization.
- There are no tests or validation gates to prevent regressions.
- Documentation does not accurately reflect the live code paths and assets.

## Scope

In scope:

- Fix app configuration loading.
- Fix the broken default source-material preview.
- Make quiz rendering safe by sanitizing model output before DOM insertion.
- Add a minimal automated test suite.
- Refresh repo documentation to match actual behavior.

Out of scope for the first improvement pass:

- Major UI redesign.
- Swapping providers or reworking the prompting model architecture.
- Multi-instance distributed rate limiting.
- Deep deployment/platform changes beyond documentation corrections.

## Desired Outcomes

- `create_app()` loads intended configuration deterministically.
- The default “Show Source Material” action works.
- Untrusted model output cannot inject active HTML/JS into the page.
- Basic app routes and error paths are covered by tests.
- README and review notes remain aligned with the codebase.

## Work Plan

### Phase 1: Correctness

1. Fix configuration loading in `quizby/core.py`.
   - Use an explicit path or `from_object` strategy so root `config.py` is loaded intentionally.
   - Verify `SECRET_KEY` and `OR_MODEL` appear in `app.config`.

2. Fix the default source preview.
   - Either point the UI to an asset that exists or add the intended PDF to static assets.
   - Verify `/static/assets/...` returns `200` for the default preview target.

### Phase 2: Safety

3. Sanitize rendered quiz output in `quizby/static/js/main.js`.
   - Keep markdown support.
   - Strip or escape unsafe tags and attributes before assigning HTML to the DOM.
   - Preserve code block rendering and highlighting.

4. Reduce production error leakage.
   - Return user-safe API errors from `/generate-quiz`.
   - Log internal exceptions server-side instead of exposing raw details by default.

### Phase 3: Validation

5. Add tests.
   - App factory smoke test.
   - `/` route test.
   - asset-serving test for default preview resource.
   - `/generate-quiz` tests for invalid input / mocked generation path.

6. Add a small validation workflow.
   - `pytest`
   - optionally a simple import/smoke check if the repo stays lightweight

### Phase 4: Documentation

7. Update `README.md`.
   - Correct asset names and config behavior.
   - Document actual local run path and expected env vars.
   - Remove or rewrite any test instructions that are not real.

8. Keep `REVIEW_NOTES.md` as the review baseline.
   - Update after implementation so future review passes can diff current state against prior findings.

## Acceptance Criteria

- `create_app()` exposes expected config values from the intended source.
- Default source preview no longer 404s.
- Rendered quiz output is sanitized before DOM insertion.
- Test suite exists and passes locally.
- README matches actual repo structure and runtime behavior.

## Risks

- Sanitization can break formatting if introduced too aggressively.
- Config loading changes can unintentionally alter current environment precedence.
- Tests around LLM generation need mocking to avoid network coupling.

## Implementation Notes

- Preserve the app’s current structure unless a change clearly reduces complexity.
- Prefer small, explicit fixes over broad refactors.
- Add tests before or alongside fixes where practical, not as a final afterthought.

## First Execution Order

1. Fix config loading.
2. Fix default asset preview.
3. Add sanitization.
4. Add tests.
5. Update README and review notes.
