import click 
import llm
import datetime as dt
from pathlib import Path
from typing import Optional
from utils import get_diff
from utils import mark
from utils import get_llm_models
from consts import DEFAULT_MODEL
from consts import DEFAULT_MAX_QUESTIONS
from consts import Detail
from utils import view_markdown

@click.command()
@click.option(
    "-b", "--base", 
    default="HEAD~1",
    help="Base commit for diff (default HEAD~1)"
)
@click.option(
    "-s", "--staged", 
    is_flag=True,
    help="Use staged changes instead of commit diff"
)
@click.option(
    "-m", "--model", 
    default=None,
    help="Model ID, e.g. gpt-4o-mini, mistral:7b, llama2:latest"
)
@click.option(
    "-p", "--plain", 
    is_flag=True,
    help="Disable emoji / Unicode output"
)
@click.option(
    "-md", "--markdown", "md_path",
    nargs=1, required=False, default=None,
    type=click.Path(path_type=Path, writable=True, dir_okay=True),
    help="Save review (+ Q&A) to Markdown. "
         "Supply a filename, a directory, or the value . to "
         "write to ./code-review-<timestamp>.md"
)
@click.option(
    "-max-q", "--max-questions", default=DEFAULT_MAX_QUESTIONS,
    help="Maximum number of follow up questions (default 10)"
)
@click.option(
    "-l", "--list-models", is_flag=True,
    help="Lists the valid model names"
)
@click.option(
    "-d", "--detail",
    "detail_level",          
    type=click.Choice([d.value for d in Detail], case_sensitive=False),
    default=Detail.medium.value,
    show_default=True,
    help="Level of detail for the review (low / medium / high).",
)
@click.option(
    "-u", "--usage", 
    is_flag=True,
    help="Show model token usage"
)
def review(
    base: str, staged: bool, model: str, plain: bool, md_path: Optional[Path], max_questions: int, list_models: bool, detail_level: str, usage: bool
):
    if list_models:
        model_names = "\n".join(get_llm_models())
        return click.echo(f'Models:\n{model_names}')
        
    if model and model not in get_llm_models():                                                                                                                                                                      
        raise click.BadParameter(f"Invalid model name: {model}. Available models are: {', '.join(get_llm_models())}")                                                                                                
                                                                                                                                                                                                                      
    if md_path and not md_path.exists():                                                                                                                                                                             
        raise click.BadParameter(f"The specified markdown path {md_path} does not exist.")
    
    diff = get_diff(base, staged)
    if not diff.strip():
        click.echo("No changes found – nothing to review.")
        return

    model_obj = llm.get_model(model) if model else llm.get_model(DEFAULT_MODEL)
    convo = model_obj.conversation()

    transcript: list[str] = [
        "# AI Code Review\n",
    ]

    intro = "\n".join([
        "You are a helpful senior software engineer.",
        "Review the following git diff and give actionable feedback, highlighting bugs, code smells, security issues and best‑practice violations.",
        "For each comment provide and Action (with code suggestions)",
        "- An **Issue** with an explanation.",
        "- An **Action** with code suggestions.",
        f"Please use a {detail_level.lower()} level of detail."
        "\n",
        f"Diff:\n{diff}"
    ])

    click.echo(f"{mark('🧠','[RUN]', plain)}  Running AI review …")
    # it would make sense to stream this response
    first_reply = convo.prompt(intro).text()
    click.echo("\n--- AI Code Review ---\n")
    click.echo(first_reply)

    transcript += ["## Review\n", first_reply + "\n"]
    transcript += q_and_a(convo, max_questions, plain)
    transcript += [ "## Diff reviewed\n"]
    transcript += ["```diff\n" + diff + "\n```\n"]

    if md_path is not None:
        file_path = write_to_md(md_path, transcript, plain)
        view_markdown(file_path)
    
    if usage:
        click.echo('\nTOKEN USAGE\n')
        click.echo([res.token_usage() for res in convo.responses])

def q_and_a(convo: llm.Conversation, max_questions: int, plain=False):
    q_and_a_transcript = []
    max_questions = 1 if max_questions < 0 else max_questions
    
    for i in range(max_questions):
        question = input(f"\n{mark('❓','?', plain)}  Follow‑up (Enter to quit): ").strip()
        if not question:
            break
        
        answer = convo.prompt(question).text()
        click.echo("\n--- Response ---\n")
        click.echo(answer)

        q_and_a_transcript += [f"### Q: {question}\n", answer + "\n"]
        
        if(i == max_questions - 1):
            click.echo(f'Exiting: Hit max number of questions: {i}')
            
    return q_and_a_transcript

def write_to_md(md_path: Path, transcript: list[str], plain: bool):
    md_path = Path(md_path)
    ts_name = f"code-review-{dt.datetime.now():%Y%m%d-%H%M%S}.md".replace(':', '-')

    is_directory_target = (md_path.suffix == "")
    
    if is_directory_target:
        md_path.mkdir(parents=True, exist_ok=True)
        file_path = md_path / ts_name
    else:
        md_path.parent.mkdir(parents=True, exist_ok=True)
        file_path = md_path
    
    try:
        file_path.write_text("\n".join(transcript), encoding="utf-8")
    except (OSError, IOError) as e:
        click.echo(f"Error writing to the file: {e}")
        raise
    
    click.echo(f"{mark('💾', '[SAVED]', plain)}  Saved transcript to {file_path}")
    
    return file_path

if __name__ == "__main__":
    review()
