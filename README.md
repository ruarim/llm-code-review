# AI Git Code Reviewer

A lightweight CLI that uses your configured large‑language model to review Git diffs and suggest concrete fixes.

## Requirements

* Python 3.10
* [uv](https://github.com/astral-sh/uv) — blazing‑fast drop‑in replacement for pip & virtualenv
* [llm](https://github.com/simonw/llm) with at least one model configured

## Installation

```bash
# 1️⃣ Create & activate a virtual env (recommended)
uv venv                 # creates .venv with CPython in the cwd
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# 2️⃣ Install the dependencies
uv pip install -r requirements.txt
```

Need deterministic installs? Use the lock‑aware variant:

```bash
uv pip sync requirements.txt
```

## Quick start

Review the most recent commit:

```bash
python review.py                 # ⬅️ reviews HEAD~1 → HEAD
```

Review staged (uncommitted) changes:

```bash
python review.py --staged
```

Save the review (plus Q\&A) as Markdown:

```bash
python review.py --markdown .    # writes ./code-review-<timestamp>.md
```

Change the model or detail level:

```bash
python review.py --model gpt-4o-mini --detail high
```

List available models:

```bash
python review.py --list-models
```

For every flag and its default value run:

```bash
python review.py --help
```

## Build CLI 
```bash
pip install llm-plugin-<provider> # openai models are installed by default.
```

```bash
uv run -- python -m PyInstaller llm-reviewer.spec
```

## Test CLI
```bash
./dist/llm-reviewer --list-models 
```

## Typical flags

| Flag                      | Purpose                                       | Default      |
| ------------------------- | --------------------------------------------- | ------------ |
| `-b, --base`              | Choose the base commit for the diff           | `HEAD~1`     |
| `-s, --staged`            | Review only staged changes                    | *false*      |
| `-m, --model`             | Model ID to use (see `--list-models`)         | repo default |
| `-d, --detail`            | `low`, `medium`, `high` verbosity             | `medium`     |
| `-md, --markdown`         | Write review to a file/dir                    | *off*        |
| `-max-q, --max-questions` | Max follow‑up Q\&A turns                      | `10`         |
| `-u, --usage`             | Show token usage per response                 | *false*      |
| `-c, --context`           | Provide additional text or path (.md or .txt) | ""           |

## License

MIT
