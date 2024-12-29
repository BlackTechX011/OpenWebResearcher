import requests
from bs4 import BeautifulSoup

def perform_web_search(query):
    """Performs a real-world web search and returns the top 5 URLs."""
    base_url = "https://www.google.com/search?q="
    search_url = base_url + query.replace(" ", "+")

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    }

    try:
        response = requests.get(search_url, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, "html.parser")

        search_results = []
        for result in soup.find_all("div", class_="yuRUbf"):
            link = result.find("a")["href"]
            search_results.append(link)

        top_5_urls = search_results[:5]
        return top_5_urls

    except requests.exceptions.RequestException as e:
        print(f"Error during web search: {e}")
        return []
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return []
