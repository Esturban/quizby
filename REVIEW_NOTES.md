## Quizby Review Notes

Last reviewed: 2026-03-08

### Repo Snapshot

- Small Flask app with one HTML page and one quiz-generation API endpoint.
- Root config is now loaded intentionally through `config.Config` in the app factory.
- The default source preview now points to a real static asset and renders correctly.
- Frontend markdown output is sanitized before DOM insertion.
- A pytest suite now covers the main routes and the key `/generate-quiz` paths.

### Items Closed In This Pass

#### 1. Root config loading

- Status: fixed
- `quizby/core.py` now uses `app.config.from_object('config.Config')`.
- `test_config` still overrides defaults cleanly for tests.

#### 2. Default source-material preview

- Status: fixed
- The default viewer loads `dmbok-sample.txt`, which exists in `quizby/static/assets/`.
- The viewer now handles both PDF and text source previews.

#### 3. Unsafe quiz rendering

- Status: fixed
- `quizby/templates/index.html` now loads DOMPurify.
- `quizby/static/js/main.js` sanitizes rendered markdown before assigning it to `innerHTML`.
- Error rendering also uses `textContent` instead of string-built HTML.

#### 4. Raw backend error leakage

- Status: fixed
- `/generate-quiz` logs internal exceptions server-side.
- Production-style responses return a safe generic error message.
- Test mode still exposes exception text to keep automated checks precise.

#### 5. Missing validation coverage

- Status: fixed
- `tests/test_app.py` covers:
  - app factory config smoke
  - `/`
  - default source asset serving
  - invalid custom textbook input
  - mocked quiz generation success
  - safe production error handling

### Remaining Risks

- Rate limiting still uses `memory://`, so limits are per process rather than shared across instances.
- Uploaded textbook content is still passed through without token-budget trimming.
- `PyPDF2` currently raises a deprecation warning in the test environment.

### Current Validation Command

```bash
./venv/bin/python -m pytest -q
```
