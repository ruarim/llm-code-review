import subprocess
import click
from llm import get_models
from pathlib import Path
from rich.console import Console
from rich.markdown import Markdown
import logging
import llm
from typing import Callable, Optional, Tuple, TypeVar, ParamSpec

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

T = TypeVar("T")           # return type of the wrapped function
P = ParamSpec("P")         # parameters of the wrapped function

def try_except(func: Callable[P, T], *args: P.args, **kwargs: P.kwargs) -> Tuple[Optional[T], Optional[Exception]]:
    """
    Execute *func* with the supplied *args / kwargs*.

    Returns
    -------
    Tuple[Optional[T], Optional[Exception]]
        (result, error)
            • result – the value returned by *func*, or None if an exception was caught  
            • error  – the caught exception, or None if everything went well
    """
    result: Optional[T] = None
    error: Optional[Exception] = None

    try:
        result = func(*args, **kwargs)
    except (ValueError, TypeError) as e:          # expected errors
        error = e
        logging.error("Error in %s: %s", func.__name__, e)
    except Exception as e:                        # anything else
        error = e
        logging.error("Unexpected error in %s: %s", func.__name__, e)

    return result, error

def chunked_llm_response(response: llm.Response):
    chunks = []
    for chunk in response:
        click.echo(chunk, nl=False)
        chunks.append(chunk) 
    return str("".join(chunks))
