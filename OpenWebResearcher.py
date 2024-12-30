import os
import time
from config.settings import API_KEYS, DELAY_SECONDS, FINAL_REPORT_MODEL, FINAL_REPORT_MODEL_API_KEY
from core.search import perform_web_search
from core.extraction import extract_content
from core.summarization import generate_summary, extract_summary_content
from models.gemini import GeminiModel
from prompts.query_refinement import query_refinement_prompt
from prompts.response_generation import response_generation_prompt
from utils.file_utils import save_report_to_markdown
import re
from rich import print
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import track, Progress, SpinnerColumn, TimeElapsedColumn, BarColumn, TextColumn
from rich.live import Live
from rich.layout import Layout
from rich.text import Text
from rich.markdown import Markdown
from rich.tree import Tree
from rich.rule import Rule
from rich.spinner import Spinner
from rich.style import Style
from rich.columns import Columns

console = Console()

def clear_screen():
    """Clears the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def display_banner():
    """Displays a visually appealing banner."""
    console.print(
        Panel(
            Text.from_markup(
                """
[bold blue]
 ██████╗ ██████╗ ███████╗███╗   ██╗    ██╗    ██╗███████╗██████╗     ██████╗ ███████╗███████╗███████╗ █████╗ ██████╗  ██████╗██╗  ██╗███████╗██████╗ 
██╔═══██╗██╔══██╗██╔════╝████╗  ██║    ██║    ██║██╔════╝██╔══██╗    ██╔══██╗██╔════╝██╔════╝██╔════╝██╔══██╗██╔══██╗██╔════╝██║  ██║██╔════╝██╔══██╗
██║   ██║██████╔╝█████╗  ██╔██╗ ██║    ██║ █╗ ██║█████╗  ██████╔╝    ██████╔╝█████╗  ███████╗█████╗  ███████║██████╔╝██║     ███████║█████╗  ██████╔╝
██║   ██║██╔═══╝ ██╔══╝  ██║╚██╗██║    ██║███╗██║██╔══╝  ██╔══██╗    ██╔══██╗██╔══╝  ╚════██║██╔══╝  ██╔══██║██╔══██╗██║     ██╔══██║██╔══╝  ██╔══██╗
╚██████╔╝██║     ███████╗██║ ╚████║    ╚███╔███╔╝███████╗██████╔╝    ██║  ██║███████╗███████║███████╗██║  ██║██║  ██║╚██████╗██║  ██║███████╗██║  ██║
 ╚═════╝ ╚═╝     ╚══════╝╚═╝  ╚═══╝     ╚══╝╚══╝ ╚══════╝╚═════╝     ╚═╝  ╚═╝╚══════╝╚══════╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝

<Developer> BlackTechX </developer>
<GitHub> https://github.com/BlackTechX011/OpenWebResearcher </GitHub>
[/bold blue]
""",
                justify="center"
            ),
            title="[bold blue]Open Web Researcher[/bold blue]",
            subtitle="[italic blue]v1.0[/italic blue]",
            style="blue",
            padding=(1, 2),
            expand=False,
            border_style="bold blue"
        )
    )

def display_queries(queries):
    """Displays generated search queries in an animated tree view."""
    tree = Tree("🔍 [bold blue]Generated Search Queries[/bold blue]", guide_style="bold blue")
    with Live(tree, refresh_per_second=4):
        for i, query in enumerate(queries):
            time.sleep(0.2)
            branch = tree.add(f"[bold #FFA500]Query {i + 1}[/bold #FFA500]")  # Orange color for query number
            branch.add(Text(query, style="cyan"))

   # print(tree)
    print(Rule(style="bold blue"))
    print("\n")

def display_urls(query, urls):
    """Displays top URLs with a loading animation."""
    print("\n\n")
    table = Table(title=f"🔗 [bold blue]Top URLs for '[italic #FFA500]{query}[/italic #FFA500]'[/bold blue]", style="cyan", show_header=True, header_style="bold magenta")
    table.add_column("#", style="dim", width=3, justify="right")
    table.add_column("URL", min_width=60)

    with Live(table, refresh_per_second=4):
        for i, url in enumerate(urls):
            table.add_row(str(i + 1), Text(url, style="link " + url))
            time.sleep(0.1)
    print(Rule(style="bold blue"))
    print("\n")

def display_summary(url, summary):
    """Displays the summary for a given URL with a styled panel."""
    markdown_summary = Markdown(summary)
    print("\n\n")
    # Create a styled summary panel
    summary_panel = Panel(
        markdown_summary,
        title=Text.from_markup(f"📝 [bold blue]Summary from[/bold blue]: {url}"),  # URL as plain text in title
        style=Style(color="#66BB6A"),  # Green color for summaries
        expand=False,
        border_style="green"
    )
    print("\n")

    # Create a clickable link Text object
    url_link = Text(f"View Source: {url}", style=f"link {url}")

    # Create columns for layout
    columns = Columns([summary_panel, url_link], expand=True)

    # Display with Live for a smooth update
    with Live(columns, refresh_per_second=4):
        time.sleep(1)  # Simulate some processing time
    print(Rule(style="bold blue"))
    print("\n")

def generate_search_queries(user_query, model):
    """Generates related search queries with a progress indicator and extracts them from <sum> tag."""
    with Progress(
        SpinnerColumn(style="#66BB6A"),  # Green spinner
        *Progress.get_default_columns(),
        TimeElapsedColumn(),
        transient=True
    ) as progress:
        progress.add_task("[blue]Generating search queries...", total=None)
        response = model.generate_content(f"{query_refinement_prompt}\n\nUser Query: {user_query}")

        # Extract content within the <sum> tag using regular expressions
        match = re.search(r"<sum>(.*?)</sum>", response.text, re.DOTALL)
        if match:
            queries_text = match.group(1).strip()
            queries = queries_text.split('\n')
        else:
            queries = []  # Return empty list if <sum> tag is not found
    
    return queries

def generate_final_answer(summaries, user_query, model):
    """Generates the final answer with a progress bar."""
    extracted_summaries = [extract_summary_content(summary) for summary in summaries]
    summaries_text = "\n\n".join(extracted_summaries)

    with Progress(
        "[progress.description]{task.description}",
        BarColumn(bar_width=40, style="#66BB6A", complete_style="#66BB6A"),  # Green bar
        "[progress.percentage]{task.percentage:>3.0f}%",
        TimeElapsedColumn(),
        transient=True
    ) as progress:
        task = progress.add_task("[blue]Generating final report...", total=100)
        response = model.generate_content(
            f"{response_generation_prompt}\n\nUser Query: {user_query}\n\nSummaries:\n{summaries_text}"
        )
        for _ in range(100):
            time.sleep(0.02)
            progress.update(task, advance=1)
    return response.text

def main():
    """Main function to run the research agent."""
    clear_screen()
    display_banner()
   

    user_query = console.input("[ + ] [bold #FFA500]Enter your research question: [/bold #FFA500]")  # Orange color for input prompt

    if FINAL_REPORT_MODEL and FINAL_REPORT_MODEL_API_KEY:
        query_refinement_model = GeminiModel(FINAL_REPORT_MODEL_API_KEY, model_name=FINAL_REPORT_MODEL)
    else:
        query_refinement_model = GeminiModel(API_KEYS[0])
    summarization_model = GeminiModel(API_KEYS[0])

    # Use a different model for the final report if configured
    if FINAL_REPORT_MODEL and FINAL_REPORT_MODEL_API_KEY:
        response_generation_model = GeminiModel(FINAL_REPORT_MODEL_API_KEY, model_name=FINAL_REPORT_MODEL)
    else:
        response_generation_model = summarization_model

    # 1. Query Refinement
    search_queries = generate_search_queries(user_query, query_refinement_model)
    display_queries(search_queries)

    all_summaries = []
    used_urls = []

    for query in search_queries:
        # 2. Web Search
        urls = perform_web_search(query)
        display_urls(query, urls)

        # 3. Content Extraction & 4. Summarization
        for url in urls:
            content = extract_content(url)
            summary = generate_summary(content, summarization_model)
            all_summaries.append(summary)
            used_urls.append(url)
            display_summary(url, summary)
            time.sleep(DELAY_SECONDS)

    # 5. Response Generation
    final_report = generate_final_answer(all_summaries, user_query, response_generation_model)
    console.print(Panel(Markdown(final_report), title="[bold blue]Final Report[/bold blue]", style="purple", expand=False))

    # 6. Save to Markdown
    Savetofile = save_report_to_markdown(final_report, user_query, used_urls)
    console.print(Panel(Text(f"Report saved to {Savetofile}!", style="bold green"), expand=False))

if __name__ == "__main__":
    main()
