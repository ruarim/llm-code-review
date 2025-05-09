import subprocess
import click
from llm import get_models
from pathlib import Path
from rich.console import Console
from rich.markdown import Markdown

def get_diff(base: str, staged: bool) -> str:
    cmd = ["git", "diff", "--cached"] if staged else ["git", "diff", base]
    try:
        return subprocess.run(cmd, text=True, capture_output=True, check=True, shell=False).stdout
    except subprocess.CalledProcessError as e:
        raise click.ClickException(f"Failed to get git diff: {e.stderr or e}")


def mark(sym: str, fallback: str, plain: bool) -> str:
    return fallback if plain else sym

def get_llm_models():
    return [model.model_id for model in get_models()]

def view_markdown(path: Path):
    md_text = path.read_text(encoding="utf-8")
    Console().print(Markdown(md_text))
