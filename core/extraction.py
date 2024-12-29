from trafilatura import fetch_url, extract

def extract_content(url):
    """Extracts the main text content from a webpage."""
    try:
        downloaded = fetch_url(url)
        if downloaded:
            result = extract(downloaded, favor_recall=True)
            return result if result else ""
        else:
            return ""
    except Exception as e:
        print(f"Error extracting content from {url}: {e}")
        return ""
