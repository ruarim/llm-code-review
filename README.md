# AI Git Code Reviewer

A lightweight CLI that uses large‑language models to review Git diffs and suggest concrete fixes.

## Requirements

* Python 3.10
* [uv](https://github.com/astral-sh/uv) — blazing‑fast drop‑in replacement for pip & virtualenv
* [llm](https://github.com/simonw/llm) with at least one model configured

## Installation
```bash
uv sync 
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
python review.py --model o4-mini --detail high
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
uv run -- python -m PyInstaller llm-reviewer.spec
```
To include other models use [llm plugins](https://llm.datasette.io/en/stable/plugins/installing-plugins.html)

## Test CLI
```bash
./dist/llm-reviewer --list-models 
```

## Move to your path (Mac)
```bash
sudo mv ./dist/llm-reviewer /usr/local/bin/llm-reviewer
```

## Typical flags

| Flag                      | Purpose                                       | Default      |
| ------------------------- | --------------------------------------------- | ------------ |
| `-b, --base`              | Choose the base commit for the diff           | `HEAD~1`     |
| `-s, --staged`            | Review only staged changes                    | *false*      |
| `-m, --model`             | Model ID to use (see `--list-models`)         | `gpt-4o-mini`  |
| `-d, --detail`            | `low`, `medium`, `high` verbosity             | `medium`     |
| `-md, --markdown`         | Write review to a file/dir                    | *off*        |
| `-max-q, --max-questions` | Max follow‑up Q\&A turns                      | `10`         |
| `-u, --usage`             | Show token usage per response                 | *false*      |
| `-c, --context`           | Provide additional text or file (.md or .txt) | ""           |

## License

MIT
