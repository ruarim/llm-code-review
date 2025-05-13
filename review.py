import click 
import llm
import datetime as dt
from pathlib import Path
from typing import Optional, List
from utils import get_diff
from utils import mark
from utils import get_llm_models
from consts import DEFAULT_MODEL
from consts import DEFAULT_MAX_QUESTIONS
from consts import TRANSCRIPT_HEADERS
from consts import Detail
from utils import view_markdown
from utils import try_except
from utils import chunked_llm_response

def review(
    base: str, staged: bool, model: str, plain: bool, md_path: Optional[Path], max_questions: int, detail_level: str, usage: bool, context: str
):                                                                                               
    diff = get_diff(base, staged)
    if not diff.strip():
        click.echo("No changes found – nothing to review.")
        return
    
    model_obj = llm.get_model(model) if model else llm.get_model(DEFAULT_MODEL)
    convo = model_obj.conversation()
    convo.prompt(system='Output markdown')
    transcript: list[str] = [TRANSCRIPT_HEADERS['document']]
    additional_context=  handle_context(context)
    intro = "\n".join([
        "You are a helpful senior software engineer.",
        "Review the following git diff and give actionable feedback, highlighting bugs, code smells, security issues and best‑practice violations.",
        "For each review comment provide;",
        "- An **Issue** with an explanation.",
        "- An **Action** with code suggestions.",
        f"Please use a {detail_level.lower()} level of detail.",
        "Try not to nitpick",
        additional_context,
        "\n",
        f"Diff:\n{diff}",
    ])
        
    review_text = generate_review(intro, convo, plain)
    q_and_a_transcript = generate_q_and_a(convo, max_questions, plain)
    transcript.extend([
        TRANSCRIPT_HEADERS['review'],
        f"{review_text}\n",
        "\n".join(q_and_a_transcript),
        f"{TRANSCRIPT_HEADERS['diff']}\n",
        f"```diff\n{diff}\n```\n"
    ])
    
    if additional_context != "":
        transcript.extend([
            f"{TRANSCRIPT_HEADERS['context']}\n",
            additional_context
        ])

    if md_path is not None:
        file_path = write_to_md(md_path, transcript, plain)
        view_markdown(file_path)
    
    if usage:
        transcript.extend([
            TRANSCRIPT_HEADERS['usage'],
            calc_usage(convo.responses)
        ])        

def handle_context(context: Optional[str]) -> str:
    if not context:
        return ""
    p = Path(context)
    if p.is_file() and p.suffix in {'.md', '.txt'}:
        res, err = try_except(p.read_text, None)
        if err or res is None or res.strip() == "":
            click.echo(f"Warning: could not read context file {p}: {err}", err=True)
            return ""
        context = res
    return context
        
def generate_review(intro: str, convo: llm.Conversation, plain: bool) -> str:
    click.echo(f"{mark('🧠','[RUN]', plain)}  Running AI review …")
    res, err = try_except(convo.prompt, intro)
    if err:
        raise err
    if res:
        return chunked_llm_response(res)
    else:
        return 'No review generated'

def calc_usage(responses: List[llm.models._BaseResponse]):
    usage = [res.token_usage() for res in responses]
    details = [res.token_details for res in responses]
    # TODO: calc cost for tokens
    click.echo(details)
    click.echo('\nTOKEN USAGE\n')
    click.echo(usage)
    return "\n".join((usage))
    
def generate_q_and_a(convo: llm.Conversation, max_questions: int, plain=False):
    q_and_a_transcript = []
    max_questions = 1 if max_questions < 0 else max_questions
    
    for i in range(max_questions):
        question = click.prompt(
            f"\n{mark('❓','?', plain)}  Follow‑up (Enter to quit)", 
            default="", 
            show_default=False
        ).strip()
        if not question: break
        
        answer = chunked_llm_response(convo.prompt(question))
        click.echo("\n--- Response ---\n")
        click.echo(answer)

        q_and_a_transcript.extend([
            f"### Q: {question}\n", answer + "\n"
        ])
        
        if(i == max_questions - 1):
            click.echo(f'Exiting: Hit max number of questions: {max_questions}')
            
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
    
    _, err = try_except(
        file_path.write_text, 
        "\n".join(transcript), 
        encoding="utf-8"
    )
    if err: 
        raise err
    
    click.echo(f"{mark('💾', '[SAVED]', plain)}  Saved transcript to {file_path}")
    
    return file_path

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
@click.option(
    "-c", "--context", 
    default='',
    help="Additional text context for the model. Provide text in cli or point to a file (.txt or .md)."
)
def cli(
    base: str, staged: bool, model: str, plain: bool, md_path: Optional[Path], max_questions: int, list_models: bool, detail_level: str, usage: bool, context: str
):
    available_models = get_llm_models()
    if list_models:
        model_names = "\n".join(available_models)
        return click.echo(f'Models:\n{model_names}')
        
    if model and model not in available_models:                                                                                                                                                                      
        raise click.BadParameter(
            f"Invalid model name: {model}. Available models are: {', '.join(available_models)}"
        ) 
        
    review(
        base, staged, model, plain, md_path, max_questions, detail_level, usage, context
    )

if __name__ == "__main__":
    cli()
