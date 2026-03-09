# Quizby

Quizby is a small Flask app that generates quiz content from prompt templates and source material using an OpenAI-compatible chat API.

## Current Behavior

- `create_app()` loads defaults from the root `config.py` via `config.Config`.
- Environment variables from `.env` still drive the prompt paths, API settings, and output directory defaults defined in `config.py`.
- The default "Show Source Material" action previews `quizby/static/assets/dmbok-sample.txt`.
- Quiz markdown is sanitized in the browser before it is inserted into the DOM.

## Project Layout

```text
quizby/
├── app.py
├── config.py
├── quizby/
│   ├── build.py
│   ├── core.py
│   ├── quizby.py
│   ├── static/
│   └── templates/
├── tests/
└── requirements.txt
```

## Configuration

Set environment variables in `.env` as needed. The most important settings are:

```env
BASE_URL=https://openrouter.ai/api/v1
OR_API_KEY=your_api_key
OR_MODEL=google/gemini-2.5-pro-exp-03-25:free
REFERER=http://localhost
TITLE=Quizby

SYSTEM_PROMPT=prompts/system/default.txt
ASSISTANT_PROMPT=prompts/assistant/default.txt
USER_PROMPT=prompts/user/default.txt
SAMPLE_FILE=assets/cdmp-sample.txt
BOOK_FILE=assets/dmbok.txt
TARGET_DIR=data/output

SECRET_KEY=replace-me
PORT=5000
```

`SECRET_KEY` and the other defaults are exposed through `app.config` after app creation.

## Local Run

Install dependencies:

```bash
python3 -m venv venv
./venv/bin/python -m pip install -r requirements.txt
```

Start the app:

```bash
./venv/bin/python app.py
```

Then open [http://127.0.0.1:5000](http://127.0.0.1:5000).

## Validation

Run the test suite:

```bash
./venv/bin/python -m pytest -q
```

The current suite covers:

- app factory config loading
- `/`
- default source asset serving
- `/generate-quiz` invalid-input handling
- `/generate-quiz` mocked success path
- safe production error responses

## Notes

- Uploads support `.pdf` and `.txt` files up to 10 MB.
- Rate limiting uses in-memory storage, which is suitable for local or single-instance use only.
- The current PDF extraction dependency emits a deprecation warning from `PyPDF2`; functionality still works, but the dependency should eventually move to `pypdf`.
