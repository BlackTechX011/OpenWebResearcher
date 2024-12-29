from datetime import datetime

def save_report_to_markdown(report_content, user_query, used_urls):
    """Saves the report content to a Markdown file."""
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    filename = f"Reports/OpenWebResearcher_report_{timestamp}.md"

    with open(filename, "w", encoding="utf-8") as f:
        f.write(report_content)
        f.write("\n\n## References\n\n")
        for i, url in enumerate(used_urls):
            f.write(f"{i+1}. {url}\n")

    return filename
