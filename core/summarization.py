import re
from models.gemini import GeminiModel
from utils.api_utils import with_retry_and_key_rotation
from prompts.summarization import summarization_prompt

@with_retry_and_key_rotation
def generate_summary(content, model):
    """Generates a summary using the provided model."""
    response = model.generate_content(f"{summarization_prompt}\n\nText to summarize:\n{content}")
    return response.text

def extract_summary_content(summary_text):
    """Extracts the text content within <sum> tags using regex."""
    match = re.search(r"<sum>(.*?)</sum>", summary_text, re.DOTALL)
    if match:
        return match.group(1).strip()
    else:
        return ""
